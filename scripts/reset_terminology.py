"""Flush persisted terminology state and optionally rebuild it for the configured source."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from clinical_coder.config import settings


def _remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        try:
            shutil.rmtree(path)
        except PermissionError as exc:
            raise PermissionError(
                f"Could not remove '{path}' because it is in use. Stop the app or any process using the "
                "terminology index, then run this command again."
            ) from exc
    else:
        path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove persisted terminology retrieval state and optionally rebuild the active index."
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the Chroma terminology index after flushing persisted state.",
    )
    args = parser.parse_args()

    persist_dir = Path(settings.chroma_persist_dir)
    try:
        _remove_path(persist_dir)
    except PermissionError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"Removed terminology index state: {persist_dir}")

    if args.rebuild:
        from scripts.index_code_lists import main as rebuild_index

        rebuild_index()


if __name__ == "__main__":
    main()
