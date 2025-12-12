#!/usr/bin/env python3
"""
Project Structure Validator
Tests project compliance according to skill specifications
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

class ProjectValidator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_config = self._load_project_config()
        self.project_type = self.project_config.get("project", {}).get("type", "general")
        self.templates = self._load_templates()

    def _load_project_config(self) -> Dict:
        """Load project configuration from .project-config.json"""
        config_path = self.project_path / ".project-config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def _load_templates(self) -> Dict:
        """Load project structure templates"""
        template_path = self.project_path.parent.parent / "templates" / "project-structures"
        templates = {}

        for project_type in ["research-project", "data-analysis", "paper-writing", "general"]:
            template_file = template_path / f"{project_type}/structure.yml"
            if template_file.exists():
                with open(template_file, 'r') as f:
                    templates[project_type] = yaml.safe_load(f)

        return templates

    def validate(self) -> Dict:
        """Validate project structure and return compliance report"""
        template = self.templates.get(self.project_type, {})

        if not template:
            return {
                "success": False,
                "error": f"Unknown project type: {self.project_type}",
                "compliance_score": 0
            }

        required_dirs = template.get("required_directories", [])
        required_files = template.get("required_files", [])

        # Check directories
        missing_dirs = []
        present_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_path / dir_path
            if full_path.exists() and full_path.is_dir():
                present_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)

        # Check files
        missing_files = []
        present_files = []
        for file_path in required_files:
            full_path = self.project_path / file_path
            if full_path.exists() and full_path.is_file():
                present_files.append(file_path)
            else:
                missing_files.append(file_path)

        # Calculate compliance score
        total_items = len(required_dirs) + len(required_files)
        present_items = len(present_dirs) + len(present_files)
        compliance_score = int((present_items / total_items) * 100) if total_items > 0 else 0

        # Find extra items
        all_items = set()
        for item in self.project_path.rglob("*"):
            if item.name.startswith('.'):
                continue
            relative_path = item.relative_to(self.project_path)
            if item.is_file():
                if str(relative_path) not in required_files:
                    all_items.add(str(relative_path))
            elif item.is_dir():
                if str(relative_path) not in required_dirs:
                    all_items.add(str(relative_path))

        return {
            "success": True,
            "compliance_score": compliance_score,
            "project_type": self.project_type,
            "structure_analysis": {
                "required_dirs_present": present_dirs,
                "required_files_present": present_files,
                "missing_items": missing_dirs + missing_files,
                "extra_items": sorted(list(all_items))
            },
            "issues_found": self._generate_issues(missing_dirs, missing_files, list(all_items)),
            "suggestions": self._generate_suggestions(missing_dirs, missing_files, list(all_items))
        }

    def _generate_issues(self, missing_dirs: List[str], missing_files: List[str], extra_items: List[str]) -> List[str]:
        """Generate list of issues found"""
        issues = []
        if missing_dirs:
            issues.append(f"Missing required directories: {', '.join(missing_dirs)}")
        if missing_files:
            issues.append(f"Missing required files: {', '.join(missing_files)}")
        if extra_items:
            issues.append(f"Extra items found: {', '.join(extra_items[:5])}")
        return issues

    def _generate_suggestions(self, missing_dirs: List[str], missing_files: List[str], extra_items: List[str]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        if missing_dirs:
            suggestions.append("Create missing required directories")
        if missing_files:
            suggestions.append("Create missing required files")
        if extra_items:
            suggestions.append("Move extra items to appropriate standard directories")
        return suggestions

def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python test-validator.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]
    validator = ProjectValidator(project_path)
    result = validator.validate()

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()