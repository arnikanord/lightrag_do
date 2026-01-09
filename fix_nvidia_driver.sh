#!/bin/bash
# Fix NVIDIA Driver Version Mismatch
# This script addresses the driver/library version mismatch issue

set -e

echo "=== NVIDIA Driver Fix Script ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "Step 1: Checking current NVIDIA driver status..."
echo "Kernel module version:"
cat /proc/driver/nvidia/version 2>/dev/null || echo "NVIDIA kernel module not found"

echo ""
echo "Checking loaded modules:"
lsmod | grep nvidia || echo "No NVIDIA modules loaded"

echo ""
echo "Step 2: Checking installed NVIDIA packages..."
dpkg -l | grep -i nvidia | head -10

echo ""
echo "Step 3: Installing/Updating NVIDIA Container Toolkit for Docker GPU support..."

# Add NVIDIA Container Toolkit repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update and install
apt-get update
apt-get install -y nvidia-container-toolkit

echo ""
echo "Step 4: Configuring Docker to use NVIDIA runtime..."
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

echo ""
echo "Step 5: Verifying Docker GPU support..."
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi || {
    echo "WARNING: Docker GPU test failed. This may require a system reboot."
    echo "The kernel module version (575.57.08) and user-space library (535.274) are mismatched."
}

echo ""
echo "=== Next Steps ==="
echo "1. If nvidia-smi still shows errors, you may need to:"
echo "   - Reinstall NVIDIA drivers: sudo apt-get install --reinstall nvidia-driver-575"
echo "   - OR update to match kernel: sudo apt-get update && sudo apt-get install nvidia-driver-575"
echo "2. Reboot the system: sudo reboot"
echo "3. After reboot, verify with: nvidia-smi"
echo "4. Verify Docker GPU: docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi"
echo ""
echo "Script completed. Please review the output above."
