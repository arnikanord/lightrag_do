# Fix for ContainerConfig KeyError

## Problem
Docker Compose is failing with `KeyError: 'ContainerConfig'` when trying to recreate the container. This is a known issue with docker-compose 1.29.2.

## Solution

Stop and remove the container first, then rebuild:

```bash
cd /root/lightrag_do

# 1. Stop the container
docker-compose stop lightrag_api

# 2. Remove the container (force)
docker-compose rm -f lightrag_api

# 3. Remove the old image (optional, forces fresh build)
docker rmi lightrag_do-lightrag_api:latest 2>/dev/null || true

# 4. Build fresh (no cache)
docker-compose build --no-cache lightrag_api

# 5. Start the container
docker-compose up -d lightrag_api

# 6. Check status
docker-compose ps
docker-compose logs lightrag_api --tail 30
```

## Quick Fix Script

I've created a script that does all of this automatically:

```bash
cd /root/lightrag_do
chmod +x rebuild_api_fix.sh
./rebuild_api_fix.sh
```
