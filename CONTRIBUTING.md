# Contributing to Process Mining SaaS

Thank you for contributing! This document outlines our git workflow and development practices.

## Branch Strategy

We use a **two-branch workflow** for clean separation of development and production code:

### Main Branches

- **`main`** - Production-ready code only
  - Always deployable
  - Requires PR review
  - Protected branch (no direct commits)
- **`dev`** - Active development branch
  - Integration branch for features
  - Should be stable but may contain work-in-progress
  - Default branch for PRs

### Feature Branches

Create feature branches from `dev`:

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

**Naming conventions:**

- `feature/` - New features (e.g., `feature/process-dashboard`)
- `fix/` - Bug fixes (e.g., `fix/conformance-calculation`)
- `refactor/` - Code refactoring (e.g., `refactor/simplify-mining-service`)
- `docs/` - Documentation updates (e.g., `docs/api-setup-guide`)
- `chore/` - Maintenance tasks (e.g., `chore/update-dependencies`)

## Workflow

### 1. Development Workflow

````bash
# Start from dev
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/my-feature

# Make changes, commit regularly
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/my-feature

# Open PR to dev (not main!)
```git

### 2. Pull Request Process

**All PRs should target the `dev` branch** unless you're doing a release.

**PR Checklist:**

- [ ] Code follows project style guidelines
- [ ] Tests pass (`make test` in backend)
- [ ] Linting passes (`make lint` in backend)
- [ ] Documentation updated if needed
- [ ] PR title follows conventional commits format

**PR Review:**

- At least one approval required
- Address all comments
- Keep PRs focused and small when possible

### 3. Release Workflow

When `dev` is ready for production:

```bash
# Create release PR from dev to main
git checkout main
git pull origin main
git checkout -b release/v1.x.x

# Merge dev into release branch
git merge dev

# Update version numbers, CHANGELOG, etc.
# Push and create PR to main
git push origin release/v1.x.x
````

After merging to `main`:

- Tag the release: `git tag -a v1.x.x -m "Release v1.x.x"`
- Push tags: `git push origin v1.x.x`

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring (no functional changes)
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `perf`: Performance improvements
- `style`: Code style/formatting changes

**Examples:**

```
feat(processes): add conformance checking endpoint

fix(mining): resolve null pointer in event log parsing

refactor(services): simplify discovery service logic

docs(readme): update installation instructions
```

## Code Quality Standards

### Backend (Python)

```bash
# Run all checks
make check

# Individual tools
make lint      # Ruff linting
make typecheck # mypy type checking
make test      # pytest
```

**Requirements:**

- All linting errors must be resolved
- Type hints required for public functions
- Test coverage for new features
- Follow domain-driven design patterns

### Frontend (TypeScript/React)

```bash
# Run checks
npm run lint
npm run typecheck
npm run test
```

**Requirements:**

- ESLint compliance
- TypeScript strict mode
- Component tests for UI components

## Development Setup

### First Time Setup

```bash
# Backend
cd backend
make install
make dev  # Starts development server

# Frontend
cd frontend
npm install
npm run dev
```

### Working with the Monorepo

- Backend: `/backend` - FastAPI + PM4Py
- Frontend: `/frontend` - NX monorepo with React
- SDK: `/sdk` - TypeScript SDK (auto-generated)
- Docs: `/docs` - Technical documentation

## Getting Help

- Check existing issues and PRs
- Read the documentation in `/docs`
- Ask questions in PR comments
- Review `README.md` for project overview

## Branch Protection Rules

### `main` Branch

- Require PR review before merging
- Require status checks to pass
- No direct commits
- Only merge from `dev` or `release/*` branches

### `dev` Branch

- Require PR review (recommended)
- Require tests to pass
- Can be reset if needed (communicate with team)

---

**Key Principle:** All feature work goes through `dev` first. Only stable, tested code makes it to `main`.
