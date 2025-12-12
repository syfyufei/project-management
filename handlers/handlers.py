"""
Project Management Skill - Core Handlers

This module provides the core business logic for the Project Management skill,
implementing the four main operations: create, restructure, validate, and status.

All handlers follow TDD principles with comprehensive error handling and
pressure-tested scenarios for real-world usage.
"""

import os
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re


class ProjectManagementError(Exception):
    """Base exception for project management operations"""
    pass


class ValidationError(ProjectManagementError):
    """Exception raised during project validation"""
    pass


class CreationError(ProjectManagementError):
    """Exception raised during project creation"""
    pass


class RestructureError(ProjectManagementError):
    """Exception raised during project restructuring"""
    pass


def validate_project_name(name: str) -> bool:
    """Validate project name follows kebab-case format"""
    if not name:
        return False
    # kebab-case: starts with letter, contains only letters, numbers, and hyphens
    pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
    return bool(re.match(pattern, name))


def get_project_config() -> Dict[str, Any]:
    """Load project configuration"""
    config_path = Path(__file__).parent.parent / "config" / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)

    # Default configuration
    return {
        "project_types": {
            "research-project": {
                "description": "Academic research projects with data analysis and paper writing",
                "required_dirs": ["claude-code", "data/raw", "data/processed", "codes/scripts", "paper/sections", "pre/literature"],
                "optional_dirs": ["data/external", "codes/notebooks", "paper/figures", "pre/proposals"],
                "required_files": ["README.md", ".gitignore", "project.yml", ".project-config.json"]
            },
            "data-analysis": {
                "description": "Data analysis projects with ETL and reporting",
                "required_dirs": ["claude-code", "data/raw", "data/processed", "codes/etl", "codes/analysis", "reports/drafts"],
                "optional_dirs": ["data/exports", "codes/models", "codes/visualization", "reports/presentations"],
                "required_files": ["README.md", ".gitignore", "project.yml", ".project-config.json"]
            },
            "paper-writing": {
                "description": "Academic paper writing projects",
                "required_dirs": ["claude-code", "data/figures", "data/tables", "codes/analysis", "paper/chapters", "pre/outlines"],
                "optional_dirs": ["data/supplementary", "paper/sections", "pre/drafts", "pre/reviews"],
                "required_files": ["README.md", ".gitignore", "project.yml", ".project-config.json"]
            },
            "general": {
                "description": "General purpose projects with flexible structure",
                "required_dirs": ["claude-code", "data", "codes", "paper", "pre"],
                "optional_dirs": [],
                "required_files": ["README.md", ".gitignore", "project.yml", ".project-config.json"]
            }
        },
        "validation": {
            "scoring_weights": {
                "directories": 40,
                "required_files": 35,
                "content_quality": 15,
                "git_integration": 10
            }
        },
        "templates": {
            "variable_pattern": "{{(\\w+)}}",
            "default_author": "Adrian"
        }
    }


