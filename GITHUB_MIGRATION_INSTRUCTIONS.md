# GitHub Migration Instructions - Second Project

## Context: What We Just Did

We successfully migrated the **Echo Bot** project from your old inaccessible GitHub account to the new **wyldephyre** organization:

- **Old Repository:** `https://github.com/WPMG99/Echo` (inaccessible)
- **New Repository:** `https://github.com/wyldephyre/ECHO.git` ✅
- **Status:** Successfully migrated, committed, and pushed

## Current Situation

You have **3 projects** total that need migration:
1. ✅ **Echo Bot** - COMPLETED (local Windows project)
2. ⏳ **Second Local Project** - PENDING (this workspace)
3. ⏳ **WSL Project** - PENDING (Linux project in WSL)

## Migration Steps for This Project

### Step 1: Verify Current State

Check if this project is already a git repository:

```bash
git status
```

If you see "fatal: not a git repository", you'll need to initialize it first.

### Step 2: Create New GitHub Repository

1. Go to: https://github.com/wyldephyre
2. Click **"New repository"**
3. Name it appropriately (e.g., `ProjectName` or `project-name`)
4. **DO NOT** initialize with README, .gitignore, or license
5. Click **"Create repository"**
6. Copy the repository URL (e.g., `https://github.com/wyldephyre/ProjectName.git`)

### Step 3: Initialize Git (If Needed)

If this project isn't a git repository yet:

```bash
git init
```

### Step 4: Update or Set Remote

**If git repo already exists with old remote:**
```bash
# Check current remote
git remote -v

# Update to new repository
git remote set-url origin https://github.com/wyldephyre/YourProjectName.git

# Verify
git remote -v
```

**If no remote exists:**
```bash
git remote add origin https://github.com/wyldephyre/YourProjectName.git
```

### Step 5: Update .gitignore (Important!)

Make sure your `.gitignore` excludes Cursor/Factory files:

```gitignore
# Cursor & Factory AI (local IDE files - DO NOT COMMIT)
.cursor/
.factory/
```

If `.gitignore` doesn't exist, create it with at minimum:
- `.env` files (if you have them)
- `.cursor/` directory
- `.factory/` directory
- Language-specific ignores (node_modules, __pycache__, etc.)

### Step 6: Stage and Commit All Code

```bash
# Stage all files
git add .

# Check what will be committed
git status

# Create initial commit
git commit -m "Initial commit: Migration to wyldephyre organization"
```

### Step 7: Push to GitHub

```bash
# Push to master branch (or main if that's what you use)
git push -u origin master

# OR if your default branch is main:
git push -u origin main
```

**If you get authentication errors:**
- Use a GitHub Personal Access Token (Settings → Developer settings → Personal access tokens)
- Or use: `gh auth login` if GitHub CLI is installed
- Or configure credential helper: `git config --global credential.helper manager-core`

### Step 8: Verify Success

```bash
# Check remote connection
git remote -v

# Verify push succeeded
git ls-remote origin

# Check status
git status
```

## Quick Reference Commands

```bash
# Check current state
git status
git remote -v
git branch

# Update remote
git remote set-url origin https://github.com/wyldephyre/YourProjectName.git

# Commit and push
git add .
git commit -m "Initial commit: Migration to wyldephyre organization"
git push -u origin master
```

## Troubleshooting

### "Permission denied" or "Authentication failed"
- Generate a Personal Access Token at: https://github.com/settings/tokens
- Use the token as your password when pushing
- Or set up GitHub CLI: `gh auth login`

### "Repository not found"
- Verify the repository name matches exactly
- Check you're signed in to the correct GitHub account
- Ensure the repository exists on GitHub

### "Branch 'master' does not exist" or "Branch 'main' does not exist"
- Check which branch you're on: `git branch`
- Create the branch if needed: `git checkout -b master` or `git checkout -b main`
- Or push to the correct branch name

## After Migration

Once this project is migrated:
1. ✅ Verify code is visible on GitHub
2. ✅ Test that Cursor AI can access the repository
3. ✅ Continue with WSL project migration

## Notes

- **Your code is safe locally** - migration doesn't delete anything
- **Old repository URLs** in documentation may need updating
- **API keys and .env files** should never be committed (already in .gitignore)
- **Cursor/Factory files** are now excluded from git

---

**For the forgotten 99%, we rise.** 🔥

*Migration completed: [Date]*
*Next: WSL project migration*

