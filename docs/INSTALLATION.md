# Installation & Deployment Guide

Complete instructions for setting up and deploying the Fake Content Detection System.

## Prerequisites

### System Requirements

**Minimum**:
- Python 3.8+
- 2GB RAM
- 2GB disk space
- Chrome/Firefox browser

**Recommended**:
- Python 3.10+
- 8GB+ RAM
- NVIDIA GPU with CUDA 11.0+
- 10GB disk space

### Required Software

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Install pip if needed
python3 -m pip --version

# For Ubuntu/Debian:
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# For macOS:
brew install python3

# For Windows:
# Download from https://www.python.org/downloads/
```

## Backend Installation

### Step 1: Clone/Extract Project

```bash
# Navigate to project directory
cd /path/to/FakeContentDetection/backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Verify installation
python -c "import torch; print(torch.__version__)"
python -c "import cv2; print(cv2.__version__)"
python -c "import mediapipe; print(mediapipe.__version__)"
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Key variables to configure**:
```ini
FLASK_ENV=development        # development or production
FLASK_HOST=127.0.0.1        # 0.0.0.0 for external access
FLASK_PORT=5000             # Change if needed

UPLOAD_FOLDER=/tmp/fakedetector
LOG_LEVEL=INFO
```

### Step 5: Create Necessary Directories

```bash
# Create upload and log directories
mkdir -p /tmp/fakedetector/logs

# Give write permissions
chmod 755 /tmp/fakedetector
chmod 755 /tmp/fakedetector/logs
```

### Step 6: Run Backend Server

```bash
# Development mode
python app.py

# Should output:
# * Running on http://127.0.0.1:5000
# * Debug mode: on
```

**Alternative: Production Server**

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 30 app:app

# Or using systemd service (see below)
```

### Step 7: Verify Installation

```bash
# Check health endpoint
curl http://localhost:5000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "Fake Content Detection System",
#   "version": "1.0.0"
# }
```

## Extension Installation

### Chrome Installation

**Method 1: From Source (Development)**

1. **Extract extension folder**
   ```bash
   # Navigate to extension directory
   cd ../extension
   ```

2. **Open Chrome Extensions**
   - Type `chrome://extensions/` in address bar
   - Or: Menu → More Tools → Extensions

3. **Enable Developer Mode**
   - Toggle "Developer mode" in top-right corner

4. **Load Unpacked**
   - Click "Load unpacked"
   - Select the `extension/` folder
   - Extension will be installed!

5. **Verify Installation**
   - Look for "Fake Content Detector" icon in toolbar
   - Click icon to open popup

**Method 2: Package as CRX (Packaged)**

```bash
# Create signed extension package
# In Chrome Extensions page:
# 1. Right-click on extension
# 2. Select "Pack extension"
# 3. Choose extension folder
# 4. Generate key and CRX file
```

### Firefox Installation

1. **About Debugging**
   - Type `about:debugging#/runtime/this-firefox`

2. **Load Temporary Add-on**
   - Click "Load Temporary Add-on"
   - Select `manifest.json` from extension folder

3. **Extension Loaded**
   - Extension appears in toolbar
   - Reload page to refresh

### Configure Backend URL

1. **Open Extension Popup**
   - Click extension icon in toolbar

2. **Click Settings (⚙️)**

3. **Enter Backend URL**
   - Default: `http://localhost:5000`
   - Match your backend server address

4. **Save Settings**

## Docker Installation (Optional)

### Build Docker Image

```dockerfile
# Create Dockerfile in backend directory
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create upload directory
RUN mkdir -p /tmp/fakedetector/logs

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "30", "app:app"]
```

### Build and Run

```bash
# Build image
docker build -t fakedetector:1.0 .

# Run container
docker run -d \
    --name fakedetector-api \
    -p 5000:5000 \
    -e FLASK_ENV=production \
    -v /tmp/fakedetector:/tmp/fakedetector \
    fakedetector:1.0

# Verify container
docker ps
curl http://localhost:5000/health
```

## Kubernetes Deployment (Optional)

### Create Deployment Manifest

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fakedetector-api
  labels:
    app: fakedetector
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fakedetector
  template:
    metadata:
      labels:
        app: fakedetector
    spec:
      containers:
      - name: api
        image: fakedetector:1.0
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: uploads
          mountPath: /tmp/fakedetector
      volumes:
      - name: uploads
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: fakedetector-api
  labels:
    app: fakedetector