def create_project(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new project with standardized directory structure

    Args:
        payload: Dictionary containing project creation parameters
            - project_name (str, required): Project name in kebab-case
            - project_type (str, required): Type of project
            - root (str, optional): Root directory path
            - git_init (bool, optional): Initialize Git repository
            - force (bool, optional): Overwrite existing directory
            - author_name (str, optional): Author name
            - description (str, optional): Project description

    Returns:
        Dict containing operation result with success status and details
    """
    try:
        # Validate required parameters
        project_name = payload.get('project_name')
        project_type = payload.get('project_type')

        if not project_name:
            raise CreationError("project_name is required")

        if not validate_project_name(project_name):
            raise CreationError(f"Invalid project name '{project_name}'. Must be kebab-case.")

        if not project_type:
            raise CreationError("project_type is required")

        config = get_project_config()
        if project_type not in config['project_types']:
            raise CreationError(f"Unknown project type '{project_type}'. Available: {list(config['project_types'].keys())}")

        # Set default values
        root = payload.get('root', os.getcwd())
        git_init = payload.get('git_init', True)
        force = payload.get('force', False)
        author_name = payload.get('author_name', config['templates']['default_author'])
        description = payload.get('description', f"A {project_type} created by Project Management skill")

        # Create project path
        project_path = Path(root) / project_name

        # Check if project already exists
        if project_path.exists() and not force:
            raise CreationError(f"Project directory '{project_path}' already exists. Use force=True to overwrite.")

        # Create project directory structure
        project_type_config = config['project_types'][project_type]
        created_dirs = []

        # Create project root
        project_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(project_path))

        # Create required directories
        for dir_path in project_type_config['required_dirs']:
            full_path = project_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(full_path))

        # Create optional directories
        for dir_path in project_type_config.get('optional_dirs', []):
            full_path = project_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(full_path))

        # Create template files
        created_files = []
        template_vars = {
            'project_name': project_name,
            'project_type': project_type,
            'author_name': author_name,
            'description': description,
            'creation_date': datetime.now().strftime('%Y-%m-%d'),
            'year': datetime.now().year
        }

        # Generate standard files
        created_files.extend(_generate_template_files(project_path, template_vars, config))

        # Initialize Git repository if requested
        git_initialized = False
        if git_init:
            try:
                subprocess.run(['git', 'init'], cwd=project_path, check=True, capture_output=True)
                subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
                subprocess.run(['git', 'commit', '-m', f'Initial commit: {project_name}'],
                             cwd=project_path, check=True, capture_output=True)
                git_initialized = True
            except subprocess.CalledProcessError as e:
                # Non-fatal error, just warn
                pass

        return {
            'success': True,
            'message': f"Project '{project_name}' created successfully",
            'data': {
                'project_path': str(project_path),
                'project_type': project_type,
                'created_directories': created_dirs,
                'created_files': created_files,
                'git_initialized': git_initialized
            },
            'errors': [],
            'warnings': []
        }

    except Exception as e:
        return {
            'success': False,
            'message': f"Failed to create project: {str(e)}",
            'data': {},
            'errors': [str(e)],
            'warnings': []
        }


def restructure_project(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Restructure existing project to standard format

    Args:
        payload: Dictionary containing restructuring parameters
            - root (str, optional): Project directory path
            - backup (bool, optional): Create backup before restructuring
            - remove_nonstandard (bool, optional): Remove non-standard directories
            - force (bool, optional): Force restructuring without confirmation
            - target_type (str, optional): Target project type

    Returns:
        Dict containing operation result with success status and details
    """
    try:
        # Set default values
        root = payload.get('root', os.getcwd())
        backup = payload.get('backup', True)
        remove_nonstandard = payload.get('remove_nonstandard', True)
        force = payload.get('force', False)
        target_type = payload.get('target_type')

        project_path = Path(root).resolve()

        if not project_path.exists():
            raise RestructureError(f"Project directory '{project_path}' does not exist")

        # Create backup if requested
        backup_path = None
        if backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{project_path.name}_backup_{timestamp}"
            backup_path = project_path.parent / backup_name
            shutil.copytree(project_path, backup_path)

        # Analyze existing structure
        existing_dirs = [d for d in project_path.iterdir() if d.is_dir()]
        existing_files = [f for f in project_path.iterdir() if f.is_file()]

        # Auto-detect project type if not provided
        if not target_type:
            target_type = _detect_project_type(project_path)

        if not target_type:
            target_type = "general"  # fallback to general type

        config = get_project_config()
        project_type_config = config['project_types'][target_type]

        # Create missing standard directories
        created_dirs = []
        for dir_path in project_type_config['required_dirs']:
            full_path = project_path / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(full_path))

        # Move files to appropriate locations (simplified logic)
        moved_files = []
        # This would be more sophisticated in practice, analyzing file types and content
        # to determine appropriate locations

        # Remove nonstandard directories if requested
        removed_dirs = []
        if remove_nonstandard:
            all_standard_dirs = set(project_type_config['required_dirs'] +
                                  project_type_config.get('optional_dirs', []))

            for existing_dir in existing_dirs:
                if existing_dir.name not in all_standard_dirs and existing_dir.name not in ['.git', '.claude', '.claude-plugin']:
                    shutil.rmtree(existing_dir)
                    removed_dirs.append(str(existing_dir))

        # Update or create project configuration files
        template_vars = {
            'project_name': project_path.name,
            'project_type': target_type,
            'restructure_date': datetime.now().strftime('%Y-%m-%d'),
            'year': datetime.now().year
        }

        _generate_template_files(project_path, template_vars, config, update_existing=True)

        return {
            'success': True,
            'message': 'Project restructured successfully',
            'data': {
                'backup_path': str(backup_path) if backup_path else None,
                'moved_files': moved_files,
                'created_directories': created_dirs,
                'removed_directories': removed_dirs,
                'project_type': target_type
            },
            'errors': [],
            'warnings': [] if not backup_path else [f"Backup created at {backup_path}"]
        }

    except Exception as e:
        return {
            'success': False,
            'message': f"Failed to restructure project: {str(e)}",
            'data': {},
            'errors': [str(e)],
            'warnings': []
        }


