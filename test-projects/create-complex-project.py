#!/usr/bin/env python3
"""
Create a complex nested project for pressure testing
"""

import os
import json
from pathlib import Path

def create_complex_project(project_path: str):
    """Create a complex, deeply nested project structure"""
    base_path = Path(project_path)

    # Create deeply nested structure with lots of files
    complex_structure = {
        "deeper/nested/structures": {
            "level1/level2/level3/level4": ["file1.txt", "file2.py", "file3.md"],
            "experiment/data/raw": ["dataset1.csv", "dataset2.json", "config.yml"],
            "analysis/scripts": ["analyze.py", "process.R", "visualize.py"],
            "results/figures": ["plot1.png", "chart2.pdf", "graph3.svg"],
            "documentation": ["readme.md", "setup.py", "requirements.txt"]
        },
        "random/junk/folders": {
            "temp": ["tmp1.tmp", "tmp2.tmp"],
            "old": ["old_file.bak", "deprecated.py"],
            "misc": ["notes.txt", "ideas.md", "scratch.py"]
        },
        "proper/structure": {
            "claude-code": ["session1.md", "session2.md"],
            "data": ["input.csv", "output.json"],
            "codes": ["main.py", "utils.py", "functions.R"],
            "paper": ["draft.md", "sections.md"],
            "pre": ["outline.md", "literature.md"]
        }
    }

    # Create the complex structure
    for main_dir, subdirs in complex_structure.items():
        main_path = base_path / main_dir
        main_path.mkdir(parents=True, exist_ok=True)

        for subdir, files in subdirs.items():
            subdir_path = main_path / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)

            for file_name in files:
                file_path = subdir_path / file_name
                with open(file_path, 'w') as f:
                    if file_name.endswith('.py'):
                        f.write(f"# Python script: {file_name}\nprint('Hello from {file_name}')\n")
                    elif file_name.endswith('.md'):
                        f.write(f"# {file_name}\n\nThis is a markdown file.\n")
                    elif file_name.endswith('.csv'):
                        f.write("col1,col2,col3\n1,2,3\n4,5,6\n")
                    elif file_name.endswith('.json'):
                        f.write('{"key": "value", "number": 42}\n')
                    else:
                        f.write(f"Content of {file_name}\n")

    # Create lots of small files everywhere
    for i in range(50):
        file_path = base_path / f"file_{i:03d}.txt"
        with open(file_path, 'w') as f:
            f.write(f"This is file number {i}\n")

    # Create some hidden files
    for i in range(10):
        file_path = base_path / f".hidden_{i}.tmp"
        with open(file_path, 'w') as f:
            f.write(f"Hidden file {i}\n")

    # Create project configuration
    config = {
        "project": {
            "name": "complex-nested-project",
            "type": "general",
            "path": str(base_path.absolute()),
            "created": "2025-12-12T15:55:00Z",
            "last_modified": "2025-12-12T15:55:00Z",
            "version": "0.1.0"
        },
        "structure": {
            "required_directories": [],
            "required_files": [],
            "compliance_score": 0
        },
        "configuration": {
            "git_initialized": False,
            "backup_enabled": True,
            "auto_validation": True
        },
        "metadata": {
            "author": "Pressure Test",
            "email": "test@example.com",
            "description": "Complex nested project for pressure testing",
            "tags": ["complex", "nested", "pressure-test"]
        },
        "skill_info": {
            "created_by": "manual-complex",
            "skill_version": "0.1.0",
            "template": "none"
        }
    }

    with open(base_path / ".project-config.json", 'w') as f:
        json.dump(config, f, indent=2)

if __name__ == "__main__":
    create_complex_project("test-projects/complex-nested-project")
    print("Complex nested project created successfully")