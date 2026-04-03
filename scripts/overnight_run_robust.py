import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path

# Project root
PROJECT_ROOT = "/Users/mjtrotter/Desktop/Dev/Vanguard"
LOG_FILE = os.path.join(PROJECT_ROOT, "overnight_calibration_robust_v2.log")

# Unified Task: All Base Level Sources for Bands 0-1
# Processed in batches of 50 with full process restarts.
# Skips already completed (model, problem) pairs automatically.
TASK = {
    "name": "Base Calibration (Bands 0-1)",
    "bands": "0,1",
    "source": "mathcounts,gsm8k,sat,math_competition,orca_math",
    "resume": 5 # Start by trying to resume Run 5, will create new ones if needed
}

def log(message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}\n"
    print(formatted.strip())
    with open(LOG_FILE, "a") as f:
        f.write(formatted)

async def main():
    log("="*60)
    log("VANGUARD ROBUST OVERNIGHT V2 START")
    log("="*60)
    
    current_run_id = TASK["resume"]
    
    while True:
        command = [
            "python3", "-m", "src.cli", "calibrate-difficulty", 
            "--bands", TASK["bands"],
            "--source", TASK["source"],
            "--max-problems", "50"
        ]
        if current_run_id:
            command.extend(["--resume", str(current_run_id)])
            
        log(f"Running batch (Run {current_run_id or 'NEW'})...")
        
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
                if not line:
                    break
                decoded = line.decode().strip()
                output_lines.append(decoded)
                
                # Check for "Stored X results to DB"
                if "Stored" in decoded and "results to DB" in decoded:
                    try:
                        count = int(decoded.split("Stored ")[1].split(" ")[0])
                        batch_stored += count
                    except:
                        pass
                
                # Capture and log new Run ID if created
                if "Created calibration run" in decoded:
                    current_run_id = decoded.split(" ")[-1]
                    log(f"  New Run ID created: {current_run_id}")
                
                if "completed" in decoded or "Stored" in decoded:
                    print(f"    {decoded}") # Print to stdout for visibility, log only summary

            return_code = await process.wait()
            
            if return_code != 0:
                log(f"  !!! Subprocess failed with code {return_code}. Waiting 10s and retrying...")
                await asyncio.sleep(10)
                continue
            
            if batch_stored == 0:
                # If we stored 0 but the output says "No problems to process" for ALL models, we are done.
                # Since we are running multiple models, we need to be careful.
                # If total stored in the summary is 0, we are truly done.
                all_output = "\n".join(output_lines)
                if "complete — 0 total results stored" in all_output:
                    log("FINISHED: No more problems left for any model in these bands.")
                    break
                else:
                    log("  Batch did no work but not finished? Retrying once.")
                    await asyncio.sleep(5)
            else:
                log(f"  Batch complete: {batch_stored} results stored.")
                
            await asyncio.sleep(1)
            
        except Exception as e:
            log(f"  !!! Fatal error in robust loop: {str(e)}")
            await asyncio.sleep(30)

    log("="*60)
    log("VANGUARD ROBUST OVERNIGHT V2 FINISHED")
    log("="*60)

if __name__ == "__main__":
    asyncio.run(main())
