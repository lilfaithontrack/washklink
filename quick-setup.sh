#!/bin/bash

# 🏃‍♂️ Quick Setup Script for WashLink Backend
# Run after basic VPS installation: chmod +x quick-setup.sh && ./quick-setup.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the washlink backend directory"
    exit 1
fi

print_status "Setting up WashLink Backend Application..."

# Create virtual environment
print_status "Creating Python virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install additional production packages
print_status "Installing production packages..."
pip install gunicorn uvicorn[standard] python-multipart psutil setproctitle

# Copy environment file
if [ ! -f ".env" ]; then
    print_status "Creating environment file..."
    cp env.example .env
    print_warning "Please edit .env file with your configuration!"
fi

# Create necessary directories
print_status "Creating application directories..."
mkdir -p uploads logs static

# Set permissions
print_status "Setting permissions..."
chmod -R 755 .
chmod -R 777 uploads logs

# Initialize database
print_status "Setting up MongoDB database..."
python setup_mongodb.py || print_warning "Database setup failed - please run manually"

print_status "✅ Application setup complete!"
print_warning "Next steps:"
echo "1. Edit .env file with your settings"
echo "2. Configure Nginx (see DEPLOYMENT_GUIDE.md)"
echo "3. Set up systemd service"
echo "4. Install SSL certificate"
echo "5. Start the application"

print_status "To test the application:"
echo "source venv/bin/activate"
echo "uvicorn main:app --host 0.0.0.0 --port 8000" 