spec:
  selector:
    app: fakedetector
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Apply deployment
kubectl apply -f kubernetes/deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get svc

# Access service
kubectl port-forward svc/fakedetector-api 5000:80
```

## Production Deployment

### 1. Set Up Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/fakedetector.service
```

```ini
[Unit]
Description=Fake Content Detection Service
After=network.target

[Service]
Type=notify
User=fakedetector
WorkingDirectory=/opt/fakedetector/backend
Environment="PATH=/opt/fakedetector/backend/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/opt/fakedetector/backend/venv/bin/gunicorn \
    -w 4 \
    -b 0.0.0.0:5000 \
    --timeout 30 \
    --access-logfile /var/log/fakedetector/access.log \
    --error-logfile /var/log/fakedetector/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/fakedetector
sudo chown fakedetector:fakedetector /var/log/fakedetector

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable fakedetector
sudo systemctl start fakedetector

# Check status
sudo systemctl status fakedetector
```

### 2. Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/fakedetector
upstream fakedetector_backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name api.fakedetector.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.fakedetector.example.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.fakedetector.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.fakedetector.example.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # Proxy to Flask
    location / {
        proxy_pass http://fakedetector_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }
    
    # Limit file uploads
    client_max_body_size 50M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/fakedetector /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d api.fakedetector.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 4. Monitoring & Logging

```bash
# View logs
tail -f /var/log/fakedetector/error.log
tail -f /var/log/fakedetector/access.log

# Monitor processes
htop

# Monitor disk usage
df -h /tmp/fakedetector
```

## GPU Setup (Optional but Recommended)

### NVIDIA GPU Setup

```bash
# Install NVIDIA CUDA Toolkit
# Ubuntu:
sudo apt-get install nvidia-cuda-toolkit

# macOS:
brew install cuda

# Windows:
# Download from https://developer.nvidia.com/cuda-toolkit

# Verify installation
nvcc --version
nvidia-smi
```

### PyTorch GPU Support

```bash
# Install PyTorch with CUDA support
pip uninstall torch -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU
python -c "import torch; print(torch.cuda.is_available())"
```

## Testing Installation

### Backend Tests

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test image analysis
curl -X POST http://localhost:5000/api/v1/analyze/image \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}'

# Test file upload
curl -X POST http://localhost:5000/api/v1/analyze/image \
  -F "file=@test_image.jpg"
```

### Extension Tests

1. **Open Test Page**
   - Open any website with images
   - Right-click an image
   - Select "🔍 Analyze Image (Fake Detector)"

2. **Check Console**
   - Press F12 to open Developer Tools
   - Go to Console tab
   - Check for any errors

3. **Verify Results**
   - Should see analysis results in popup
   - Results should display risk level

## Troubleshooting

### Issue: ModuleNotFoundError
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
echo "FLASK_PORT=5001" >> .env
```

### Issue: GPU Not Detected
```bash
# Check NVIDIA drivers
nvidia-smi

# If not found, install drivers
# Ubuntu: sudo apt-get install nvidia-driver-XXX
# Windows: Download from NVIDIA website

# Reinstall PyTorch with CUDA support
pip install --upgrade torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Out of Memory
```bash
# Reduce batch processing
# Restart server with memory limits
# Or increase swap:
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Post-Installation

### 1. Security Hardening

```bash
# Create non-root user
sudo useradd -m -s /bin/bash fakedetector

# Set permissions
sudo chown -R fakedetector:fakedetector /opt/fakedetector

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Backup Configuration

```bash
# Backup .env file
cp backend/.env backend/.env.backup

# Regular backups
crontab -e
# Add: 0 0 * * * tar -czf /backups/fakedetector-$(date +%Y-%m-%d).tar.gz /opt/fakedetector
```

### 3. Update Strategy

```bash
# Check for updates
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart fakedetector
```

## Verification Checklist

- [ ] Backend server running on configured port
- [ ] Health endpoint responding
- [ ] Extension loads without errors
- [ ] Can analyze sample images
- [ ] Results display correctly
- [ ] GPU accelerated (if available)
- [ ] Logs being created
- [ ] HTTPS configured (production)
- [ ] Firewall rules applied
- [ ] Backups scheduled
- [ ] Monitoring configured

---

**Last Updated**: April 2026 | **Version**: 1.0
