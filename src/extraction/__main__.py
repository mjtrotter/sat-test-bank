"""CLI entry point: python -m src.extraction [command] [options]"""

import argparse
import sys

from src.extraction.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Vanguard Extraction Pipeline")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract = subparsers.add_parser("extract", help="Run MATHCOUNTS extraction pipeline")
    extract.add_argument("pdf_dir", nargs="?", default=None, help="Path to MathCounts Tests/")
    extract.add_argument("--output-dir", default=None)
    extract.add_argument("--image-dir", default=None)
    extract.add_argument("--year-start", type=int, default=2002)
    extract.add_argument("--year-end", type=int, default=2013)
    extract.add_argument("--levels", nargs="+", default=["chapter", "state"])

    args = parser.parse_args()

    if args.command == "extract":
        years = range(args.year_start, args.year_end + 1)
        run_pipeline(
            pdf_dir=args.pdf_dir,
            output_dir=args.output_dir,
            image_dir=args.image_dir,
            years=years,
            levels=args.levels,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
