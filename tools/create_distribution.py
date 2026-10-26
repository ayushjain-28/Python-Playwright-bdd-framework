"""Create a source archive without credentials or local/generated files."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

EXCLUDED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "allure-results",
    "artifacts",
    "build",
    "dist",
    "logs",
    "playwright-report",
    "test-results",
    "venv",
}


def _is_excluded(relative_path: Path) -> bool:
    if any(part in EXCLUDED_DIRECTORIES for part in relative_path.parts):
        return True

    name = relative_path.name
    return name == ".env" or (name.startswith(".env.") and name != ".env.example")


def create_archive(output_path: Path | None = None) -> Path:
    repository_root = Path(__file__).resolve().parent.parent
    archive_path = (
        output_path
        if output_path is not None
        else repository_root / "dist" / f"{repository_root.name}.zip"
    ).resolve()
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for file_path in sorted(repository_root.rglob("*")):
            relative_path = file_path.relative_to(repository_root)
            if (
                not file_path.is_file()
                or file_path.is_symlink()
                or _is_excluded(relative_path)
                or file_path.resolve() == archive_path
            ):
                continue

            archive_name = PurePosixPath(
                repository_root.name, *relative_path.parts
            ).as_posix()
            archive.write(file_path, archive_name)

    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a source ZIP excluding secrets and local/generated files."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Archive destination (defaults to dist/<repository-name>.zip).",
    )
    args = parser.parse_args()

    archive_path = create_archive(args.output)
    print(f"Created {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
