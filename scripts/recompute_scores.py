import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from src.core.database import async_session
from src.models.tables import CalibrationResponse, Problem
from src.calibration.scorer import extract_answer, score

async def recompute_scores(run_id: int):
    print(f"Recomputing scores for Run {run_id}...")
    
    async with async_session() as session:
        # 1. Fetch all responses for the run along with problem answers
        query = select(
            CalibrationResponse.id,
            CalibrationResponse.response_text,
            Problem.answer
        ).join(Problem, CalibrationResponse.problem_id == Problem.id).where(
            CalibrationResponse.run_id == run_id
        )
        
        result = await session.execute(query)
        rows = result.all()
        print(f"  Found {len(rows)} responses to re-score")
        
        count = 0
        updated_count = 0
        
        # Process in batches for DB efficiency
        BATCH_SIZE = 500
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i+BATCH_SIZE]
            
            for row in batch:
                new_extracted = extract_answer(row.response_text)
                if new_extracted:
                    new_extracted = new_extracted[:490]
                new_correct = score(new_extracted, row.answer)
                
                # Update the row
                stmt = update(CalibrationResponse).where(
                    CalibrationResponse.id == row.id
                ).values(
                    extracted_answer=new_extracted,
                    is_correct=new_correct
                )
                await session.execute(stmt)
                updated_count += 1
            
            await session.commit()
            count += len(batch)
            print(f"  [{count}/{len(rows)}] re-scored...")

    print(f"\nFinished! Re-scored {updated_count} responses.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/recompute_scores.py <run_id>")
        sys.exit(1)
        
    run_id = int(sys.argv[1])
    asyncio.run(recompute_scores(run_id))
