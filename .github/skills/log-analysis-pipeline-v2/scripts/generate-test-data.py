from pathlib import Path
import sys

from log_analysis_core_v2 import generate_fixtures

if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "tests" / "fixtures"
    paths = generate_fixtures(out)
    for p in paths:
        print(p)
