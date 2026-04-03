import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = "/Users/mjtrotter/Desktop/Dev/Vanguard"
LOG_FILE = os.path.join(PROJECT_ROOT, "overnight_sequential_robust.log")

# Sequential Tasks: STRICTLY ONE AT A TIME to prevent Metal OOM and macOS panics.
TASKS = [
    {
        "name": "Band 0 (SmolLM2 + Qwen2.5-0.5B) on Base Sources",
        "bands": "0",
        "source": "mathcounts,gsm8k,sat,math_competition,orca_math",
        "resume": 5
    },
    {
        "name": "Band 1 (Qwen2.5-Math-1.5B + 3B) on Base Sources",
        "bands": "1",
        "source": "mathcounts,gsm8k,sat,math_competition,orca_math",
        "resume": None  # Will create a new run
    }
]

def log(message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}\n"
    print(formatted.strip())
    with open(LOG_FILE, "a") as f:
        f.write(formatted)

async def run_task_sequentially(task):
    log(f"Starting Sequential Task: {task['name']}")
    current_run_id = task.get("resume")
    
    consecutive_no_work = 0
    cycle_start_time = time.time()
    
    while True:
        # Check thermal duty cycle (20 mins active -> 3 mins cool down)
        if time.time() - cycle_start_time > (20 * 60):
            log(f"  [THERMAL CYCLE] 20 minutes of active load reached. Cooling down for 3 minutes...")
            await asyncio.sleep(3 * 60)
            log(f"  [THERMAL CYCLE] Cooldown complete. Resuming...")
            cycle_start_time = time.time()
            
        command = [
            "python3", "-m", "src.cli", "calibrate-difficulty", 
            "--bands", task["bands"],
            "--source", task["source"],
            "--max-problems", "50"
        ]
        if current_run_id:
            command.extend(["--resume", str(current_run_id)])
            
        try:
            log(f"  Launching process for batch (Run {current_run_id or 'NEW'})...")
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=PROJECT_ROOT
            )
            
            output_lines = []
            batch_stored = 0
            
            while True:
                line = await process.stdout.readline()
                if not line: break
                decoded = line.decode().strip()
                output_lines.append(decoded)
                
                # Check for progress lines
                if "total results stored" in decoded:
                    try:
                        count = int(decoded.split(" — ")[1].split(" ")[0])
                        batch_stored = count
                    except: pass
                
                # Extract new run ID
                if "Created calibration run" in decoded:
                    current_run_id = decoded.split(" ")[-1]
                    log(f"    New Run ID created: {current_run_id}")
                    
            return_code = await process.wait()
            
            if return_code != 0:
                log(f"    !!! Subprocess failed with code {return_code}. Cooling down for 15s...")
                await asyncio.sleep(15)
                continue
                
            # Check completion criteria
            if batch_stored == 0:
                all_output = "\n".join(output_lines)
                if "complete — 0 total results stored" in all_output:
                    log(f"  FINISHED: {task['name']}")
                    break
                else:
                    consecutive_no_work += 1
                    if consecutive_no_work >= 2:
                        log(f"  FINISHED: {task['name']} (Repeated 0 results with no explicit complete message)")
                        break
                    log("    Batch stored 0 but no 'complete' message. Retrying...")
                    await asyncio.sleep(5)
            else:
                consecutive_no_work = 0
                log(f"    Batch complete: {batch_stored} results stored.")
                
            # Crucial: Wait between batches to ensure Metal memory is fully reclaimed by macOS
            await asyncio.sleep(2)
            
        except Exception as e:
            log(f"    !!! Fatal error in sequential loop: {str(e)}")
            await asyncio.sleep(10)

async def main():
    with open(LOG_FILE, "w") as f:
        f.write(f"SEQUENTIAL LOG STARTED {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    log("="*60)
    log("VANGUARD SEQUENTIAL ROBUST RUN START")
    log("="*60)
    
    # Run tasks strictly one by one
    for task in TASKS:
        await run_task_sequentially(task)
    
    log("="*60)
    log("VANGUARD SEQUENTIAL ROBUST RUN FINISHED")
    log("="*60)

if __name__ == "__main__":
    asyncio.run(main())
