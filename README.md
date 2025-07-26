# git-ok

A tool to check what's not backed up in your Git repository.

## Why git-ok?

When managing multiple local repositories, it's common to want to clean up old projects. However, before deleting a repository, you need to ensure:
- All changes are committed and pushed
- No valuable local configuration files (like `.env` files with secrets) will be lost
- The local branch is fully synced with remote

This tool provides a comprehensive check for all these concerns in one simple command.

### Real-world Scenarios

1. **Non-Git Directory** - Most critical! No version control at all
   ```
   ❌ NOT A GIT REPOSITORY!
   All 156 files (2.3 MB) are NOT backed up!
   ```

2. **Orphaned Local Repository** - No remote configured with local commits
   ```
   ⚠️  No remote repository configured! (2 local commits)
   ```

3. **Database Files** - Local SQLite databases that might contain important data
   ```
   ⚠️  Important config/secret files:
      - addresses.db
   ```

4. **Environment Files** - Configuration files with API keys or secrets
   ```
   ⚠️  Important config/secret files:
      - .env.local
      - .claude/settings.local.json
   ```

5. **Large Node.js Projects** - Smart filtering to avoid false positives
   - Ignores `node_modules/` and build directories
   - Focuses on actual config files, not source code

## Features

- **Non-Git Directory Detection**: Warns when directories have NO version control at all (most critical!)
- **Uncommitted Changes Detection**: Identifies staged, unstaged, and untracked files
- **Remote Sync Status**: Checks if your local branch is ahead or behind the remote
- **Ignored Files Listing**: Shows all files ignored by `.gitignore` (crucial for finding local configs)
- **Clean Output**: Clear, emoji-enhanced terminal output for easy reading
- **JSON Support**: Machine-readable output for automation

## Quick Start

```bash
# Clone the repository
git clone https://github.com/dongzhenye/git-ok.git
cd git-ok

# Run directly with Python
python3 git_ok.py /path/to/repo

# Or make it executable
chmod +x git_ok.py
./git_ok.py /path/to/repo
```

## Usage

### Basic Check
```bash
# Check current directory
git-ok

# Check specific repository
git-ok /path/to/repo
```

### Show Ignored Files
This is especially useful for finding important local configuration files:
```bash
git-ok --show-ignored
```

### JSON Output
For scripting and automation:
```bash
git-ok --json
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