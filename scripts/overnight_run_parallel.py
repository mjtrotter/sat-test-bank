import asyncio
import os
import time
from pathlib import Path

PROJECT_ROOT = "/Users/mjtrotter/Desktop/Dev/Vanguard"
LOG_FILE = os.path.join(PROJECT_ROOT, "overnight_parallel_robust.log")

# Parallel Tasks: One process per Band to maximize GPU utilization
TASKS = [
    {
        "name": "Band 0 (SmolLM2)",
        "bands": "0",
        "source": "mathcounts,gsm8k,sat,math_competition,orca_math",
        "resume": 5
    },
    {
        "name": "Band 1 (Qwen2.5-Math)",
        "bands": "1",
        "source": "mathcounts,gsm8k,sat,math_competition,orca_math",
        "resume": 7
    }
]

def log(message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}\n"
    print(formatted.strip())
    with open(LOG_FILE, "a") as f:
        f.write(formatted)

async def run_task_loop(task):
    log(f"Starting Task Loop: {task['name']}")
    current_run_id = task.get("resume")
    
    while True:
        command = [
            "python3", "-m", "src.cli", "calibrate-difficulty", 
            "--bands", task["bands"],
            "--source", task["source"],
            "--max-problems", "50"
        ]
        if current_run_id:
            command.extend(["--resume", str(current_run_id)])
            
        try:
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
                
                if "total results stored" in decoded:
                    try:
                        count = int(decoded.split(" — ")[1].split(" ")[0])
                        batch_stored = count
                    except: pass
                
                if "Created calibration run" in decoded:
                    current_run_id = decoded.split(" ")[-1]
                    log(f"  [{task['name']}] New Run ID: {current_run_id}")

            await process.wait()
            
            if batch_stored == 0:
                all_output = "\n".join(output_lines)
                if "complete — 0 total results stored" in all_output:
                    log(f"FINISHED: {task['name']}")
                    break
            else:
                log(f"  [{task['name']}] Stored {batch_stored} results.")
                
            await asyncio.sleep(1) # Gap between process restarts
            
        except Exception as e:
            log(f"  !!! [{task['name']}] Error: {str(e)}")
            await asyncio.sleep(10)

async def main():
    with open(LOG_FILE, "w") as f:
        f.write(f"PARALLEL LOG STARTED {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    log("="*60)
    log("VANGUARD PARALLEL ROBUST RUN START")
    log("="*60)
    
    # Run tasks in parallel
    await asyncio.gather(*[run_task_loop(t) for t in TASKS])
    
    log("="*60)
    log("VANGUARD PARALLEL ROBUST RUN FINISHED")
    log("="*60)

if __name__ == "__main__":
    asyncio.run(main())
