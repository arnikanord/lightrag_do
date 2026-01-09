# Remote Access Configuration

## Server IP Address
**http://162.243.201.21:8000**

## Current Status

The API is configured to be accessible remotely at:
- **Web Interface**: http://162.243.201.21:8000
- **API Endpoints**: http://162.243.201.21:8000/api/...
- **API Docs**: http://162.243.201.21:8000/docs

## Starting Services

### Option 1: Without GPU (If GPU driver has issues)
```bash
cd /root/gafta-guardian
docker compose -f docker-compose.no-gpu.yml up -d --build
```

### Option 2: With GPU (After fixing driver)
```bash
cd /root/gafta-guardian
docker compose up -d --build
```

## Checking API Accessibility

```bash
# Quick check
./check_api.sh

# Or manually
curl http://162.243.201.21:8000/health
```

## Firewall Configuration

If the API is not accessible remotely, check firewall:

```bash
# Check if port 8000 is open
sudo ufw status
sudo ufw allow 8000/tcp

# Or if using iptables
sudo iptables -L -n | grep 8000
```

## Troubleshooting

### Service Not Accessible Remotely

1. **Check if service is running locally**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check Docker port binding**:
   ```bash
   docker compose ps
   # Should show: 0.0.0.0:8000->8000/tcp
   ```

3. **Check firewall**:
   ```bash
   sudo ufw allow 8000
   ```

4. **Check if service is bound to all interfaces**:
   The docker-compose.yml now uses `0.0.0.0:8000:8000` to bind to all interfaces.

### GPU Driver Issues

If you see "driver/library version mismatch" errors:

1. **Fix the driver** (requires reboot):
   ```bash
   sudo ./fix_nvidia_driver.sh
   sudo reboot
   ```

2. **Or run without GPU** (slower but works):
   ```bash
   docker compose -f docker-compose.no-gpu.yml up -d
   ```

## Updated Scripts

All scripts have been updated to use the IP address:
- `bulk_ingest.py` - Uses http://162.243.201.21:8000
- `ingest_all_files.py` - Uses http://162.243.201.21:8000
- `process_all_files.sh` - Uses http://162.243.201.21:8000
- Web interface - Auto-detects and uses the IP

## Testing from Remote PC

1. **Open browser**: http://162.243.201.21:8000
2. **Check health**: http://162.243.201.21:8000/health
3. **View API docs**: http://162.243.201.21:8000/docs
