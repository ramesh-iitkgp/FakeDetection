# Backend Server - Fake Content Detection

Flask-based REST API for detecting fake and manipulated content using multiple AI models.

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy and edit environment variables
cp .env.example .env
# Edit .env with your settings
```

### 3. Run

```bash
# Development
python app.py

# Production (with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Server will be available at `http://localhost:5000`

## API Reference

### Image Analysis
- **Endpoint**: `POST /api/v1/analyze/image`
- **Parameters**: URL or multipart file upload
- **Returns**: Detection results with confidence scores
- **Time**: 2-5s per image

### Video Analysis  
- **Endpoint**: `POST /api/v1/analyze/video`
- **Parameters**: URL, sample_frames (default: 10)
- **Returns**: Frame-by-frame analysis
- **Time**: ~1-2s per frame

### Batch Analysis
- **Endpoint**: `POST /api/v1/analyze/batch`
- **Parameters**: Multiple files in form-data
- **Returns**: Results for each file
- **Limit**: 50 files per batch

### Health Check
- **Endpoint**: `GET /health`
- **Returns**: Server status
- **Usage**: For load balancer checks

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration classes
├── utils/
│   ├── detector.py     # Deepfake detection
│   ├── metadata_analyzer.py  # Metadata analysis
│   └── error_handler.py      # Error handling
├── models/             # Pre-trained models (downloaded on first use)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## Detection Models

### 1. Deepfake Detection
- **Method**: Multi-indicator ensemble
- **Components**:
  - Face detection (MediaPipe)
  - Frequency domain analysis
  - Texture consistency checks
  - Facial landmark analysis
- **Confidence**: 0-1 score

### 2. Metadata Analysis
- **EXIF Data**: Validates photo properties
- **Compression**: Detects JPEG artifacts
- **Noise Patterns**: Analyzes noise consistency
- **Color Distribution**: HSV histogram analysis

### 3. Frequency Domain
- **FFT Analysis**: Detects synthetic patterns
- **Power Spectrum**: Anomaly detection
- **Block Artifacts**: JPEG compression patterns

### 4. Facial Consistency
- **Eye Symmetry**: Checks bilateral consistency
- **Blend Boundaries**: Detects pasting artifacts
- **Facial Geometry**: Validates natural proportions

## Configuration

### Environment Variables (.env)

```ini
# Server
FLASK_ENV=development
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# File handling
UPLOAD_FOLDER=/tmp/fakedetector
MAX_FILE_SIZE=52428800

# Detection
DETECTION_CONFIDENCE_THRESHOLD=0.5
ENABLE_FREQUENCY_ANALYSIS=true
ENABLE_METADATA_ANALYSIS=true
ENABLE_DEEPFAKE_DETECTION=true

# Performance
MAX_WORKERS=4
API_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=/tmp/fakedetector/logs/api.log
```

## Dependencies

```
Flask==2.3.3
torch==2.0.0
torchvision==0.15.1
opencv-python==4.8.0.76
numpy==1.24.3
Pillow==10.0.0
mediapipe==0.8.11
exifread==3.0.0
```

## Performance Tips

- **GPU**: Install CUDA for 3-5x faster processing
- **Batch Processing**: Use `/batch` endpoint for multiple files
- **Caching**: Enable Redis for repeated file analysis
- **Sampling**: Reduce video sample_frames for faster processing

## Troubleshooting

### Issue: ModuleNotFoundError
```bash
# Ensure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: CUDA not found
```bash
# Use CPU fallback (slower)
# Or install CUDA 11.0+: https://developer.nvidia.com/cuda-downloads
```

### Issue: Port 5000 already in use
```bash
# Change port in .env
FLASK_PORT=5001
# Or kill existing process
lsof -ti:5000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :5000   # Windows (find PID and kill)
```

## Development

### Adding a Custom Model

1. Create model file in `models/`:
```python
# models/custom_detector.py
class MyDetector:
    def __init__(self):
        self.model = load_model()
    
    def detect(self, image):
        return prediction_score
```

2. Register in `utils/detector.py`:
```python
from models.custom_detector import MyDetector
self.models['custom'] = MyDetector()
```

3. Use in analysis:
```python
score = self.models['custom'].detect(frame)
```

### Running Tests

```bash
# (Tests not yet implemented - future work)
pytest tests/
```

## API Examples

### Analyze Image URL
```bash
curl -X POST http://localhost:5000/api/v1/analyze/image \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}'
```

### Analyze Local Image
```bash
curl -X POST http://localhost:5000/api/v1/analyze/image \
  -F "file=@/path/to/image.jpg"
```

### Analyze Video
```bash
curl -X POST http://localhost:5000/api/v1/analyze/video \
  -F "file=@/path/to/video.mp4" \
  -F "sample_frames=10"
```

### Python Client
```python
import requests

# Analyze image
response = requests.post(
    'http://localhost:5000/api/v1/analyze/image',
    json={'url': 'https://example.com/image.jpg'}
)
results = response.json()
print(f"Risk Level: {results['overall_risk']['level']}")
print(f"Confidence: {results['overall_risk']['score']}")
```

## Deployment

### Docker
```dockerfile
# Dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
# Build and run
docker build -t fakedetector .
docker run -p 5000:5000 fakedetector
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fakedetector-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fakedetector-api
  template:
    metadata:
      labels:
        app: fakedetector-api
    spec:
      containers:
      - name: api
        image: fakedetector:latest
        ports:
        - containerPort: 5000
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

## Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use production WSGI server (gunicorn, uWSGI)
- [ ] Configure CORS properly
- [ ] Set up HTTPS/SSL
- [ ] Configure logging and monitoring
- [ ] Set up database for result caching
- [ ] Configure backups
- [ ] Rate limiting for API
- [ ] Load balancer setup
- [ ] Security headers

## Support

For issues or questions:
1. Check logs: `tail -f /tmp/fakedetector/logs/api.log`
2. Run health check: `curl http://localhost:5000/health`
3. Review error_handler.py for error codes
