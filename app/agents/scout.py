
"""Discover eligible Python source files in a local workspace."""

import os
from pathlib import Path
from typing import TypedDict


EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        "site-packages",
    }
)


class DiscoveryResult(TypedDict):
    """Result of a bounded Python file discovery operation."""

    files: list[Path]
    limit_reached: bool


def discover_python_files_detailed(
    root: str | Path,
    max_files: int = 500,
) -> DiscoveryResult:
    """Discover Python files and indicate whether the limit truncated results.

    The limit is considered reached only when an additional eligible Python
    file exists beyond the returned list.
    """
    if isinstance(max_files, bool) or not isinstance(max_files, int):
        raise ValueError("max_files must be a positive integer.")

    if max_files < 1:
        raise ValueError("max_files must be a positive integer.")

    root_path = Path(root).resolve()

    if not root_path.is_dir():
        raise ValueError("Workspace root must be an existing directory.")

    discovered: list[Path] = []

    for current_dir, dir_names, file_names in os.walk(
        root_path,
        followlinks=False,
    ):
        # Prune excluded directories before descending into them.
        dir_names[:] = sorted(
            name
            for name in dir_names
            if name not in EXCLUDED_DIRS
        )

        for filename in sorted(file_names):
            if not filename.endswith(".py"):
                continue

            # We have already collected max_files. This eligible file proves
            # that the result would be truncated, so do not include it.
            if len(discovered) >= max_files:
                return {
                    "files": discovered,
                    "limit_reached": True,
                }

            discovered.append(Path(current_dir) / filename)

    return {
        "files": discovered,
        "limit_reached": False,
    }


def discover_python_files(
    root: str | Path,
    max_files: int = 500,
) -> list[Path]:
    """Return eligible Python files beneath a workspace root."""
    return discover_python_files_detailed(
        root,
        max_files=max_files,
    )["files"]
