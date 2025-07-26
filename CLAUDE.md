# Git Sync Check - Project Context

## Overview
A command-line tool to check if a local Git repository is fully synced with remote, helping users safely delete local repositories without losing uncommitted work or important ignored files.

## Key Features
- Check for uncommitted changes (staged, unstaged, untracked)
- Verify sync status with remote repository
- List all files ignored by .gitignore (especially important for config files like .env)
- Detect orphaned repositories (no remote configured)
- Smart identification of important files (databases, env files, certificates)
- JSON output support for automation

## Technical Details
- Language: Python 3.6+
- No external dependencies (uses only subprocess and standard library)
- Entry point: git_sync_check.py
- Can be installed as a command-line tool via setup.py

## Important File Detection
- **Patterns**: `.env`, `secret`, `credential`, `key`, `password`, `.local`, `config.local`
- **Extensions**: `.db`, `.sqlite`, `.sqlite3`, `.pem`, `.key`, `.cert`, `.crt`, `.pfx`, `.p12`
- **Excluded Dirs**: `node_modules/`, `.next/`, `dist/`, `build/`, `.venv/`, `__pycache__/`, `.cache/`

## Usage Examples
```bash
# Check current directory
python3 git_sync_check.py

# Check specific repository
python3 git_sync_check.py /path/to/repo

# Show ignored files
python3 git_sync_check.py --show-ignored

# Show only important files
python3 git_sync_check.py --important-only

# JSON output for automation
python3 git_sync_check.py --json
```

## Project Status
- Core functionality implemented and tested
- Smart filtering to reduce false positives in Node.js projects
- Handles edge cases like orphaned repos and OneDrive paths
- Ready for open-source release