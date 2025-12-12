#!/usr/bin/env python3
"""
Project Status Reporter
Generates comprehensive project status reports
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class ProjectStatusReporter:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def generate_status(self, include_git: bool = True, include_file_stats: bool = True) -> Dict:
        """Generate comprehensive project status report"""

        # Basic project info
        project_info = self._get_project_info()

        # Structure statistics
        structure_stats = self._get_structure_stats()

        # File breakdown
        file_breakdown = self._get_file_breakdown()

        # Git information
        git_info = {}
        if include_git:
            git_info = self._get_git_info()

        return {
            "success": True,
            "message": "Status report generated",
            "data": {
                "project_info": project_info,
                "structure_stats": structure_stats,
                "file_breakdown": file_breakdown,
                "git_info": git_info,
                "timestamp": datetime.now().isoformat()
            }
        }

    def _get_project_info(self) -> Dict:
        """Get basic project information"""
        config_path = self.project_path / ".project-config.json"

        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                project_data = config.get("project", {})
                return {
                    "name": project_data.get("name", "Unknown"),
                    "path": str(self.project_path.absolute()),
                    "type": project_data.get("type", "general"),
                    "last_modified": self._get_last_modified(),
                    "version": project_data.get("version", "0.1.0"),
                    "metadata": config.get("metadata", {})
                }

        return {
            "name": self.project_path.name,
            "path": str(self.project_path.absolute()),
            "type": "general",
            "last_modified": self._get_last_modified(),
            "version": "0.1.0"
        }

    def _get_last_modified(self) -> str:
        """Get last modification time for the project"""
        try:
            latest_file = max(
                (f for f in self.project_path.rglob("*") if f.is_file()),
                key=lambda f: f.stat().st_mtime
            )
            return datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
        except (ValueError, FileNotFoundError):
            return datetime.now().isoformat()

    def _get_structure_stats(self) -> Dict:
        """Get project structure statistics"""
        directories = list(self.project_path.rglob("*/"))
        files = list(self.project_path.rglob("*"))

        total_files = sum(1 for f in files if f.is_file() and not f.name.startswith('.'))
        total_directories = len([d for d in directories if not any(parent.name.startswith('.') for parent in d.parents)])

        # Calculate project size
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        project_size_mb = round(total_size / (1024 * 1024), 2)

        return {
            "total_directories": total_directories,
            "total_files": total_files,
            "project_size_mb": project_size_mb,
            "compliance_score": self._calculate_compliance_score()
        }

    def _get_file_breakdown(self) -> Dict:
        """Get detailed file breakdown by directory"""
        breakdown = {}

        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if item.name in ['data', 'codes', 'paper', 'pre', 'claude-code']:
                    files = list(item.rglob("*"))
                    file_count = sum(1 for f in files if f.is_file() and not f.name.startswith('.'))
                    size_bytes = sum(f.stat().st_size for f in files if f.is_file())
                    size_mb = round(size_bytes / (1024 * 1024), 2)

                    breakdown[f"{item.name}/"] = {
                        "files": file_count,
                        "size_mb": size_mb
                    }

        return breakdown

    def _get_git_info(self) -> Dict:
        """Get git repository information"""
        try:
            # Check if it's a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {"initialized": False}

            # Get commit count
            commits_result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )

            # Get branches
            branches_result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )

            # Get last commit
            last_commit_result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )

            return {
                "initialized": True,
                "commits": int(commits_result.stdout.strip()) if commits_result.returncode == 0 else 0,
                "branches": len(branches_result.stdout.strip().split('\n')) if branches_result.returncode == 0 else 0,
                "last_commit": last_commit_result.stdout.strip() if last_commit_result.returncode == 0 else None
            }

        except (subprocess.SubprocessError, FileNotFoundError):
            return {"initialized": False, "error": "Git not available"}

    def _calculate_compliance_score(self) -> int:
        """Calculate compliance score based on structure"""
        # Import validator for compliance calculation
        import sys
        sys.path.append(str(Path(__file__).parent))

        try:
            from test_validator import ProjectValidator
            validator = ProjectValidator(str(self.project_path))
            result = validator.validate()
            return result.get("compliance_score", 0)
        except ImportError:
            return 0

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test-status.py <project_path> [--no-git] [--no-file-stats]")
        sys.exit(1)

    project_path = sys.argv[1]
    include_git = "--no-git" not in sys.argv
    include_file_stats = "--no-file-stats" not in sys.argv

    reporter = ProjectStatusReporter(project_path)
    result = reporter.generate_status(include_git=include_git, include_file_stats=include_file_stats)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()