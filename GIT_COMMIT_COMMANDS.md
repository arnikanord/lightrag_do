# Git Commit and Push Commands

## Option 1: Using Personal Access Token (HTTPS)

```bash
cd /root/lightrag_do

# Configure git user (if not already done)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Stage all changes
git add docker-compose.yml lightrag_api/static/index.html UI_FIXES.md TROUBLESHOOTING.md ACCESS_COMMANDS.md QUICK_RESTORE_GUIDE.md README.md

# Commit changes
git commit -m "Fix UI health check and add comprehensive troubleshooting documentation

- Fixed API_URL in HTML to use window.location.origin (removes hardcoded IP)
- Updated health check condition to allow healthy status when API is healthy
- Fixed docker-compose.yml GPU configuration for docker-compose 1.29.2
- Added TROUBLESHOOTING.md with common issues and solutions
- Added UI_FIXES.md documenting the fixes applied
- Added ACCESS_COMMANDS.md with complete API usage examples
- Updated QUICK_RESTORE_GUIDE.md with fixes and troubleshooting
- Updated README.md with links to new documentation"

# Push to GitHub (replace YOUR_TOKEN with your GitHub Personal Access Token)
git push https://YOUR_TOKEN@github.com/arnikanord/lightrag_do.git main
```

## Option 2: Using SSH Key

```bash
cd /root/lightrag_do

# Stage all changes
git add docker-compose.yml lightrag_api/static/index.html UI_FIXES.md TROUBLESHOOTING.md ACCESS_COMMANDS.md QUICK_RESTORE_GUIDE.md README.md

# Commit changes
git commit -m "Fix UI health check and add comprehensive troubleshooting documentation

- Fixed API_URL in HTML to use window.location.origin (removes hardcoded IP)
- Updated health check condition to allow healthy status when API is healthy
- Fixed docker-compose.yml GPU configuration for docker-compose 1.29.2
- Added TROUBLESHOOTING.md with common issues and solutions
- Added UI_FIXES.md documenting the fixes applied
- Added ACCESS_COMMANDS.md with complete API usage examples
- Updated QUICK_RESTORE_GUIDE.md with fixes and troubleshooting
- Updated README.md with links to new documentation"

# Push to GitHub (requires SSH key to be set up)
git push git@github.com:arnikanord/lightrag_do.git main
```

## Option 3: Using GitHub CLI (gh)

```bash
cd /root/lightrag_do

# Stage all changes
git add docker-compose.yml lightrag_api/static/index.html UI_FIXES.md TROUBLESHOOTING.md ACCESS_COMMANDS.md QUICK_RESTORE_GUIDE.md README.md

# Commit changes
git commit -m "Fix UI health check and add comprehensive troubleshooting documentation

- Fixed API_URL in HTML to use window.location.origin (removes hardcoded IP)
- Updated health check condition to allow healthy status when API is healthy
- Fixed docker-compose.yml GPU configuration for docker-compose 1.29.2
- Added TROUBLESHOOTING.md with common issues and solutions
- Added UI_FIXES.md documenting the fixes applied
- Added ACCESS_COMMANDS.md with complete API usage examples
- Updated QUICK_RESTORE_GUIDE.md with fixes and troubleshooting
- Updated README.md with links to new documentation"

# Authenticate and push (gh will prompt for authentication)
gh auth login
git push origin main
```

## Creating a GitHub Personal Access Token

If you need to create a token:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name (e.g., "lightrag-do-push")
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token (you won't see it again!)
7. Use it in the push command: `git push https://YOUR_TOKEN@github.com/arnikanord/lightrag_do.git main`

## Verify Changes Before Pushing

```bash
# Review what will be committed
git status
git diff --staged

# View commit message
git log -1 --stat
```
