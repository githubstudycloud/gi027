from pathlib import Path
import sys

from log_analysis_core import generate_fixtures

if __name__ == "__main__":
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./tests/fixtures")
    print(generate_fixtures(output_dir))
