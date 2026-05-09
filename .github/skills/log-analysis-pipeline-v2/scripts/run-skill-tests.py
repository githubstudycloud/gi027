from pathlib import Path
import sys

from log_analysis_core_v2 import run_test_suite

if __name__ == "__main__":
    skill_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    locale = sys.argv[2] if len(sys.argv) > 2 else "en-US"
    print(run_test_suite(skill_root, locale))
