# Branch Protection Strategy

This document outlines the recommended branch protection rules for this repository.

## GitHub Branch Protection Settings

### For `main` Branch

Navigate to: **Settings → Branches → Add branch protection rule**

**Branch name pattern:** `main`

**Protection Rules:**

- ✅ Require a pull request before merging
  - ✅ Require approvals: `1`
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (optional, if CODEOWNERS file exists)
- ✅ Require status checks to pass before merging

  - ✅ Require branches to be up to date before merging
  - **Status checks to require:**
    - `backend-tests` (if CI/CD is set up)
    - `backend-lint`
    - `frontend-tests`
    - `frontend-lint`

- ✅ Require conversation resolution before merging

- ✅ Require signed commits (recommended for production)

- ✅ Include administrators (enforce rules for all)

- ✅ Restrict who can push to matching branches

  - Only allow merges from: `dev` and `release/*` branches

- ✅ Do not allow bypassing the above settings

### For `dev` Branch

**Branch name pattern:** `dev`

**Protection Rules:**

- ✅ Require a pull request before merging
  - ✅ Require approvals: `1` (can be 0 for solo projects)
- ✅ Require status checks to pass before merging

  - **Status checks to require:**
    - `backend-tests`
    - `backend-lint`

- ✅ Require conversation resolution before merging

- ⚠️ Allow force pushes (for maintainers only, if needed)

## Setting Up CI/CD (Optional)

To enforce automated checks, create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
    branches: [dev, main]
  push:
    branches: [dev, main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Run tests
        run: cd backend && make test

  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Run lint
        run: cd backend && make lint
```

## CODEOWNERS (Optional)

Create `.github/CODEOWNERS` to automatically request reviews:

```
# Default owners for everything
* @namanag97

# Backend code
/backend/ @namanag97

# Frontend code
/frontend/ @namanag97

# Documentation
/docs/ @namanag97
*.md @namanag97
```

## Quick Setup Commands

```bash
# Configure commit message template locally
git config commit.template .gitmessage

# Set default branch to dev for new work
git config branch.autoSetupMerge always

# Set up pre-commit hooks (optional)
pre-commit install
```

## Migration Plan

If you need to clean up your current branches:

```bash
# Ensure dev branch exists and is up to date
git checkout -b dev
git push origin dev

# Set dev as default branch on GitHub:
# Settings → Branches → Default branch → Change to 'dev'

# Protect branches as described above
```

---

**Note:** These settings should be configured in your GitHub repository settings to enforce the workflow automatically.
