#!/usr/bin/env python
"""
EE Deployment Clean Script

Cleans all cache files and temporary artifacts from EE directory
to prepare for deployment.

Usage:
    python scripts/clean_deployment.py [--verbose]
"""

import sys
import argparse
from pathlib import Path


def clean_pycache(ee_root: Path, verbose: bool = False) -> int:
    """Remove all __pycache__ directories."""
    count = 0
    for pycache in ee_root.rglob("__pycache__"):
        try:
            pycache.rmdir()
            if verbose:
                print(f"Removed: {pycache.relative_to(ee_root)}")
            count += 1
        except OSError:
            # Directory not empty, use shutil.rmtree
            import shutil
            try:
                shutil.rmtree(pycache)
                if verbose:
                    print(f"Removed: {pycache.relative_to(ee_root)}")
                count += 1
            except Exception as e:
                print(f"Failed to remove {pycache}: {e}")
    return count


def clean_pyc_files(ee_root: Path, verbose: bool = False) -> int:
    """Remove all .pyc files."""
    count = 0
    for pyc_file in ee_root.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            if verbose:
                print(f"Removed: {pyc_file.relative_to(ee_root)}")
            count += 1
        except Exception as e:
            print(f"Failed to remove {pyc_file}: {e}")
    return count


def clean_pytest_cache(ee_root: Path, verbose: bool = False) -> int:
    """Remove .pytest_cache directories."""
    count = 0
    import shutil
    for pytest_cache in ee_root.rglob(".pytest_cache"):
        try:
            shutil.rmtree(pytest_cache)
            if verbose:
                print(f"Removed: {pytest_cache.relative_to(ee_root)}")
            count += 1
        except Exception as e:
            print(f"Failed to remove {pytest_cache}: {e}")
    return count


def main() -> int:
    """Main cleaning routine."""
    parser = argparse.ArgumentParser(
        description="Clean EE directory for deployment"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--ee-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Path to EE root directory"
    )

    args = parser.parse_args()

    ee_root = args.ee_root.resolve()
    verbose = args.verbose

    print(f"Cleaning EE directory: {ee_root}")
    print()

    # Clean cache
    pycache_count = clean_pycache(ee_root, verbose)
    pyc_count = clean_pyc_files(ee_root, verbose)
    pytest_count = clean_pytest_cache(ee_root, verbose)

    # Summary
    total = pycache_count + pyc_count + pytest_count
    print()
    print(f"Cleaning Summary:")
    print(f"  __pycache__ directories: {pycache_count}")
    print(f"  .pyc files: {pyc_count}")
    print(f"  .pytest_cache directories: {pytest_count}")
    print(f"  Total items removed: {total}")
    print()
    print("EE directory is clean and ready for deployment!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
