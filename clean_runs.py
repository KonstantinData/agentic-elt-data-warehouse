#!/usr/bin/env python3
"""
clean_runs.py

Removes all pipeline run artifacts to provide a clean repository state.
Keeps the directory structure but removes all run-specific data.
"""

import shutil
from pathlib import Path


def clean_artifacts():
    """Remove all run artifacts while preserving directory structure."""
    repo_root = Path(__file__).resolve().parent
    
    # Directories to clean (remove all subdirectories with run IDs)
    artifact_dirs = [
        repo_root / "artifacts" / "bronze",
        repo_root / "artifacts" / "silver", 
        repo_root / "artifacts" / "gold" / "marts",
        repo_root / "artifacts" / "orchestrator",
        repo_root / "artifacts" / "reports"
    ]
    
    # Temp directories to clean completely
    temp_dirs = [
        repo_root / "tmp"
    ]
    
    files_removed = 0
    dirs_removed = 0
    
    # Clean artifact directories (keep structure, remove run folders)
    for artifact_dir in artifact_dirs:
        if artifact_dir.exists():
            for run_dir in artifact_dir.iterdir():
                if run_dir.is_dir() and not run_dir.name.startswith('.'):
                    print(f"Removing: {run_dir}")
                    shutil.rmtree(run_dir)
                    dirs_removed += 1
                elif run_dir.is_file() and not run_dir.name.startswith('.'):
                    print(f"Removing: {run_dir}")
                    run_dir.unlink()
                    files_removed += 1
    
    # Clean temp directories completely
    for temp_dir in temp_dirs:
        if temp_dir.exists():
            print(f"Removing temp directory: {temp_dir}")
            shutil.rmtree(temp_dir)
            dirs_removed += 1
    
    # Clean bronze state file
    state_file = repo_root / "artifacts" / "bronze" / "_state" / "last_ingested.yaml"
    if state_file.exists():
        print(f"Removing state file: {state_file}")
        state_file.unlink()
        files_removed += 1
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Directories removed: {dirs_removed}")
    print(f"   Files removed: {files_removed}")
    print(f"   Repository is now clean for fresh runs.")


if __name__ == "__main__":
    clean_artifacts()