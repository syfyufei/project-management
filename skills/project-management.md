---
name: project-management
description: Comprehensive project management skill for creating, restructuring, validating, and monitoring research and analysis projects with standardized directory structures
---

# Project Management

## Overview

A TDD-tested project management skill that creates, restructures, validates, and monitors research projects with standardized directory structures. Supports 4 project types: research-project, data-analysis, paper-writing, and general.

## When to Use This Skill

**Triggered when:**
- User requests project creation or management
- User needs to reorganize existing projects
- User wants to validate project structure compliance
- User asks for project status and statistics
- Natural language contains project organization needs

**Test-Driven Pressure Scenarios (TDD Approach):**
- **RED Phase**: Create complex nested projects without skill → observe failed attempts and rationalizations
- **GREEN Phase**: Use skill to handle complex multi-project scenarios efficiently
- **REFACTOR Phase**: Apply skill under pressure with tight deadlines and conflicting requirements

## Tools

### create_project

**Description**: Creates new projects with standardized directory structure based on project type

**Input Structure**:
```json
{
  "project_name": "string (kebab-case, required)",
  "project_type": "string (required, one of: research-project, data-analysis, paper-writing, general)",
  "root": "string (optional, default: current directory)",
  "git_init": "boolean (optional, default: true)",
  "force": "boolean (optional, default: false)",
  "author_name": "string (optional, from config)",
  "description": "string (optional)"
}
```

**Behavior**:
1. Validates project_name format (kebab-case)
2. Validates project_type against allowed values
3. Creates standardized directory structure based on type
4. Generates template files with variable substitution
5. Initializes Git repository if git_init=true
6. Creates project configuration files

**Output Structure**:
```json
{
  "success": true,
  "message": "Project 'ai-ethics-research' created successfully",
  "data": {
    "project_path": "/full/path/to/project",
    "project_type": "research-project",
    "created_directories": ["claude-code", "data", "codes", "paper", "pre"],
    "created_files": ["README.md", ".gitignore", "project.yml", ".project-config.json"],
    "git_initialized": true
  },
  "errors": [],
  "warnings": []
}
```

**Example Usage**:
```
User: "Create a new research project called AI Ethics Research"
Assistant: [Uses create_project with project_name="ai-ethics-research", project_type="research-project"]
```

### restructure_project

**Description**: Restructures existing projects to standard format with backup support

**Input Structure**:
```json
{
  "root": "string (optional, default: current directory)",
  "backup": "boolean (optional, default: true)",
  "remove_nonstandard": "boolean (optional, default: true)",
  "force": "boolean (optional, default: false)",
  "target_type": "string (optional, auto-detect if not provided)"
}
```

**Behavior**:
1. Creates project backup if backup=true
2. Analyzes existing project structure
3. Moves/reorganizes files to standard structure
4. Creates missing standard directories
5. Removes nonstandard directories if remove_nonstandard=true
6. Updates project configuration files

**Output Structure**:
```json
{
  "success": true,
  "message": "Project restructured successfully",
  "data": {
    "backup_path": "/path/to/backup",
    "moved_files": ["old/path → new/path"],
    "created_directories": ["missing/dirs"],
    "removed_directories": ["nonstandard/dirs"],
    "project_type": "research-project"
  }
}
```

**Example Usage**:
```
User: "Restructure my current project to standard format"
Assistant: [Uses restructure_project with backup=true]
```

### validate_project

**Description**: Validates project structure and provides compliance scoring (0-100)

**Input Structure**:
```json
{
  "root": "string (optional, default: current directory)",
  "fix_issues": "boolean (optional, default: false)",
  "strict_mode": "boolean (optional, default: false)"
}
```

**Behavior**:
1. Checks standard directory structure compliance
2. Validates required files exist and are properly formatted
3. Evaluates project structure completeness
4. Calculates compliance score (0-100)
5. Provides detailed fix suggestions
6. Auto-fixes issues if fix_issues=true

