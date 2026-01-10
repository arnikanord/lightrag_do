#!/bin/bash
# Git commit and push script for LightRAG fixes
# Usage: bash COMMIT_AND_PUSH.sh YOUR_GITHUB_TOKEN

set -e

TOKEN="${1:-YOUR_TOKEN_HERE}"

if [ "$TOKEN" = "YOUR_TOKEN_HERE" ] || [ -z "$TOKEN" ]; then
    echo "Error: Please provide your GitHub Personal Access Token"
    echo "Usage: bash COMMIT_AND_PUSH.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "To create a token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Generate new token (classic) with 'repo' scope"
    echo "3. Copy the token and use it as argument"
    exit 1
fi

cd /root/lightrag_do

echo "=== Staging changes ==="
git add docker-compose.yml \
        lightrag_api/static/index.html \
        UI_FIXES.md \
        TROUBLESHOOTING.md \
        ACCESS_COMMANDS.md \
        QUICK_RESTORE_GUIDE.md \
        README.md \
        .gitignore

echo "=== Committing changes ==="
git commit -m "Fix UI health check and add comprehensive troubleshooting documentation

- Fixed API_URL in HTML to use window.location.origin (removes hardcoded IP)
- Updated health check condition to allow healthy status when API is healthy  
- Fixed docker-compose.yml GPU configuration for docker-compose 1.29.2
- Added TROUBLESHOOTING.md with common issues and solutions
- Added UI_FIXES.md documenting the fixes applied
- Added ACCESS_COMMANDS.md with complete API usage examples
- Updated QUICK_RESTORE_GUIDE.md with fixes and troubleshooting
- Updated README.md with links to new documentation
- Added .gitignore for backup files"

echo "=== Pushing to GitHub ==="
git push https://${TOKEN}@github.com/arnikanord/lightrag_do.git main

echo "=== Done! ==="
echo "Changes pushed successfully to: https://github.com/arnikanord/lightrag_do"
