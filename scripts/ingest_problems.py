"""
Ingest problem database into Vanguard PostgreSQL.

Sources:
  1. Perplexity unified v3 JSONL (970K records, sharded db_00..db_09)
  2. Gemini MATHCOUNTS extractions (1990-2013, 3,456 records)

Usage:
  python scripts/ingest_problems.py                    # full import
  python scripts/ingest_problems.py --dry-run          # count without inserting
  python scripts/ingest_problems.py --source gemini    # only Gemini MATHCOUNTS
  python scripts/ingest_problems.py --source perplexity # only Perplexity DB
"""
import argparse
import ast
import json
import os
import sys
import time
import uuid
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

# ── Config ────────────────────────────────────────────────────────────────────

DB_URL = os.getenv("DATABASE_URL", "postgresql://vanguard:vanguard@localhost:5433/vanguard")

PERPLEXITY_DIR = Path.home() / "Downloads" / "problem-database" / "01-Database"
PERPLEXITY_SHARDS = [
    "db_00.jsonl", "db_01.jsonl", "db_02.jsonl", "db_03(2).jsonl",
    "db_04.jsonl", "db_05.jsonl", "db_06.jsonl", "db_07.jsonl",
    "db_08.jsonl", "db_09.jsonl",
]

GEMINI_DIR = Path.home() / "Desktop" / "Dev" / "Vanguard" / "data" / "extracted"

BATCH_SIZE = 5000

# ── Field mapping: v3 compact → Vanguard Problem ─────────────────────────────

def _clean(s: str | None) -> str | None:
    """Strip NUL bytes that break PostgreSQL text columns."""
    if s is None:
        return None
    return s.replace("\x00", "")


def _normalize_subject(subj: str) -> str:
    """Normalize subject field — some v3 records have stringified Python lists."""
    if not subj or not subj.startswith("["):
        return subj
    try:
        parsed = ast.literal_eval(subj)
        if parsed and isinstance(parsed, list):
            return parsed[0].split(" -> ")[-1].lower()
    except (ValueError, SyntaxError):
        pass
    return subj


def map_v3_to_problem(r: dict) -> dict:
    """Map a Perplexity v3 JSONL record to Vanguard Problem columns."""
    subj = _normalize_subject(r.get("subj", "") or "")

    return {
        "external_id": r.get("id"),
        "contest_family": r.get("contest", "other"),
        "contest_year": r.get("year"),
        "contest_round": None,  # v3 doesn't have round for most records
        "contest_level": None,
        "problem_number": r.get("prob_num"),
        "problem_text": _clean(r.get("text", "")),
        "text_format": r.get("fmt", "plain"),
        "answer": _clean(r.get("ans")) or None,
        "answer_type": r.get("ans_t", "unknown"),
        "choices": json.dumps(r["choices"]) if r.get("choices") else None,
        "official_solution": _clean(r.get("sol")) or None,
        "difficulty_band": r.get("diff"),
        "difficulty_source": r.get("diff_src"),
        "primary_domain": r.get("domain", "math"),
        "subject": subj or None,
        "grade_band": r.get("grade"),
        "requires_visual": bool(r.get("vis")),
        "source_dataset": r.get("src"),
        "source_path": r.get("src_file"),
        "source_url": r.get("src_url"),
        "extraction_method": r.get("ext_method"),
    }


def map_gemini_to_problem(r: dict, source_file: str) -> dict:
    """Map a Gemini MATHCOUNTS JSON record to Vanguard Problem columns."""
    return {
        "external_id": str(uuid.uuid4()),
        "contest_family": "mathcounts",
        "contest_year": r.get("contest_year"),
        "contest_round": r.get("contest_round"),
        "contest_level": r.get("contest_level"),
        "problem_number": r.get("problem_number"),
        "problem_text": r.get("problem_text", ""),
        "text_format": "plain",
        "answer": r.get("answer") or None,
        "answer_type": "numeric",  # MATHCOUNTS is always numeric
        "choices": None,
        "official_solution": None,
        "difficulty_band": None,
        "difficulty_source": None,
        "primary_domain": "math",
        "subject": "competition_math",
        "grade_band": "ms",
        "requires_visual": bool(r.get("figure_paths")),
        "source_dataset": "mathcounts_gemini",
        "source_path": r.get("source_path"),
        "source_url": None,
        "extraction_method": "vision_llm",
    }


# ── Columns (insertion order) ────────────────────────────────────────────────

COLUMNS = [
    "external_id", "contest_family", "contest_year", "contest_round",
    "contest_level", "problem_number", "problem_text", "text_format",
    "answer", "answer_type", "choices", "official_solution",
    "difficulty_band", "difficulty_source", "primary_domain", "subject",
    "grade_band", "requires_visual", "source_dataset", "source_path",
    "source_url", "extraction_method",
]

INSERT_SQL = f"""
INSERT INTO problems ({", ".join(COLUMNS)})
VALUES %s
ON CONFLICT (external_id) DO NOTHING
"""


