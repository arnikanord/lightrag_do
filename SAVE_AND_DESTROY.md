# Save Implementation & Destroy Droplet - Quick Guide

## ⚡ Quick Actions (Before Destroying)

### 1. Save Code to GitHub (5 minutes)

```bash
cd /root/gafta-guardian

# Initialize git (if not already)
git init

# Add remote (create repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/gafta-guardian.git

# Add all code files
git add .

# Commit
git commit -m "Save GAFTA Guardian implementation"

# Push
git branch -M main
git push -u origin main
```

**What gets pushed**: All code, configs, docs (~100KB)
**What doesn't**: Models (40GB), knowledge graph data

### 2. Backup Models & Data (Optional but Recommended)

```bash
# Backup models (40GB+ - takes time!)
tar -czf ollama_data_backup.tar.gz ollama_data/

# Backup knowledge graph
tar -czf rag_data_backup.tar.gz rag_data/

# Upload to cloud storage (AWS S3, Google Cloud, etc.)
# Example with AWS CLI:
aws s3 cp ollama_data_backup.tar.gz s3://your-bucket/
aws s3 cp rag_data_backup.tar.gz s3://your-bucket/
```

**Note**: Models can be re-downloaded, but backup saves time.

### 3. Stop Services

```bash
docker compose down
```

### 4. Destroy Droplet

- Go to your cloud provider dashboard
- Stop/Delete the droplet
- **Cost saved**: $3/hour = $72/day = $2,160/month

## 🔄 Restoration (When Needed)

### Option A: Fresh Setup (Models Re-download)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/gafta-guardian.git
cd gafta-guardian

# 2. Setup server (see SETUP_GUIDE.md)
sudo bash fix_nvidia_driver.sh
sudo reboot

# 3. Download models (40GB+ - takes 1-2 hours)
bash setup_models.sh

# 4. Start services
docker compose up -d --build
```

### Option B: Restore from Backup (Faster)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/gafta-guardian.git
cd gafta-guardian

# 2. Download backups from cloud storage
aws s3 cp s3://your-bucket/ollama_data_backup.tar.gz .
aws s3 cp s3://your-bucket/rag_data_backup.tar.gz .

# 3. Extract backups
tar -xzf ollama_data_backup.tar.gz
tar -xzf rag_data_backup.tar.gz

# 4. Start services
docker compose up -d --build
```

## 📋 Pre-Destroy Checklist

- [ ] Code pushed to GitHub
- [ ] Models backed up (optional)
- [ ] Knowledge graph backed up (optional)
- [ ] Documentation reviewed
- [ ] Services stopped
- [ ] Droplet destroyed

## 💡 Cost Savings

- **Running**: $3/hour = $72/day
- **Stopped**: $0/hour
- **Monthly savings**: ~$2,160

Models can be re-downloaded when needed (free, but takes time).

## 📚 Documentation Created

All documentation is in the repository:

- **README.md**: Quick start guide
- **SETUP_GUIDE.md**: Complete setup instructions
- **ARCHITECTURE.md**: System architecture
- **DEPLOYMENT.md**: Deployment checklist
- **GITHUB_SETUP.md**: GitHub repository setup
- **This file**: Save & destroy guide

## 🎯 What's Saved

✅ **In GitHub**:
- All source code
- Docker configurations
- Setup scripts
- Documentation
- Configuration files

❌ **Not in GitHub** (too large):
- Ollama models (40GB+)
- Knowledge graph data
- PDF files

## ⚠️ Important Notes

1. **Models**: Can be re-downloaded using `setup_models.sh`
2. **Knowledge Graph**: Must be backed up separately if you want to preserve it
3. **Code**: All code is in GitHub, fully restorable
4. **Configuration**: All configs are in GitHub

## 🚀 Next Time You Deploy

1. Clone repository
2. Run `setup_models.sh` (downloads models)
3. Run `docker compose up -d`
4. Done!

Total setup time: ~2-3 hours (mostly model download)