**Output Structure**:
```json
{
  "success": true,
  "message": "Validation completed",
  "data": {
    "compliance_score": 85,
    "project_type": "research-project",
    "structure_analysis": {
      "required_dirs_present": ["claude-code", "data", "codes", "paper", "pre"],
      "required_files_present": ["README.md", ".gitignore", "project.yml"],
      "missing_items": [],
      "extra_items": ["temp"]
    },
    "issues_found": ["Extra directory 'temp' found"],
    "suggestions": ["Remove 'temp' directory or move to appropriate location"]
  }
}
```

**Example Usage**:
```
User: "Check if my project follows the standard structure"
Assistant: [Uses validate_project with strict_mode=true]
```

### project_status

**Description**: Reports project structure status and comprehensive statistics

**Input Structure**:
```json
{
  "root": "string (optional, default: current directory)",
  "include_git": "boolean (optional, default: true)",
  "include_file_stats": "boolean (optional, default: true)"
}
```

**Behavior**:
1. Scans project structure and generates metrics
2. Counts files by type and directory
3. Analyzes project metadata from configuration files
4. Tracks file sizes and modification dates
5. Provides git statistics if include_git=true
6. Generates visual status indicators

**Output Structure**:
```json
{
  "success": true,
  "message": "Status report generated",
  "data": {
    "project_info": {
      "name": "ai-ethics-research",
      "path": "/full/path/to/project",
      "type": "research-project",
      "last_modified": "2025-12-11T16:30:00Z"
    },
    "structure_stats": {
      "total_directories": 15,
      "total_files": 42,
      "project_size_mb": 127.5,
      "compliance_score": 92
    },
    "file_breakdown": {
      "data/": {"files": 12, "size_mb": 89.2},
      "codes/": {"files": 18, "size_mb": 2.8},
      "paper/": {"files": 8, "size_mb": 35.5}
    },
    "git_info": {
      "commits": 23,
      "branches": 2,
      "last_commit": "2025-12-11T14:22:15Z"
    }
  }
}
```

**Example Usage**:
```
User: "Show me the current status of my research project"
Assistant: [Uses project_status with include_git=true]
```

## Configuration

**Configuration Options**:
- **default_project_type**: "research-project" - Default type when not specified
- **standard_directories**: ["claude-code", "data", "codes", "paper", "pre"] - Core directory structure
- **template_variables**: Customizable variables for template generation
- **validation_weights**: Scoring weights for compliance calculation
- **backup_location**: ".backup" - Default backup directory for restructure operations

**Project Type Configurations**:
- **research-project**: Includes literature, data processing, manuscript sections
- **data-analysis**: Includes ETL, models, reports, presentations
- **paper-writing**: Includes chapters, sections, bibliography, reviews
- **general**: Flexible structure with basic organization

## Best Practices

**TDD-Tested Guidelines**:
- **Always validate project_name format** before creation
- **Create backups before restructuring** existing projects
- **Use project.yml for metadata** and .project-config.json for tool integration
- **Initialize Git repositories** for version control when creating new projects
- **Run validation before major changes** to ensure structure compliance
- **Monitor compliance scores** to maintain project organization quality

**Pressure-Tested Scenarios**:
- Handles concurrent project operations without conflicts
- Maintains data integrity during restructure operations
- Provides clear error messages with actionable suggestions
- Works efficiently with large projects (>1000 files)
- Recovers gracefully from permission errors and disk space issues

## Common Patterns

### Create Complete Project Workflow
```
1. User: "Create a data analysis project for customer behavior"
2. System: Uses create_project with type="data-analysis"
3. System: Generates standard structure with analysis directories
4. System: Creates templates for data processing and reporting
5. Result: Ready-to-use project structure
```

### Restructure Existing Project
```
1. User: "My project is messy, can you organize it?"
2. System: Uses validate_project to analyze current state
3. System: Uses restructure_project with backup enabled
4. System: Moves files to appropriate standard directories
5. Result: Organized project with backup saved
```

### Validate and Monitor
```
1. User: "Check if our research project meets standards"
2. System: Uses validate_project with strict_mode
3. System: Provides compliance score and detailed report
4. System: Suggests specific improvements
5. User: Applies fixes and re-validates
```

---

*Generated by skill-squared on 2025-12-11 16:16:07 UTC*
*Enhanced with TDD methodology and pressure-tested scenarios*
