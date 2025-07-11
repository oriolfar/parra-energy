"""
Project Cleanup Script

This script analyzes the project structure and identifies:
1. Duplicate files
2. Unnecessary files
3. Files that should be in .gitignore
4. Potential issues with the project structure
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Files and directories to ignore
IGNORE_PATTERNS = {
    # Python
    '*.pyc', '__pycache__', '*.pyo', '*.pyd',
    '.Python', 'build/', 'develop-eggs/', 'dist/', 'downloads/', 'eggs/',
    '.eggs/', 'lib/', 'lib64/', 'parts/', 'sdist/', 'var/', 'wheels/',
    '*.egg-info/', '*.egg',
    # Virtual Environment
    'venv/', 'env/', '.env/', '.venv/',
    # IDE
    '.idea/', '.vscode/', '*.swp', '*.swo',
    # Git
    '.git/', '.gitignore',
    # Testing
    '.pytest_cache/', '.coverage', 'htmlcov/',
    # Logs
    '*.log',
}

def get_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def analyze_project() -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    """Analyze the project structure.
    
    Returns:
        Tuple containing:
        - Dictionary of duplicate files (hash -> list of paths)
        - List of unnecessary files
        - List of files that should be in .gitignore
    """
    project_root = Path('.')
    duplicate_files: Dict[str, List[str]] = {}
    unnecessary_files: List[str] = []
    should_ignore: List[str] = []
    
    # Track all files and their hashes
    file_hashes: Dict[str, List[str]] = {}
    
    # Walk through all files in the project
    for root, dirs, files in os.walk(project_root):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not any(d.endswith(p) for p in IGNORE_PATTERNS)]
        
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath)
            
            # Skip ignored files
            if any(rel_path.endswith(p) for p in IGNORE_PATTERNS):
                continue
                
            # Check if file should be in .gitignore
            if any(rel_path.endswith(p) for p in IGNORE_PATTERNS):
                should_ignore.append(rel_path)
                continue
            
            # Calculate file hash
            try:
                file_hash = get_file_hash(filepath)
                if file_hash in file_hashes:
                    file_hashes[file_hash].append(rel_path)
                else:
                    file_hashes[file_hash] = [rel_path]
            except Exception as e:
                print(f"Error processing {rel_path}: {e}")
    
    # Find duplicates
    duplicate_files = {h: paths for h, paths in file_hashes.items() if len(paths) > 1}
    
    # Find potentially unnecessary files
    for filepath in file_hashes.values():
        path = filepath[0]
        if path.endswith('.pyc') or path.endswith('.pyo'):
            unnecessary_files.append(path)
    
    return duplicate_files, unnecessary_files, should_ignore

def main():
    """Main function to analyze and report project structure."""
    print("Analyzing project structure...")
    print("=============================")
    
    duplicates, unnecessary, should_ignore = analyze_project()
    
    # Report duplicates
    if duplicates:
        print("\nDuplicate files found:")
        for hash_value, files in duplicates.items():
            print(f"\nFiles with hash {hash_value[:8]}...:")
            for file in files:
                print(f"  - {file}")
    else:
        print("\nNo duplicate files found.")
    
    # Report unnecessary files
    if unnecessary:
        print("\nPotentially unnecessary files:")
        for file in unnecessary:
            print(f"  - {file}")
    else:
        print("\nNo unnecessary files found.")
    
    # Report files that should be in .gitignore
    if should_ignore:
        print("\nFiles that should be in .gitignore:")
        for file in should_ignore:
            print(f"  - {file}")
    else:
        print("\nNo files need to be added to .gitignore.")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main() 