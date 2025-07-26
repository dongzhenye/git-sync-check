# git-sync-check

A command-line tool to check if a Git repository is fully synced with its remote, helping you safely delete local repositories without losing uncommitted work or important configuration files.

## Why git-sync-check?

When managing multiple local repositories, it's common to want to clean up old projects. However, before deleting a repository, you need to ensure:
- All changes are committed and pushed
- No valuable local configuration files (like `.env` files with secrets) will be lost
- The local branch is fully synced with remote

This tool provides a comprehensive check for all these concerns in one simple command.

### Real-world Scenarios

1. **Orphaned Local Repository** - No remote configured with local commits
   ```
   ⚠️  No remote repository configured! (2 local commits)
   ```

2. **Database Files** - Local SQLite databases that might contain important data
   ```
   ⚠️  Important config/secret files:
      - addresses.db
   ```

3. **Environment Files** - Configuration files with API keys or secrets
   ```
   ⚠️  Important config/secret files:
      - .env.local
      - .claude/settings.local.json
   ```

4. **Large Node.js Projects** - Smart filtering to avoid false positives
   - Ignores `node_modules/` and build directories
   - Focuses on actual config files, not source code

## Features

- **Uncommitted Changes Detection**: Identifies staged, unstaged, and untracked files
- **Remote Sync Status**: Checks if your local branch is ahead or behind the remote
- **Ignored Files Listing**: Shows all files ignored by `.gitignore` (crucial for finding local configs)
- **Clean Output**: Clear, emoji-enhanced terminal output for easy reading
- **JSON Support**: Machine-readable output for automation

## Quick Start

```bash
# Clone the repository
git clone https://github.com/dongzhenye/git-sync-check.git
cd git-sync-check

# Run directly with Python
python3 git_sync_check.py /path/to/repo

# Or make it executable
chmod +x git_sync_check.py
./git_sync_check.py /path/to/repo
```

## Usage

### Basic Check
```bash
# Check current directory
git-sync-check

# Check specific repository
git-sync-check /path/to/repo
```

### Show Ignored Files
This is especially useful for finding important local configuration files:
```bash
git-sync-check --show-ignored
```

### JSON Output
For scripting and automation:
```bash
git-sync-check --json
```

## Example Output

```
📁 Repository: /Users/example/my-project
============================================================
⚠️  Issues found:
   - Uncommitted changes found
   - Not in sync with remote

🔄 Sync Status:
   Local branch is 2 commits ahead of remote

📝 Uncommitted Changes:
   Modified files:
   src/main.py
   
   Untracked files:
   .env.local
   notes.txt

🚫 Ignored Files: 5 files
   Files ignored by .gitignore:
   - .env
   - .env.local
   - node_modules/
   - *.log
   - .DS_Store

============================================================
⚠️  WARNING: This repository has unsynced changes!
   Review the above before deleting this repository.
```

## Safety First

The tool helps you identify:
1. **Uncommitted work** that would be lost
2. **Unpushed commits** that exist only locally
3. **Ignored files** that might contain important data (API keys, local configs, etc.)

Always review the output carefully before deleting any repository!

## Requirements

- Python 3.6+
- Git command-line tool
- Unix-like environment (Linux, macOS, WSL)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Author

Zhenye Dong ([@dongzhenye](https://github.com/dongzhenye))