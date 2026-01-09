# GitHub Repository Setup

## Initial Setup

```bash
cd /root/gafta-guardian

# Initialize git repository
git init

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/gafta-guardian.git

# Add all files (respects .gitignore)
git add .

# Commit
git commit -m "Initial commit: GAFTA Guardian LightRAG system"

# Push to GitHub
git branch -M main
git push -u origin main
```

## What Gets Pushed

✅ **Included**:
- All Python code (`*.py`)
- Docker files (`Dockerfile`, `docker-compose.yml`)
- Shell scripts (`*.sh`)
- Documentation (`*.md`)
- Configuration (`.gitignore`, `.gitattributes`)

❌ **Excluded** (via `.gitignore`):
- `ollama_data/` - Models (40GB+)
- `rag_data/` - Knowledge graph
- `*.pdf` - PDF files
- `demo_files/` - Demo data
- `__pycache__/` - Python cache
- `*.log` - Log files

## Repository Size

- **Code only**: ~50-100 KB
- **With models**: ~40+ GB (models NOT pushed)

## Cloning and Setup

After cloning:

```bash
git clone https://github.com/YOUR_USERNAME/gafta-guardian.git
cd gafta-guardian

# Models must be downloaded separately
bash setup_models.sh

# Start services
docker compose up -d --build
```

## Backup Strategy

### Option 1: Git Only (Recommended)
- Push code to GitHub
- Backup models separately (cloud storage, S3, etc.)
- Backup knowledge graph separately

### Option 2: Git + External Storage
- Code: GitHub
- Models: AWS S3 / Google Cloud Storage / etc.
- Knowledge Graph: Regular backups to cloud storage

### Option 3: Private Repository
- Use GitHub private repo
- Still exclude large files
- Use Git LFS for models (if needed, but expensive)

## Recommended Backup Commands

```bash
# Backup models to cloud storage (example with AWS S3)
aws s3 sync ollama_data/ s3://your-bucket/ollama_data/

# Backup knowledge graph
aws s3 sync rag_data/ s3://your-bucket/rag_data/

# Or use tar + upload
tar -czf ollama_data_backup.tar.gz ollama_data/
tar -czf rag_data_backup.tar.gz rag_data/
# Upload to cloud storage
```

## Restoration from GitHub

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/gafta-guardian.git
cd gafta-guardian

# 2. Restore models (from backup)
tar -xzf ollama_data_backup.tar.gz

# 3. Restore knowledge graph (from backup)
tar -xzf rag_data_backup.tar.gz

# 4. Start services
docker compose up -d --build
```

## Security Considerations

- **Public Repo**: Don't include sensitive data in code
- **Private Repo**: Recommended for production
- **Secrets**: Use environment variables, not hardcoded
- **API Keys**: Never commit to repository

## Continuous Updates

```bash
# After making changes
git add .
git commit -m "Description of changes"
git push
```
