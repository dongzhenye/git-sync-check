# Key Design Decisions

## 1. Single Repository Focus
**Decision**: Check one repository at a time, no batch operations

**Rationale**:
- Each repository requires careful individual review
- Batch operations could lead to accidental data loss
- Keeps the tool simple and predictable
- Users can easily script batch operations if needed: `find . -name .git -type d | xargs -I {} git-ok {}/..`

## 2. Direct Script Execution
**Decision**: No installation required, just run the Python script

**Rationale**:
- Zero friction to start using
- No dependency conflicts
- Easy to audit (single file)

## 3. Non-Git Directory Support
**Decision**: Full support with highest severity warnings

**Context**: Initially overlooked, added after user feedback
**Learning**: The most dangerous case is no version control at all

## 4. Important File Detection
**Decision**: Pattern-based detection with smart filtering

**Detected**:
- Config patterns: `.env`, `secret`, `credential`, `key`, `password`, `.local`
- Database files: `.db`, `.sqlite`, `.sqlite3`
- Certificates: `.pem`, `.key`, `.cert`, `.crt`, `.pfx`, `.p12`

**Filtered out**: `node_modules/`, build directories, common source files

## 5. Read-Only Operation
**Decision**: Never modify files or repository state

**Rationale**:
- Safety first - no accidental commits or pushes
- Users must understand issues before taking action
- Prevents tool from becoming a crutch

## 6. Exit Code Semantics
**Decision**: Different codes for different severities

- `0`: Repository is clean and safe
- `1`: Git repository has issues
- `2`: Not a Git repository (most severe)

**Use case**: Shell scripts can handle different scenarios:
```bash
git-ok || handle_issues $?
```

## 7. No Configuration Files
**Decision**: Convention over configuration

**Rationale**:
- Works the same everywhere
- No hidden surprises
- Learned patterns work well for 90% of cases

## 8. Emoji Usage
**Decision**: Use emojis for visual clarity in terminal output

**Rationale**:
- Quick visual scanning of issues
- Works in modern terminals
- Falls back gracefully in older terminals
- Disabled in JSON output