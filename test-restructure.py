#!/usr/bin/env python3
"""
Project Restructurer
Restructures projects to standard format with backup support
"""

import os
import json
import shutil
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ProjectRestructurer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.backup_path = self.project_path.parent / f".backup_{self.project_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def restructure(self, backup: bool = True, remove_nonstandard: bool = True, force: bool = False, target_type: str = None) -> Dict:
        """Restructure project to standard format"""

        try:
            # Determine project type
            project_type = target_type or self._detect_project_type()

            # Create backup if requested
            if backup:
                self._create_backup()

            # Load target structure
            target_structure = self._load_target_structure(project_type)

            # Analyze existing structure
            analysis = self._analyze_existing_structure()

            # Restructure project
            moved_files, created_dirs, removed_dirs = self._perform_restructure(
                target_structure, analysis, remove_nonstandard
            )

            # Update project configuration
            self._update_project_config(project_type)

            return {
                "success": True,
                "message": "Project restructured successfully",
                "data": {
                    "backup_path": str(self.backup_path) if backup else None,
                    "moved_files": moved_files,
                    "created_directories": created_dirs,
                    "removed_directories": removed_dirs,
                    "project_type": project_type
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Restructure failed: {str(e)}",
                "error": str(e)
            }

    def _detect_project_type(self) -> str:
        """Auto-detect project type from existing structure"""
        # Check for .project-config.json first
        config_path = self.project_path / ".project-config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get("project", {}).get("type", "general")

        # Simple heuristic based on directory names
        dirs = [d.name.lower() for d in self.project_path.iterdir() if d.is_dir()]

        if any(x in dirs for x in ['raw', 'processed', 'etl', 'analysis']):
            return "data-analysis"
        elif any(x in dirs for x in ['chapters', 'sections', 'figures', 'tables']):
            return "paper-writing"
        elif any(x in dirs for x in ['literature', 'scripts', 'outlines']):
            return "research-project"
        else:
            return "general"

    def _load_target_structure(self, project_type: str) -> Dict:
        """Load target structure from templates"""
        template_path = self.project_path.parent.parent / "templates" / "project-structures" / f"{project_type}/structure.yml"

        if template_path.exists():
            with open(template_path, 'r') as f:
                return yaml.safe_load(f)

        # Fallback to general structure
        return {
            "required_directories": ["claude-code", "data", "codes", "paper", "pre"],
            "required_files": ["README.md", ".gitignore", "project.yml", ".project-config.json"]
        }

    def _create_backup(self):
        """Create backup of existing project"""
        if self.backup_path.exists():
            shutil.rmtree(self.backup_path)

        shutil.copytree(self.project_path, self.backup_path)
        print(f"Backup created at: {self.backup_path}")

    def _analyze_existing_structure(self) -> Dict:
        """Analyze existing project structure"""
        existing_dirs = []
        existing_files = []

        for item in self.project_path.iterdir():
            if item.name.startswith('.'):
                continue

            if item.is_dir():
                existing_dirs.append(item.name)
            elif item.is_file():
                existing_files.append(item.name)

        return {
            "directories": existing_dirs,
            "files": existing_files
        }

    def _perform_restructure(self, target_structure: Dict, analysis: Dict, remove_nonstandard: bool) -> Tuple[List, List, List]:
        """Perform the actual restructuring"""
        moved_files = []
        created_dirs = []
        removed_dirs = []

        required_dirs = target_structure.get("required_directories", [])
        optional_dirs = target_structure.get("optional_directories", [])
        special_files = target_structure.get("special_files", [])

        # Create missing required directories
        for dir_path in required_dirs:
            full_path = self.project_path / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(dir_path)

        # Create optional directories if they don't exist
        for dir_path in optional_dirs:
            full_path = self.project_path / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(dir_path)

        # Create special .gitkeep files
        for file_path in special_files:
            full_path = self.project_path / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.touch()
                moved_files.append(f"Created {file_path}")

        # Move files to appropriate locations (simplified logic)
        for file_name in analysis["files"]:
            file_path = self.project_path / file_name

            # Skip if it's a required file
            if file_name in ["README.md", ".gitignore", "project.yml", ".project-config.json"]:
                continue

            # Simple file categorization
            if file_name.endswith('.py') or file_name.endswith('.R'):
                target_dir = self.project_path / "codes"
            elif file_name.endswith('.md'):
                target_dir = self.project_path / "paper"
            elif file_name.endswith(('.csv', '.xlsx', '.json')):
                target_dir = self.project_path / "data"
            else:
                continue

            if not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(target_dir.relative_to(self.project_path)))

            target_path = target_dir / file_name
            if not target_path.exists():
                shutil.move(str(file_path), str(target_path))
                moved_files.append(f"{file_name} → {target_dir.name}/{file_name}")

        # Remove nonstandard directories if requested
        if remove_nonstandard:
            all_standard_dirs = set(required_dirs + optional_dirs)
            existing_dirs = set(analysis["directories"])

            for dir_name in existing_dirs - all_standard_dirs:
                dir_path = self.project_path / dir_name
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    removed_dirs.append(dir_name)

        return moved_files, created_dirs, removed_dirs

    def _update_project_config(self, project_type: str):
        """Update project configuration file"""
        config_path = self.project_path / ".project-config.json"

        if not config_path.exists():
            # Create new config
            config = {
                "project": {
                    "name": self.project_path.name,
                    "type": project_type,
                    "path": str(self.project_path.absolute()),
                    "created": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat(),
                    "version": "0.1.0"
                },
                "structure": {
                    "required_directories": [],
                    "required_files": ["README.md", ".gitignore", "project.yml"],
                    "compliance_score": 100
                },
                "configuration": {
                    "git_initialized": False,
                    "backup_enabled": True,
                    "auto_validation": True
                },
                "skill_info": {
                    "created_by": "project-management-restructure",
                    "skill_version": "0.1.0",
                    "template": f"{project_type}-standard"
                }
            }
        else:
            # Update existing config
            with open(config_path, 'r') as f:
                config = json.load(f)

            config["project"]["type"] = project_type
            config["project"]["last_modified"] = datetime.now().isoformat()

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test-restructure.py <project_path> [--no-backup] [--keep-nonstandard] [--type <type>]")
        sys.exit(1)

    project_path = sys.argv[1]
    backup = "--no-backup" not in sys.argv
    remove_nonstandard = "--keep-nonstandard" not in sys.argv
    target_type = None

    if "--type" in sys.argv:
        type_index = sys.argv.index("--type")
        if type_index + 1 < len(sys.argv):
            target_type = sys.argv[type_index + 1]

    restructurer = ProjectRestructurer(project_path)
    result = restructurer.restructure(backup=backup, remove_nonstandard=remove_nonstandard, target_type=target_type)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()