def validate_project(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate project structure and provide compliance scoring

    Args:
        payload: Dictionary containing validation parameters
            - root (str, optional): Project directory path
            - fix_issues (bool, optional): Automatically fix issues
            - strict_mode (bool, optional): Enable strict validation

    Returns:
        Dict containing validation result with compliance score and details
    """
    try:
        # Set default values
        root = payload.get('root', os.getcwd())
        fix_issues = payload.get('fix_issues', False)
        strict_mode = payload.get('strict_mode', False)

        project_path = Path(root).resolve()

        if not project_path.exists():
            raise ValidationError(f"Project directory '{project_path}' does not exist")

        # Auto-detect project type
        project_type = _detect_project_type(project_path)
        if not project_type:
            project_type = "general"

        config = get_project_config()
        project_type_config = config['project_types'][project_type]

        # Validate directory structure
        required_dirs = project_type_config['required_dirs']
        optional_dirs = project_type_config.get('optional_dirs', [])
        existing_dirs = [d.name for d in project_path.iterdir() if d.is_dir()]

        missing_dirs = [d for d in required_dirs if d not in existing_dirs]
        extra_dirs = [d for d in existing_dirs if d not in required_dirs + optional_dirs +
                     ['.git', '.claude', '.claude-plugin', '__pycache__']]

        # Validate required files
        required_files = project_type_config['required_files']
        existing_files = [f.name for f in project_path.iterdir() if f.is_file()]

        missing_files = [f for f in required_files if f not in existing_files]
        extra_files = [f for f in existing_files if f not in required_files and not f.startswith('.')]

        # Calculate compliance score
        score_weights = config['validation']['scoring_weights']

        dir_score = len(required_dirs) - len(missing_dirs)
        dir_score = max(0, (dir_score / len(required_dirs)) * score_weights['directories'])

        file_score = len(required_files) - len(missing_files)
        file_score = max(0, (file_score / len(required_files)) * score_weights['required_files'])

        # Basic content quality check (simplified)
        content_score = score_weights['content_quality'] if not missing_files else 0

        # Git integration check
        git_score = 0
        if (project_path / '.git').exists():
            git_score = score_weights['git_integration']

        compliance_score = int(dir_score + file_score + content_score + git_score)

        # Generate issues and suggestions
        issues_found = []
        suggestions = []

        if missing_dirs:
            issues_found.append(f"Missing required directories: {', '.join(missing_dirs)}")
            suggestions.append(f"Create missing directories: {', '.join(missing_dirs)}")

        if missing_files:
            issues_found.append(f"Missing required files: {', '.join(missing_files)}")
            suggestions.append(f"Create missing files: {', '.join(missing_files)}")

        if extra_dirs and strict_mode:
            issues_found.append(f"Extra directories found: {', '.join(extra_dirs[:3])}")
            suggestions.append("Remove extra directories or move to appropriate locations")

        # Auto-fix issues if requested
        fixes_applied = []
        if fix_issues:
            # Create missing directories
            for dir_path in missing_dirs:
                full_path = project_path / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                fixes_applied.append(f"Created directory: {dir_path}")

            # Create missing files
            template_vars = {
                'project_name': project_path.name,
                'project_type': project_type,
                'validation_date': datetime.now().strftime('%Y-%m-%d'),
                'year': datetime.now().year
            }
            created_files = _generate_template_files(project_path, template_vars, config, missing_only=True)
            fixes_applied.extend([f"Created file: {f}" for f in created_files])

        return {
            'success': True,
            'message': 'Validation completed',
            'data': {
                'compliance_score': compliance_score,
                'project_type': project_type,
                'structure_analysis': {
                    'required_dirs_present': [d for d in required_dirs if d in existing_dirs],
                    'required_files_present': [f for f in required_files if f in existing_files],
                    'missing_items': missing_dirs + missing_files,
                    'extra_items': extra_dirs + extra_files
                },
                'issues_found': issues_found,
                'suggestions': suggestions,
                'fixes_applied': fixes_applied
            }
        }

    except Exception as e:
        return {
            'success': False,
            'message': f"Validation failed: {str(e)}",
            'data': {},
            'errors': [str(e)]
        }


def get_project_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report project structure status and comprehensive statistics

    Args:
        payload: Dictionary containing status parameters
            - root (str, optional): Project directory path
            - include_git (bool, optional): Include Git statistics
            - include_file_stats (bool, optional): Include detailed file statistics

    Returns:
        Dict containing comprehensive project status report
    """
    try:
        # Set default values
        root = payload.get('root', os.getcwd())
        include_git = payload.get('include_git', True)
        include_file_stats = payload.get('include_file_stats', True)

        project_path = Path(root).resolve()

        if not project_path.exists():
            raise ValidationError(f"Project directory '{project_path}' does not exist")

        # Get basic project info
        project_name = project_path.name

        # Auto-detect project type
        project_type = _detect_project_type(project_path)
        if not project_type:
            project_type = "general"

        # Get modification time
        last_modified = datetime.fromtimestamp(project_path.stat().st_mtime)

        # Scan directory structure
        total_directories = 0
        total_files = 0
        total_size = 0
        file_breakdown = {}

        for root_dir, dirs, files in os.walk(project_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            relative_path = Path(root_dir).relative_to(project_path)
            dir_key = str(relative_path) + "/"

            total_directories += len(dirs)
            dir_files = len(files)
            total_files += dir_files

            # Calculate directory size
            dir_size = 0
            for file in files:
                file_path = Path(root_dir) / file
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    dir_size += file_size
                    total_size += file_size

            if dir_files > 0:
                file_breakdown[dir_key] = {
                    'files': dir_files,
                    'size_mb': round(dir_size / (1024 * 1024), 1)
                }

        # Get compliance score
        validation_result = validate_project({'root': str(project_path)})
        compliance_score = validation_result['data']['compliance_score'] if validation_result['success'] else 0

        # Get Git info if requested
        git_info = None
        if include_git and (project_path / '.git').exists():
            try:
                # Get commit count
                result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'],
                                      cwd=project_path, capture_output=True, text=True)
                commits = int(result.stdout.strip()) if result.returncode == 0 else 0

                # Get branch count
                result = subprocess.run(['git', 'branch', '--list'],
                                      cwd=project_path, capture_output=True, text=True)
                branches = len(result.stdout.strip().split('\n')) if result.returncode == 0 else 0

                # Get last commit date
                result = subprocess.run(['git', 'log', '-1', '--format=%ci'],
                                      cwd=project_path, capture_output=True, text=True)
                last_commit = result.stdout.strip() if result.returncode == 0 else None

                git_info = {
                    'commits': commits,
                    'branches': branches,
                    'last_commit': last_commit
                }
            except subprocess.CalledProcessError:
                git_info = {'error': 'Failed to get git information'}

        return {
            'success': True,
            'message': 'Status report generated',
            'data': {
                'project_info': {
                    'name': project_name,
                    'path': str(project_path),
                    'type': project_type,
                    'last_modified': last_modified.isoformat()
                },
                'structure_stats': {
                    'total_directories': total_directories,
                    'total_files': total_files,
                    'project_size_mb': round(total_size / (1024 * 1024), 1),
                    'compliance_score': compliance_score
                },
                'file_breakdown': file_breakdown,
                'git_info': git_info
            }
        }

    except Exception as e:
        return {
            'success': False,
            'message': f"Failed to generate status report: {str(e)}",
            'data': {},
            'errors': [str(e)]
        }


# Helper functions

def _detect_project_type(project_path: Path) -> Optional[str]:
    """Auto-detect project type based on existing structure"""
    config = get_project_config()

    # Simple heuristic: check which project type has the most matching directories
    best_match = None
    best_score = 0

    for project_type, type_config in config['project_types'].items():
        required_dirs = type_config['required_dirs']
        existing_dirs = [d.name for d in project_path.iterdir() if d.is_dir()]

        # Count matching directories
        matches = sum(1 for dir_name in required_dirs if dir_name in existing_dirs)
        score = matches / len(required_dirs)

        if score > best_score:
            best_score = score
            best_match = project_type

    return best_match if best_score > 0.3 else None  # Threshold for detection


def _generate_template_files(project_path: Path, template_vars: Dict[str, Any],
                           config: Dict[str, Any], update_existing: bool = False,
                           missing_only: bool = False) -> List[str]:
    """Generate template files for the project"""
    created_files = []

    # Define file templates
    templates = {
        'README.md': f"""# {{{{project_name}}}}

{{{{description}}}}

## Project Type
{{{{project_type}}}}

## Directory Structure

- `claude-code/` - Claude Code conversation history and prompts
- `data/` - Data files (raw and processed)
- `codes/` - Analysis scripts and code
- `paper/` - Paper-related content
- `pre/` - Preliminary work and planning

## Created
- Date: {{{{creation_date}}}}
- Author: {{{{author_name}}}}

---

*Generated by Project Management skill on {{{{creation_date}}}}*
""",
        '.gitignore': """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Data files
*.csv
*.xlsx
*.json
*.xml
data/raw/*
!data/raw/.gitkeep

# Outputs
outputs/
figures/
*.pdf
*.png
*.jpg
*.jpeg

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
.env
config/local.*
""",
        'project.yml': f"""project:
  name: {{{{project_name}}}}
  type: {{{{project_type}}}}
  description: {{{{description}}}}
  created: {{{{creation_date}}}}
  author: {{{{author_name}}}}

directories:
  claude_code: claude-code
  data: data
  codes: codes
  paper: paper
  pre: pre

structure:
  - claude-code
  - data
  - codes
  - paper
  - pre

metadata:
  version: 0.1.0
  last_updated: {{{{creation_date}}}}
""",
        '.project-config.json': f"""{{
  "project_name": "{{{{project_name}}}}",
  "project_type": "{{{{project_type}}}}",
  "created_at": "{{{{creation_date}}}}",
  "author": "{{{{author_name}}}}",
  "description": "{{{{description}}}}",
  "version": "0.1.0",
  "structure_version": "1.0",
  "config": {{
    "backup_enabled": true,
    "auto_validate": true,
    "git_integration": true
  }}
}}"""
    }

    for filename, template in templates.items():
        file_path = project_path / filename

        if missing_only and file_path.exists():
            continue

        if not file_path.exists() or update_existing:
            # Simple template substitution
            content = template
            for var, value in template_vars.items():
                content = content.replace('{{' + var + '}}', str(value))
                content = content.replace('{{ ' + var + ' }}', str(value))

            with open(file_path, 'w') as f:
                f.write(content)
            created_files.append(filename)

    return created_files