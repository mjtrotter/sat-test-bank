import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path

# Project root
PROJECT_ROOT = "/Users/mjtrotter/Desktop/Dev/Vanguard"
LOG_FILE = os.path.join(PROJECT_ROOT, "overnight_calibration_base_full.log")

# Task definitions: Full Base Level Sets (GSM8K, orca_math, easy SAT, basic MC)
# Focusing on the most capable mini models: SmolLM2-1.7B and Qwen2.5-Math-1.5B
TASKS = [
    # 1. Finish Run 5 (SmolLM2 on MATHCOUNTS)
    {
        "name": "SmolLM2: Finish MATHCOUNTS (Run 5)",
        "command": ["python3", "-m", "src.cli", "calibrate-difficulty", "--resume", "5", "--bands", "0", "--source", "mathcounts"]
    },
    # 2. SmolLM2 on all other Base Sources (GSM8K, SAT, basic MC, orca_math)
    {
        "name": "SmolLM2: All Other Base Sources (Full)",
        "command": ["python3", "-m", "src.cli", "calibrate-difficulty", "--bands", "0", "--source", "gsm8k,sat,math_competition,orca_math"]
    },
    # 3. Qwen2.5-Math-1.5B on all Base Sources
    {
        "name": "Qwen2.5-Math-1.5B: All Base Sources (Full)",
        "command": ["python3", "-m", "src.cli", "calibrate-difficulty", "--bands", "1", "--source", "mathcounts,gsm8k,sat,math_competition,orca_math"]
    }
]

def log(message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}\n"
    print(formatted.strip())
    with open(LOG_FILE, "a") as f:
        f.write(formatted)

async def main():
    log("="*60)
    log("VANGUARD OVERNIGHT BASE-LEVEL FULL-RUN START")
    log("="*60)
    log(f"Process PID: {os.getpid()}")
    
    for i, task in enumerate(TASKS):
        log(f"Starting Task {i+1}/{len(TASKS)}: {task['name']}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *task["command"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=PROJECT_ROOT
            )
            
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                decoded = line.decode().strip()
                if "completed" in decoded or "Stored" in decoded or "Band" in decoded:
                    log(f"  {decoded}")
                elif "ERROR" in decoded or "Exception" in decoded:
                    log(f"  !!! ERROR: {decoded}")

            return_code = await process.wait()
            
            if return_code == 0:
                log(f"Task {i+1} completed successfully.")
            else:
                log(f"Task {i+1} failed with exit code {return_code}.")
                await asyncio.sleep(10)
        
        except Exception as e:
            log(f"Fatal error in Task {i+1}: {str(e)}")
            await asyncio.sleep(60)

    log("="*60)
    log("VANGUARD OVERNIGHT BASE-LEVEL FULL-RUN FINISHED")
    log("="*60)

if __name__ == "__main__":
    asyncio.run(main())
