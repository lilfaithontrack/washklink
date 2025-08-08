# 🚀 WashLink Backend VPS Deployment Guide

## 📋 System Requirements

### Operating System
- **Ubuntu 20.04+ / CentOS 8+ / Debian 11+**
- **Minimum**: 2GB RAM, 2 CPU cores, 20GB storage
- **Recommended**: 4GB RAM, 4 CPU cores, 40GB storage

---

## 🔧 Step 1: System Update & Basic Tools

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git unzip software-properties-common
sudo apt install -y build-essential python3-dev python3-pip python3-venv
sudo apt install -y nginx supervisor certbot python3-certbot-nginx
```

---

## 🐍 Step 2: Python 3.11+ Installation

```bash
# Add Python 3.11 repository (Ubuntu/Debian)
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Create symlink (optional)
sudo ln -sf /usr/bin/python3.11 /usr/bin/python3

# Install pip for Python 3.11
curl https://bootstrap.pypa.io/get-pip.py | sudo python3.11
```

---

## 🍃 Step 3: MongoDB Installation

```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update and install MongoDB
sudo apt update
sudo apt install -y mongodb-org

# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify MongoDB installation
sudo systemctl status mongod
mongosh --version
```

---

## 📦 Step 4: Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/washlink-backend
cd /var/www/washlink-backend

# Clone your repository
sudo git clone https://github.com/lilfaithontrack/washklink.git .

# Set proper ownership
sudo chown -R $USER:$USER /var/www/washlink-backend

# Create Python virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

---

## 📚 Step 5: Python Dependencies Installation

```bash
# Install all Python packages
pip install -r requirements.txt

# Additional packages for production
pip install gunicorn uvicorn[standard] python-multipart
pip install psutil setproctitle

# Verify installations
pip list | grep -E "(fastapi|beanie|motor|uvicorn|gunicorn)"
```

---

## 🔐 Step 6: Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit environment variables
nano .env
```

### Environment Variables (.env)
```bash
# Database Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=washlink_db

# Security Settings
SECRET_KEY=your-super-secret-key-change-this-immediately
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Admin User Settings
DEFAULT_ADMIN_EMAIL=admin@washlink.com
DEFAULT_ADMIN_PASSWORD=secure-admin-password-123
DEFAULT_ADMIN_PHONE=+1234567890

# API Settings
API_VERSION=v1
DEBUG=False

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads

# Email Settings (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Payment Settings
CHAPA_SECRET_KEY=your-chapa-secret-key
TELEBIRR_MERCHANT_ID=your-telebirr-merchant-id
```

---

## 🗄️ Step 7: Database Setup

```bash
# Create MongoDB user and database
mongosh

# In MongoDB shell:
use washlink_db

# Create admin user for database
db.createUser({
  user: "washlink_admin",
  pwd: "secure-db-password",
  roles: [
    { role: "readWrite", db: "washlink_db" },
    { role: "dbAdmin", db: "washlink_db" }
  ]
})

# Exit MongoDB shell
exit

# Run database initialization
source venv/bin/activate
python setup_mongodb.py
```

---

## 🚀 Step 8: Application Configuration

### Create Gunicorn Configuration
```bash
# Create gunicorn config
nano gunicorn.conf.py
```

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "www-data"
group = "www-data"
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
```

### Create Systemd Service
```bash
sudo nano /etc/systemd/system/washlink-backend.service
```

```ini
[Unit]
Description=WashLink Backend API
After=network.target mongod.service
Requires=mongod.service

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=washlink
WorkingDirectory=/var/www/washlink-backend
Environment=PATH=/var/www/washlink-backend/venv/bin
ExecStart=/var/www/washlink-backend/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🌐 Step 9: Nginx Configuration

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/washlink-backend
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Main API location
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Static files (if any)
    location /static/ {
        alias /var/www/washlink-backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # File uploads
    location /uploads/ {
        alias /var/www/washlink-backend/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Health check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }

    # File upload size limit
    client_max_body_size 50M;
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/washlink-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Step 10: SSL Certificate (Let's Encrypt)

```bash
# Install SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

---

## 🎬 Step 11: Start Services

```bash
# Set proper permissions
sudo chown -R www-data:www-data /var/www/washlink-backend
sudo chmod -R 755 /var/www/washlink-backend

# Create necessary directories
sudo mkdir -p /var/www/washlink-backend/uploads
sudo mkdir -p /var/www/washlink-backend/logs
sudo chown -R www-data:www-data /var/www/washlink-backend/uploads
sudo chown -R www-data:www-data /var/www/washlink-backend/logs

# Start and enable services
sudo systemctl daemon-reload
sudo systemctl start washlink-backend
sudo systemctl enable washlink-backend
sudo systemctl start nginx
sudo systemctl enable nginx

# Check service status
sudo systemctl status washlink-backend
sudo systemctl status nginx
sudo systemctl status mongod
```

---

## 🔥 Step 12: Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 27017  # MongoDB (optional, for external access)
sudo ufw --force enable

# Check firewall status
sudo ufw status
```

---

## 📊 Step 13: Monitoring & Logs

```bash
# View application logs
sudo journalctl -u washlink-backend -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# Check application status
curl http://localhost:8000/health
curl https://your-domain.com/api/v1/health
```

---

## 🔄 Step 14: Backup & Maintenance

### Daily Backup Script
```bash
sudo nano /usr/local/bin/washlink-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/washlink"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --db washlink_db --out $BACKUP_DIR/mongodb_$DATE

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /var/www/washlink-backend

# Clean old backups (keep 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
sudo chmod +x /usr/local/bin/washlink-backup.sh

# Add to crontab for daily backup at 2 AM
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/washlink-backup.sh
```

---

## ✅ Verification Checklist

- [ ] MongoDB is running and accessible
- [ ] Python virtual environment is activated
- [ ] All dependencies are installed
- [ ] Environment variables are configured
- [ ] Database is initialized with admin user
- [ ] Gunicorn service is running
- [ ] Nginx is configured and running
- [ ] SSL certificate is installed
- [ ] Firewall is configured
- [ ] API endpoints are accessible
- [ ] Admin panel can connect to backend
- [ ] Mobile app can connect to backend

---

## 🆘 Troubleshooting

### Common Issues:

1. **MongoDB Connection Failed**
   ```bash
   sudo systemctl status mongod
   sudo journalctl -u mongod
   ```

2. **Gunicorn Won't Start**
   ```bash
   cd /var/www/washlink-backend
   source venv/bin/activate
   gunicorn -c gunicorn.conf.py main:app
   ```

3. **Permission Denied**
   ```bash
   sudo chown -R www-data:www-data /var/www/washlink-backend
   sudo chmod -R 755 /var/www/washlink-backend
   ```

4. **Port Already in Use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

---

## 📞 Support

For deployment issues, check:
- Application logs: `sudo journalctl -u washlink-backend -f`
- Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- MongoDB logs: `sudo tail -f /var/log/mongodb/mongod.log`

## 🎉 Deployment Complete!

Your WashLink backend is now deployed and ready for production use!

**API Base URL**: `https://your-domain.com/api/v1`
**Admin Panel URL**: Update your admin panel to point to the new API URL
**Mobile App URL**: Update your mobile app API configuration 