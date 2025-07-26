# Documentation

## [Why git-ok?](./why-git-ok.md)
What git-ok does and why it exists.

## [Key Decisions](./key-decisions.md)
Design choices and their rationale:
- Why single repository focus (no batch operations)
- Why support non-Git directories
- Exit code semantics
- Read-only operation principle

## [Naming Decision](./naming-decision.md)
How we arrived at the name "git-ok" from "git-sync-check".

## Key Learning

The most important lesson: **Always check if it's a Git repository first**. 

Our initial version only worked with Git repositories, missing the most critical case - directories with no version control at all. This oversight was caught by user feedback and transformed how we think about the tool.