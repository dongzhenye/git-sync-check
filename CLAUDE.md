# git-ok - Project Context

## Overview
A tool to check what's not backed up in your Git repository.

## Key Features
- Detect non-Git directories (most critical - no version control at all!)
- Check for uncommitted changes (staged, unstaged, untracked)
- Verify sync status with remote repository
- List all files ignored by .gitignore (especially important for config files like .env)
- Detect orphaned repositories (no remote configured)
- Smart identification of important files (databases, env files, certificates)
- JSON output support for automation

## Technical Details
- Language: Python 3.6+
- No external dependencies (uses only subprocess and standard library)
- Entry point: git_ok.py
- Direct script execution (no installation needed)

## Important File Detection
- **Patterns**: `.env`, `secret`, `credential`, `key`, `password`, `.local`, `config.local`
- **Extensions**: `.db`, `.sqlite`, `.sqlite3`, `.pem`, `.key`, `.cert`, `.crt`, `.pfx`, `.p12`
- **Excluded Dirs**: `node_modules/`, `.next/`, `dist/`, `build/`, `.venv/`, `__pycache__/`, `.cache/`

## Usage Examples
```bash
# Check current directory
python3 git_ok.py

# Check specific repository
python3 git_ok.py /path/to/repo

# Show ignored files
python3 git_ok.py --show-ignored

# Show only important files
python3 git_ok.py --important-only

# JSON output for automation
python3 git_ok.py --json
```

## Project Status
- Core functionality implemented and tested
- Supports non-Git directories (critical for finding unversioned projects)
- Smart filtering to reduce false positives in Node.js projects
- Handles edge cases like orphaned repos and OneDrive paths
- Exit codes: 0 (clean), 1 (git repo with issues), 2 (not a git repo)
- Ready for open-source release