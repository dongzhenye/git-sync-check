#!/usr/bin/env python3
"""
git-ok - A tool to check what's not backed up in your Git repository.

Ensure everything important is committed, pushed, or identified before removing local repos.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


class GitSyncChecker:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).expanduser().resolve()
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Path does not exist: {self.repo_path}")
        self.is_git = self.is_git_repo()
    
    def is_git_repo(self) -> bool:
        """Check if the directory is a git repository."""
        return (self.repo_path / ".git").exists()
    
    def get_directory_stats(self) -> Tuple[int, int]:
        """Get file count and total size for non-git directory."""
        file_count = 0
        total_size = 0
        
        for path in self.repo_path.rglob('*'):
            if path.is_file():
                file_count += 1
                try:
                    total_size += path.stat().st_size
                except:
                    pass
        
        return file_count, total_size
    
    def format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def run_git_command(self, args: List[str]) -> Tuple[int, str, str]:
        """Run a git command and return exit code, stdout, and stderr."""
        cmd = ["git", "-C", str(self.repo_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    
    def check_uncommitted_changes(self) -> Tuple[bool, str]:
        """Check for uncommitted changes including untracked files."""
        # Check for staged changes
        code, staged, _ = self.run_git_command(["diff", "--cached", "--name-only"])
        
        # Check for unstaged changes
        code, unstaged, _ = self.run_git_command(["diff", "--name-only"])
        
        # Check for untracked files
        code, untracked, _ = self.run_git_command(["ls-files", "--others", "--exclude-standard"])
        
        has_changes = bool(staged.strip() or unstaged.strip() or untracked.strip())
        
        details = []
        if staged.strip():
            details.append(f"Staged files:\n{staged}")
        if unstaged.strip():
            details.append(f"Modified files:\n{unstaged}")
        if untracked.strip():
            details.append(f"Untracked files:\n{untracked}")
        
        return has_changes, "\n".join(details)
    
    def check_stash(self) -> Tuple[bool, str]:
        """Check if there are stashed changes."""
        code, stash_list, _ = self.run_git_command(["stash", "list"])
        stash_count = len(stash_list.strip().splitlines()) if stash_list.strip() else 0
        
        if stash_count > 0:
            return True, f"{stash_count} stashed changes"
        return False, ""
    
    def check_merge_rebase_state(self) -> Tuple[bool, str]:
        """Check if repository is in the middle of a merge or rebase."""
        git_dir = self.repo_path / ".git"
        
        # Check for merge in progress
        if (git_dir / "MERGE_HEAD").exists():
            return True, "Merge in progress"
        
        # Check for rebase in progress
        if (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists():
            return True, "Rebase in progress"
        
        # Check for cherry-pick in progress
        if (git_dir / "CHERRY_PICK_HEAD").exists():
            return True, "Cherry-pick in progress"
        
        return False, ""
    
    def check_remote_sync(self) -> Tuple[bool, str]:
        """Check if local branch is in sync with remote."""
        # 1. Check if there are any remotes configured
        code, remotes, _ = self.run_git_command(["remote"])
        if not remotes.strip():
            # No remotes - check repository state
            code, commits, _ = self.run_git_command(["rev-list", "--count", "HEAD"])
            try:
                commit_count = int(commits.strip())
            except:
                commit_count = 0
            
            if commit_count > 0:
                return False, f"⚠️  No remote repository configured! ({commit_count} local commits will be lost)"
            else:
                return False, "⚠️  Empty repository with no remote configured"
        
        # 2. Fetch latest remote info (dry-run to not modify local)
        self.run_git_command(["fetch", "--dry-run"])
        
        # 3. Get current branch
        code, branch, _ = self.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch.strip()
        
        if not branch or branch == "HEAD":
            return False, "⚠️  Not on any branch (detached HEAD state)"
        
        # 4. Check if branch has upstream
        code, upstream, _ = self.run_git_command(["rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"])
        if code != 0:
            # No upstream - check if branch exists on remote
            code, remote_branches, _ = self.run_git_command(["branch", "-r"])
            if any(f"/{branch}" in line for line in remote_branches.splitlines()):
                return False, f"⚠️  Branch '{branch}' exists on remote but upstream is not set\n   Fix: git branch --set-upstream-to=origin/{branch}"
            else:
                # Check if this is the only branch
                code, local_branches, _ = self.run_git_command(["branch"])
                if len(local_branches.strip().splitlines()) == 1:
                    return False, f"⚠️  Branch '{branch}' not pushed to remote yet"
                else:
                    return False, f"⚠️  Branch '{branch}' has no remote tracking branch"
        
        # 5. Compare local and remote
        upstream = upstream.strip()  # Remove any whitespace
        code, ahead, _ = self.run_git_command(["rev-list", "--count", f"{upstream}..{branch}"])
        code2, behind, _ = self.run_git_command(["rev-list", "--count", f"{branch}..{upstream}"])
        
        if code != 0 or code2 != 0:
            return False, "⚠️  Could not compare with remote branch"
        
        try:
            ahead = int(ahead.strip()) if ahead.strip() else 0
            behind = int(behind.strip()) if behind.strip() else 0
        except ValueError:
            return False, "⚠️  Could not compare with remote branch"
        
        # 6. Determine sync status
        if ahead == 0 and behind == 0:
            return True, "✅ Local branch is in sync with remote"
        elif ahead > 0 and behind > 0:
            return False, f"⚠️  Diverged: {ahead} commits ahead, {behind} commits behind remote"
        elif ahead > 0:
            return False, f"⚠️  Local branch is {ahead} commits ahead of remote (need to push)"
        else:  # behind > 0
            return False, f"⚠️  Local branch is {behind} commits behind remote (need to pull)"
    
    def list_ignored_files(self) -> List[str]:
        """List all files ignored by .gitignore."""
        # Use git ls-files to get all ignored files efficiently
        code, all_ignored, _ = self.run_git_command(["ls-files", "--others", "--ignored", "--exclude-standard"])
        
        # Filter out directories from the output
        ignored_files = []
        for file in all_ignored.splitlines():
            if file and not file.endswith('/'):
                ignored_files.append(file)
        
        return sorted(set(ignored_files))
    
    def full_check(self) -> dict:
        """Perform a full sync check and return results."""
        results = {
            "repo_path": str(self.repo_path),
            "is_git": self.is_git,
            "is_clean": True,
            "issues": []
        }
        
        # Handle non-git directory - most severe case
        if not self.is_git:
            results["is_clean"] = False
            results["issues"].append("Not a Git repository")
            file_count, total_size = self.get_directory_stats()
            results["file_count"] = file_count
            results["total_size"] = total_size
            results["total_size_human"] = self.format_size(total_size)
            return results
        
        # 1. Check working directory state
        has_changes, changes_detail = self.check_uncommitted_changes()
        if has_changes:
            results["is_clean"] = False
            results["issues"].append("Uncommitted changes found")
            results["uncommitted_changes"] = changes_detail
        
        # 2. Check for stashed changes
        has_stash, stash_detail = self.check_stash()
        if has_stash:
            results["is_clean"] = False
            results["issues"].append("Stashed changes exist")
            results["stash_info"] = stash_detail
        
        # 3. Check for merge/rebase in progress
        in_progress, progress_detail = self.check_merge_rebase_state()
        if in_progress:
            results["is_clean"] = False
            results["issues"].append(progress_detail)
            results["operation_in_progress"] = progress_detail
        
        # 4. Check remote sync status
        is_synced, sync_detail = self.check_remote_sync()
        if not is_synced:
            results["is_clean"] = False
            results["issues"].append("Not in sync with remote")
            results["sync_status"] = sync_detail
        else:
            results["sync_status"] = sync_detail
        
        # List ignored files
        ignored_files = self.list_ignored_files()
        results["ignored_files"] = ignored_files
        results["ignored_count"] = len(ignored_files)
        
        # Identify important ignored files
        important_patterns = ['.env', 'secret', 'credential', 'key', 'password', '.local', 'config.local']
        important_extensions = ['.db', '.sqlite', '.sqlite3', '.pem', '.key', '.cert', '.crt', '.pfx', '.p12']
        exclude_dirs = ['node_modules/', '.next/', 'dist/', 'build/', '.venv/', '__pycache__/', '.cache/']
        
        important_files = []
        for f in ignored_files:
            # Skip files in excluded directories
            if any(f.startswith(d) or f'/{d}' in f for d in exclude_dirs):
                continue
            # Check if file matches important patterns or extensions
            file_lower = f.lower()
            
            # Check for important extensions
            if any(f.endswith(ext) for ext in important_extensions):
                important_files.append(f)
                continue
            
            # Check for important patterns
            if any(p in file_lower for p in important_patterns):
                # Additional filtering for common false positives
                if f.endswith('.py') or f.endswith('.js') or f.endswith('.ts') or f.endswith('.map'):
                    # Only include source files if they have very specific names
                    if any(f.endswith(p) for p in ['.env.py', '.env.js', 'secrets.py', 'secrets.js']):
                        important_files.append(f)
                else:
                    important_files.append(f)
        
        if important_files:
            results["important_ignored_files"] = important_files
            results["important_ignored_count"] = len(important_files)
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Check what's not backed up in your Git repository."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the git repository (default: current directory)"
    )
    parser.add_argument(
        "--show-ignored",
        action="store_true",
        help="Show list of ignored files"
    )
    parser.add_argument(
        "--important-only",
        action="store_true",
        help="Show only important ignored files (config, secrets, etc.)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    try:
        checker = GitSyncChecker(args.path)
        results = checker.full_check()
        
        if args.json:
            import json
            print(json.dumps(results, indent=2))
        else:
            # Pretty print results
            if not results.get("is_git", True):
                # Special handling for non-git directories
                print(f"\n📁 Directory: {results['repo_path']}")
                print("=" * 60)
                print("❌ NOT A GIT REPOSITORY!")
                print(f"\n⚠️  This directory has no version control.")
                print(f"   All {results['file_count']} files ({results['total_size_human']}) are NOT backed up!")
                print(f"\n💡 To initialize Git: git init")
                print("=" * 60)
                print("\n⚠️  CRITICAL: This directory has no backup whatsoever!")
                print("   Any file deletion or disk failure means permanent data loss.")
            else:
                # Normal git repository output
                print(f"\n📁 Repository: {results['repo_path']}")
                print("=" * 60)
                
                if results["is_clean"]:
                    print("✅ Repository is clean and synced!")
                else:
                    print("⚠️  Issues found:")
                    for issue in results["issues"]:
                        print(f"   - {issue}")
                
                print(f"\n🔄 Sync Status:")
                print(f"   {results['sync_status']}")
            
            if "uncommitted_changes" in results:
                print(f"\n📝 Uncommitted Changes:")
                for line in results["uncommitted_changes"].splitlines():
                    print(f"   {line}")
            
            if "stash_info" in results:
                print(f"\n📦 Stash: {results['stash_info']}")
            
            if "operation_in_progress" in results:
                print(f"\n⚡ Operation: {results['operation_in_progress']}")
            
            if results.get("is_git", True):
                print(f"\n🚫 Ignored Files: {results['ignored_count']} files")
                
                # Show important ignored files if found
                if "important_ignored_files" in results and results["important_ignored_files"]:
                    print(f"   ⚠️  Found {results['important_ignored_count']} important config/secret files")
            
            if args.important_only and "important_ignored_files" in results:
                print("   Important files that would be lost:")
                for file in results["important_ignored_files"]:
                    print(f"   ⚠️  - {file}")
            elif args.show_ignored and results["ignored_files"]:
                print("   Files ignored by .gitignore:")
                
                # Show important files first if any
                if "important_ignored_files" in results:
                    print("   ⚠️  Important config/secret files:")
                    for file in results["important_ignored_files"][:10]:
                        print(f"      - {file}")
                    if len(results["important_ignored_files"]) > 10:
                        print(f"      ... and {len(results['important_ignored_files']) - 10} more important files")
                    print()
                
                # Show other files
                other_files = [f for f in results["ignored_files"] if f not in results.get("important_ignored_files", [])]
                if other_files:
                    print("   📄 Other ignored files:")
                    for file in other_files[:20]:
                        print(f"      - {file}")
                    if len(other_files) > 20:
                        print(f"      ... and {len(other_files) - 20} more")
            
            print("\n" + "=" * 60)
            
            # Safety reminder
            if not results["is_clean"]:
                if not results.get("is_git", True):
                    sys.exit(2)  # Special exit code for non-git directories
                else:
                    print("⚠️  WARNING: This repository has unsynced changes!")
                    print("   Review the above before deleting this repository.")
                    sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()