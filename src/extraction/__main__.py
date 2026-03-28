
import sys

# This allows running the module as a script
if __package__ is None and not hasattr(sys, 'frozen'):
    # direct call to __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

from src.extraction.pipeline import run_pipeline

if __name__ == "__main__":
    """
    CLI entry point for the extraction module.
    Allows running the pipeline with: python -m src.extraction
    """
    print("Running MATHCOUNTS extraction pipeline...")
    run_pipeline()
