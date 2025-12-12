---
description: Restructure existing project to standard format with backup
---

# Restructure

This command restructures existing projects to follow standard format with backup support.

Parameters:
- root (optional): Project directory (default: current)
- backup (optional): Create backup before restructuring (default: true)
- remove_nonstandard (optional): Remove non-standard directories (default: true)
- force (optional): Force restructuring without confirmation (default: false)
- target_type (optional): Target project type (auto-detect if not provided)

The command will:
1. Create backup if enabled
2. Analyze existing structure
3. Move/reorganize files to standard structure
4. Create missing standard directories
5. Remove nonstandard directories if enabled
6. Update project configuration files
7. Generate restructure report

## Usage

This command should:

1. Process the user's request
2. Perform necessary operations
3. Return results to the user

## Example

**User request**:
```
[Example request]
```

**Expected behavior**:
```
[Expected behavior description]
```
