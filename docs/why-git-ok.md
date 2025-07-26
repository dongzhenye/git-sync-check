# Why git-ok?

## What We Do
Check if a directory is safe to delete by identifying what's not backed up.

## The Problem
Before deleting a local repository, you need to manually check:
- Is this a Git repository?
- Any uncommitted changes?
- Any unpushed commits?
- Any important ignored files (configs, databases)?

## Our Solution
One command that checks everything and gives a clear answer.

## Design Principles

1. **Check Non-Git Directories Too**  
   The riskiest directories have no version control at all.

2. **Be Explicit**  
   Show exactly what would be lost, don't hide anything.

3. **Stay Read-Only**  
   We check but never modify. Users decide what to do.

4. **Keep It Simple**  
   No configuration, no installation, just works.

## Why "git-ok"?
The simplest name that answers the user's question: "Is this repository OK?"