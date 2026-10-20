"""Run from any directory: python /path/to/rumor_llm_study/run.py --help."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from rumor_sim.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
