# Pre-Push Workflow Guide

## Overview

The pre-push workflow script (`pre_push.py`) automates the process of preparing code for git push. It performs safety checks, code review, generates dev logs, and pushes to git only if all checks pass.

## Quick Start

### Basic Usage

```bash
# Full workflow (recommended)
python pre_push.py

# With custom commit message
python pre_push.py --commit-message "Add feature X"

# With notes for dev log
python pre_push.py --notes "Fixed bug in image generation"
```

## Workflow Steps

The script performs these steps in order:

1. **Git Repository Check** - Verifies git is initialized
2. **Git Status Check** - Checks for uncommitted changes
3. **Syntax Check** - Validates Python syntax
4. **Secret Check** - Scans for potential secrets in code
5. **Code Review** - Performs static analysis
6. **Dev Log Generation** - Creates developer log entry
7. **Stage Changes** - `git add .`
8. **Create Commit** - `git commit`
9. **Push to Remote** - `git push`

## Command Options

### Full Workflow Options

```bash
python pre_push.py [options]
```

**Options:**
- `--skip-review` - Skip code review step
- `--skip-devlog` - Skip dev log generation
- `--dry-run` - Preview without actually pushing
- `--commit-message MESSAGE` - Custom commit message
- `--notes NOTES` - Additional notes for dev log
- `--branch BRANCH` - Branch to push to (default: current branch)

### Partial Workflows

```bash
# Only run code review
python pre_push.py --review-only

# Only generate dev log
python pre_push.py --devlog-only --notes "Session notes"
```

## Code Review

The code review checks for:

- **Syntax Errors** - Python syntax validation
- **Potential Secrets** - API keys, passwords, tokens
- **Common Issues** - Print statements, TODO comments, hardcoded paths
- **Import Issues** - Invalid imports

Review report is saved to `code_review_report.md`

### Review Severity Levels

- **Critical** - Blocks push (syntax errors, secrets)
- **Warning** - Non-blocking (print statements, hardcoded paths)
- **Info** - Informational (TODO comments)

## Dev Log Generation

Dev logs are automatically generated in `devlogs/` folder with:
- Session number (auto-incremented)
- Date and time
- Work completed (extracted from git changes)
- Files changed
- Technical details

### Dev Log Template

```markdown
# Developer's Log - Session XX

**Date:** YYYY-MM-DD
**Time:** HH:MM:SS
**Session:** Session XX
**Developer:** Fyrebug (WPMG)

## Overview
## Objectives
## Work Completed
## Challenges Encountered
## Solutions Implemented
## Notes & Observations
## Next Steps
## Technical Details
```

## Safety Features

### Dry Run Mode

Preview what would happen without actually pushing:

```bash
python pre_push.py --dry-run
```

### Confirmation Prompts

- Code review failures prompt for confirmation
- Critical issues block push by default

### Error Handling

- Graceful failure at each step
- Clear error messages
- Option to continue or abort

## Examples

### Standard Push

```bash
python pre_push.py
```

### Quick Push (Skip Review)

```bash
python pre_push.py --skip-review
```

### Push with Custom Message

```bash
python pre_push.py --commit-message "Implement image generation API"
```

### Generate Dev Log Only

```bash
python pre_push.py --devlog-only --notes "Completed handoff system implementation"
```

## Integration with Git

The script works with your existing git repository:

- Repository: https://github.com/wyldephyre/ECHO
- Automatically detects current branch
- Handles authentication through git credentials

## Troubleshooting

### "Not a git repository"

Initialize git first:
```bash
git init
git remote add origin https://github.com/wyldephyre/ECHO.git
```

### "Git not found"

Install Git: https://git-scm.com/downloads

### Syntax Errors

Fix syntax errors before pushing. The script will show file and line numbers.

### Secret Check Fails

Remove hardcoded secrets. Use `.env` file and `os.getenv()` instead.

### Code Review Fails

Fix critical issues or use `--skip-review` (not recommended).

## Best Practices

1. **Run full workflow** - Don't skip checks unless necessary
2. **Review code report** - Check `code_review_report.md` before pushing
3. **Use meaningful commit messages** - Or let script auto-generate
4. **Add notes to dev log** - Document important decisions
5. **Test with dry-run** - Preview changes before pushing

## Related Files

- `pre_push.py` - Main workflow script
- `code_reviewer.py` - Code review module
- `devlog_generator.py` - Dev log generation
- `code_review_report.md` - Generated review report
- `devlogs/session_XX_devlog.md` - Generated dev logs

---

*For the forgotten 99%, we rise.* 🔥



