"""Run a pytest-bdd scenario selected by its Gherkin tags."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a Gherkin scenario using its pytest marker tags."
    )
    parser.add_argument(
        "tags",
        nargs="+",
        help="Scenario tags to match, such as smoke and a scenario identifier.",
    )
    args = parser.parse_args()

    repository_root = Path(__file__).resolve().parent.parent
    marker_expression = " and ".join(args.tags)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-m", marker_expression],
        cwd=repository_root,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
