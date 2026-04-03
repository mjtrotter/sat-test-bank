import argparse
import sys
import asyncio


def main():
    parser = argparse.ArgumentParser(description="Vanguard CLI for data operations.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape AoPS command
    scrape_aops_parser = subparsers.add_parser("scrape-aops", help="Scrape problems from AoPS Wiki")
    scrape_aops_parser.add_argument("--contest", type=str, help="Specific contest to scrape (e.g., AMC10A, AIME_I)")
    scrape_aops_parser.add_argument("--year", type=int, help="Specific year to scrape (e.g., 2020)")
    scrape_aops_parser.set_defaults(func=run_scrape_aops)

    # Calibrate difficulty command
    cal_parser = subparsers.add_parser(
        "calibrate-difficulty",
        help="Run mini-model difficulty calibration pipeline",
    )
    cal_parser.add_argument(
        "--bands", type=str, default=None,
        help="Comma-separated band numbers to run (e.g., '0,1,2'). Default: all",
    )
    cal_parser.add_argument(
        "--source", type=str, default=None,
        help="Comma-separated contest families to filter (e.g., 'mathcounts,amc')",
    )
    cal_parser.add_argument(
        "--max-problems", type=int, default=None,
        help="Max problems per model (for testing/limiting run size)",
    )
    cal_parser.add_argument(
        "--resume", type=int, default=None, metavar="RUN_ID",
        help="Resume a previous calibration run by ID",
    )
    cal_parser.add_argument(
        "--dry-run", action="store_true",
        help="Print execution plan without running inference",
    )
    cal_parser.set_defaults(func=run_calibrate)

    # Seed taxonomy command
    seed_parser = subparsers.add_parser(
        "seed-taxonomy",
        help="Parse taxonomy-atomic.md and load skill nodes into the database",
    )
    seed_parser.add_argument(
        "--spec", type=str, default="specs/taxonomy-atomic.md",
        help="Path to taxonomy markdown file (default: specs/taxonomy-atomic.md)",
    )
    seed_parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse and validate only — don't write to database",
    )
    seed_parser.add_argument(
        "--validate-only", action="store_true",
        help="Only validate prerequisite graph (no DB write, no summary)",
    )
    seed_parser.set_defaults(func=run_seed_taxonomy)

    # Tag problems with skill nodes
    tag_parser = subparsers.add_parser(
        "tag-problems",
        help="Tag problems with skill nodes using keyword-based domain classification",
    )
    tag_parser.add_argument(
        "--source", type=str, default=None,
        help="Comma-separated contest families to tag (default: all)",
    )
    tag_parser.add_argument(
        "--limit", type=int, default=None,
        help="Max problems to process",
    )
    tag_parser.add_argument(
        "--include-tagged", action="store_true",
        help="Re-tag problems that already have tags",
    )
    tag_parser.add_argument(
        "--dry-run", action="store_true",
        help="Classify and count but don't write to database",
    )
    tag_parser.set_defaults(func=run_tag_problems)

    # LLM-assisted skill tagging (Phase 2)
    llm_tag_parser = subparsers.add_parser(
        "tag-problems-llm",
        help="Tag problems with skill nodes using Claude API classification",
    )
    llm_tag_parser.add_argument(
        "--source", type=str, default=None,
        help="Comma-separated contest families to tag (default: all)",
    )
    llm_tag_parser.add_argument(
        "--limit", type=int, default=None,
        help="Max problems to process",
    )
    llm_tag_parser.add_argument(
        "--batch-size", type=int, default=20,
        help="Problems per API call (default: 20)",
    )
    llm_tag_parser.add_argument(
        "--model", type=str, default="claude-sonnet-4-20250514",
        help="Claude model to use",
    )
    llm_tag_parser.add_argument(
        "--include-tagged", action="store_true",
        help="Re-tag problems already tagged by LLM",
    )
    llm_tag_parser.add_argument(
        "--dry-run", action="store_true",
        help="Print plan without making API calls",
    )
    llm_tag_parser.set_defaults(func=run_tag_problems_llm)

    args = parser.parse_args()

    if hasattr(args, "func"):
        asyncio.run(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


async def run_scrape_aops(args):
    from src.extraction.aops_scraper import scrape_aops_problems
    print(f"Running AoPS scraper with contest: {args.contest}, year: {args.year}")
    await scrape_aops_problems(contest=args.contest, year=args.year)


async def run_calibrate(args):
    from src.calibration.pipeline import run_calibration

    bands = None
    if args.bands:
        bands = [int(b.strip()) for b in args.bands.split(",")]

    source_filter = None
    if args.source:
        source_filter = [s.strip() for s in args.source.split(",")]

    print("=" * 60)
    print("Vanguard Mini-Model Difficulty Calibration")
    print("=" * 60)

    run_id = await run_calibration(
        bands=bands,
        source_filter=source_filter,
        max_problems=args.max_problems,
        resume_run_id=args.resume,
        dry_run=args.dry_run,
    )

    print(f"\nRun ID: {run_id}")


async def run_seed_taxonomy(args):
    from pathlib import Path
    from src.services.taxonomy_loader import TaxonomyLoader

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"Error: Taxonomy spec not found at {spec_path}")
        sys.exit(1)

    loader = TaxonomyLoader(str(spec_path))

    print(f"Parsing {spec_path}...")
    nodes = await loader.parse_markdown()
    print(f"Parsed {len(nodes)} skill nodes")

    errors = loader.validate_prerequisites()
    if errors:
        print(f"\n{len(errors)} validation error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("Prerequisite graph validated — no cycles or orphan references")

    if args.validate_only:
        return

    loader.print_summary_stats()

    if args.dry_run:
        print("Dry run — skipping database write")
        return

    from sqlalchemy import select
    from src.core.database import async_session
    from src.models.tables import SkillNode

    async with async_session() as session:
        existing = await session.execute(select(SkillNode.id))
        existing_ids = {row[0] for row in existing.fetchall()}

        if existing_ids:
            new_nodes = [n for n in nodes if n["id"] not in existing_ids]
            skipped = len(nodes) - len(new_nodes)
            if skipped:
                print(f"Skipping {skipped} nodes already in DB")
            if not new_nodes:
                print("All nodes already loaded — nothing to do")
                return
            # Temporarily replace the data list for load_to_db
            loader.skill_nodes_data = new_nodes

        await loader.load_to_db(session)


async def run_tag_problems_llm(args):
    import os
    from src.core.database import async_session
    from src.services.llm_tagger import batch_tag_llm

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    source_filter = None
    if args.source:
        source_filter = [s.strip() for s in args.source.split(",")]

    print("=" * 60)
    print("Vanguard Problem Skill Tagger (Phase 2 — LLM)")
    print("=" * 60)
    print(f"Model: {args.model}")
    if source_filter:
        print(f"Sources: {', '.join(source_filter)}")
    if args.limit:
        print(f"Limit: {args.limit}")
    if args.dry_run:
        print("DRY RUN — no API calls")

    async with async_session() as session:
        stats = await batch_tag_llm(
            session,
            api_key=api_key,
            source_filter=source_filter,
            limit=args.limit,
            batch_size=args.batch_size,
            skip_tagged=not args.include_tagged,
            model=args.model,
            dry_run=args.dry_run,
        )

    print(f"\nResults:")
    print(f"  Problems processed: {stats['total']}")
    print(f"  Batches: {stats['batches']}")
    print(f"  Tagged: {stats['tagged']}")
    print(f"  Tags created: {stats['tags_created']}")
    if stats.get("invalid_nodes"):
        print(f"  Invalid node IDs (skipped): {stats['invalid_nodes']}")


async def run_tag_problems(args):
    from src.core.database import async_session
    from src.services.skill_tagger import batch_tag

    source_filter = None
    if args.source:
        source_filter = [s.strip() for s in args.source.split(",")]

    print("=" * 60)
    print("Vanguard Problem Skill Tagger (Phase 1 — keyword)")
    print("=" * 60)

    if source_filter:
        print(f"Sources: {', '.join(source_filter)}")
    if args.limit:
        print(f"Limit: {args.limit}")
    if args.dry_run:
        print("DRY RUN — no database writes")

    async with async_session() as session:
        stats = await batch_tag(
            session,
            source_filter=source_filter,
            limit=args.limit,
            skip_tagged=not args.include_tagged,
            dry_run=args.dry_run,
        )

    print(f"\nResults:")
    print(f"  Problems processed: {stats['total']}")
    print(f"  Tagged: {stats['tagged']}")
    print(f"  Skipped (no domain match): {stats['skipped']}")
    print(f"  Tags created: {stats['tags_created']}")


if __name__ == "__main__":
    main()