# ── Streaming ingest ─────────────────────────────────────────────────────────

def ingest_perplexity(conn, dry_run: bool = False) -> int:
    """Stream Perplexity v3 JSONL shards into problems table."""
    total = 0
    skipped = 0
    batch = []

    for shard_name in PERPLEXITY_SHARDS:
        shard_path = PERPLEXITY_DIR / shard_name
        if not shard_path.exists():
            print(f"  SKIP: {shard_name} not found")
            continue

        print(f"  Processing {shard_name}...", end="", flush=True)
        shard_count = 0

        with open(shard_path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    skipped += 1
                    continue

                # Skip records with no text
                text = r.get("text", "")
                if not text or len(text.strip()) < 10:
                    skipped += 1
                    continue

                mapped = map_v3_to_problem(r)
                row = tuple(mapped[c] for c in COLUMNS)
                batch.append(row)
                shard_count += 1

                if len(batch) >= BATCH_SIZE and not dry_run:
                    with conn.cursor() as cur:
                        execute_values(cur, INSERT_SQL, batch, page_size=BATCH_SIZE)
                    conn.commit()
                    batch = []

        total += shard_count
        print(f" {shard_count:,} records")

    # Flush remaining
    if batch and not dry_run:
        with conn.cursor() as cur:
            execute_values(cur, INSERT_SQL, batch, page_size=BATCH_SIZE)
        conn.commit()

    if skipped:
        print(f"  Skipped {skipped:,} (no text or parse error)")
    return total


def ingest_gemini(conn, dry_run: bool = False) -> int:
    """Load Gemini MATHCOUNTS JSONs into problems table."""
    total = 0
    batch = []

    json_files = sorted(GEMINI_DIR.glob("*.json"))
    json_files = [f for f in json_files if "AUDIT" not in f.name and "QC" not in f.name]

    for jp in json_files:
        with open(jp) as f:
            records = json.load(f)

        for r in records:
            text = r.get("problem_text", "")
            if not text or len(text.strip()) < 10:
                continue

            mapped = map_gemini_to_problem(r, jp.name)
            row = tuple(mapped[c] for c in COLUMNS)
            batch.append(row)
            total += 1

    if batch and not dry_run:
        with conn.cursor() as cur:
            execute_values(cur, INSERT_SQL, batch, page_size=BATCH_SIZE)
        conn.commit()

    print(f"  Gemini MATHCOUNTS: {total:,} records from {len(json_files)} files")
    return total


def ingest_figures(conn) -> int:
    """Load Gemini figure paths into problem_figures table."""
    json_files = sorted(GEMINI_DIR.glob("*.json"))
    json_files = [f for f in json_files if "AUDIT" not in f.name and "QC" not in f.name]
    total = 0

    for jp in json_files:
        with open(jp) as f:
            records = json.load(f)

        for r in records:
            fig_paths = r.get("figure_paths", [])
            if not fig_paths:
                continue

            # Find the problem by contest lookup
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id FROM problems
                       WHERE contest_family = 'mathcounts'
                         AND contest_year = %s
                         AND contest_round = %s
                         AND contest_level = %s
                         AND problem_number = %s
                       LIMIT 1""",
                    (r["contest_year"], r["contest_round"],
                     r["contest_level"], r["problem_number"]),
                )
                row = cur.fetchone()
                if not row:
                    continue
                problem_id = row[0]

            for fp in fig_paths:
                if os.path.exists(fp):
                    with conn.cursor() as cur:
                        cur.execute(
                            """INSERT INTO problem_figures (problem_id, figure_path, figure_type)
                               VALUES (%s, %s, %s) ON CONFLICT DO NOTHING""",
                            (problem_id, fp, "diagram"),
                        )
                    total += 1

    conn.commit()
    print(f"  Figures linked: {total:,}")
    return total


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ingest problems into Vanguard DB")
    parser.add_argument("--dry-run", action="store_true", help="Count records without inserting")
    parser.add_argument("--source", choices=["perplexity", "gemini", "all"], default="all")
    parser.add_argument("--skip-figures", action="store_true", help="Skip figure linking")
    args = parser.parse_args()

    conn = psycopg2.connect(DB_URL)
    start = time.time()

    try:
        total = 0

        if args.source in ("perplexity", "all"):
            print("Ingesting Perplexity v3 database...")
            total += ingest_perplexity(conn, args.dry_run)

        if args.source in ("gemini", "all"):
            print("Ingesting Gemini MATHCOUNTS (1990-2013)...")
            total += ingest_gemini(conn, args.dry_run)

            if not args.skip_figures and not args.dry_run:
                print("Linking figures...")
                ingest_figures(conn)

        elapsed = time.time() - start
        action = "counted" if args.dry_run else "ingested"
        print(f"\nDone: {total:,} records {action} in {elapsed:.1f}s")

        if not args.dry_run:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM problems")
                print(f"Total in DB: {cur.fetchone()[0]:,}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
