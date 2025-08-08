#!/bin/bash

# 🚀 WashLink Backend VPS Quick Install Script
# Run with: chmod +x vps-install.sh && sudo ./vps-install.sh

set -e

echo "🚀 Starting WashLink Backend VPS Installation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root directly. It will use sudo when needed."
   exit 1
fi

print_status "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

print_status "Step 2: Installing essential tools..."
sudo apt install -y curl wget git unzip software-properties-common
sudo apt install -y build-essential python3-dev python3-pip python3-venv
sudo apt install -y nginx supervisor certbot python3-certbot-nginx

print_status "Step 3: Installing Python 3.11..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

print_status "Step 4: Installing pip for Python 3.11..."
curl https://bootstrap.pypa.io/get-pip.py | sudo python3.11

print_status "Step 5: Installing MongoDB..."
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

print_status "Step 6: Starting MongoDB..."
sudo systemctl start mongod
sudo systemctl enable mongod

print_status "Step 7: Creating application directory..."
sudo mkdir -p /var/www/washlink-backend
sudo chown -R $USER:$USER /var/www/washlink-backend

print_status "Step 8: Installing Node.js (for admin panel)..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

print_status "Step 9: Setting up firewall..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

print_status "✅ Basic installation complete!"
print_warning "Next steps:"
echo "1. Clone your repository to /var/www/washlink-backend"
echo "2. Create Python virtual environment and install dependencies"
echo "3. Configure environment variables"
echo "4. Set up Nginx and Gunicorn"
echo "5. Install SSL certificate"
echo ""
print_status "Use the DEPLOYMENT_GUIDE.md for detailed instructions!"

# Display installed versions
print_status "Installed versions:"
echo "Python: $(python3.11 --version)"
echo "MongoDB: $(mongod --version | head -n1)"
echo "Nginx: $(nginx -v 2>&1)"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)" 