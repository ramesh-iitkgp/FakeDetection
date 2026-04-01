# API Specification - Fake Content Detection System

Complete API documentation for the detection backend.

## Base URL

```
http://localhost:5000
https://api.fakedetector.example.com  # Production
```

## Authentication

Currently no authentication required. For production, implement:
- API Key validation
- Rate limiting per IP
- CORS validation

## Response Format

All responses are JSON with the following structure:

```json
{
  "status": "success|error",
  "data": { ... },
  "error": "message (if status=error)",
  "timestamp": "ISO8601 timestamp"
}
```

---

## Endpoints

### 1. Health Check

Check if service is running and healthy.

**Request**
```http
GET /health
```

**Response**
```json
{
  "status": "healthy",
  "service": "Fake Content Detection System",
  "version": "1.0.0",
  "uptime": 3600,
  "gpu_available": true
}
```

**Status Codes**
- `200 OK`: Service healthy
- `503 Service Unavailable`: Service down

---

### 2. Analyze Image

Analyze a single image for deepfakes and manipulation.

**Request**
```http
POST /api/v1/analyze/image
Content-Type: application/json

{
  "url": "https://example.com/image.jpg"
}
```

Or with file upload:
```http
POST /api/v1/analyze/image
Content-Type: multipart/form-data

file: <binary image data>
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | Optional | URL to image (alternative to file) |
| file | binary | Optional | Image file (alternative to url) |

**Response (200 OK)**
```json
{
  "status": "success",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "content_type": "image",
  "image_size": [1920, 1080],
  
  "detection_results": {
    "face_count": 1,
    "is_deepfake": false,
    "confidence": 0.32,
    "risk_factors": [
      "Frequency anomalies detected"
    ],
    "detections": [
      {
        "bbox": [100, 150, 200, 200],
        "face_detection_confidence": 0.95,
        "deepfake_score": 0.25,
        "indicators": {
          "frequency_score": 0.35,
          "texture_score": 0.28,
          "blink_score": 0.22,
          "blend_score": 0.18
        },
        "risk_factors": [
          "Frequency anomalies detected"
        ]
      }
    ]
  },
  
  "metadata_results": {
    "exif_analysis": {
      "exif_present": true,
      "exif_stripped": false,
      "suspicious_fields": [],
      "suspicion_score": 0.1
    },
    "compression_analysis": {
      "format": "JPEG",
      "has_double_compression": false,
      "suspicion_score": 0.2
    },
    "noise_analysis": {
      "noise_variance": 0.45,
      "noise_consistency": 0.9,
      "suspicion_score": 0.15
    },
    "anomaly_score": 0.15,
    "is_suspicious": false,
    "confidence": 0.15
  },
  
  "overall_risk": {
    "level": "low",
    "score": 0.2375
  },
  
  "confidence": 0.2375,
  "processing_time_ms": 3200
}
```

**Error Response (400 Bad Request)**
```json
{
  "status": "error",
  "message": "File type not allowed. Allowed: jpg, jpeg, png, gif, bmp, mp4, avi, mov, webm"
}
```

**Error Codes**
- `400 Bad Request`: Invalid input
- `413 Payload Too Large`: File exceeds max size (50MB)
- `500 Internal Server Error`: Processing error
- `503 Service Unavailable`: Service overloaded

---

### 3. Analyze Video

Analyze video for deepfakes by sampling frames.

**Request**
```http
POST /api/v1/analyze/video
Content-Type: multipart/form-data

file: <binary video data>
sample_frames: 10
```

Or with URL:
```http
POST /api/v1/analyze/video
Content-Type: application/json

{
  "url": "https://example.com/video.mp4",
  "sample_frames": 10
}
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| url | string | - | Video URL |
| file | binary | - | Video file |
| sample_frames | integer | 10 | Number of frames to analyze |

**Response (200 OK)**
```json
{
  "status": "success",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "content_type": "video",
  
  "frame_count": 300,
  "fps": 24.0,
  "duration_seconds": 12.5,
  "frames_analyzed": 10,
  
  "detection_results": {
    "frame_scores": [
      {
        "frame_index": 0,
        "score": 0.28,
        "detections": 1,
        "deepfake": false
      },
      {
        "frame_index": 33,
        "score": 0.32,
        "detections": 1,
        "deepfake": false
      },
      {
        "frame_index": 66,
        "score": 0.31,
        "detections": 1,
        "deepfake": false
      }
    ],
    "confidence": 0.30,
    "confidence_std": 0.018,
    "is_deepfake": false
  },
  
  "metadata_results": {
    "frame_count": 300,
    "frame_rate": 24.0,
    "frame_metadata": [
      {
        "frame_index": 0,
        "compression_score": 0.15
      }
    ],
    "anomaly_score": 0.15,
    "confidence": 0.15,
    "is_suspicious": false
  },
  
  "overall_risk": {
    "level": "low",
    "score": 0.225
  },
  
  "confidence": 0.225,
  "processing_time_ms": 12500
}
```

**Notes**
- Min sample_frames: 1
- Max sample_frames: 100
- Processing time scales with sample_frames
- Average: ~1-2s per frame analysis
- Consistency check: If std > 0.3, content might be partially fake

---

### 4. Batch Analysis

Analyze multiple images in one request.

**Request**
```http
POST /api/v1/analyze/batch
Content-Type: multipart/form-data

files: <image1>, <image2>, <image3>, ...
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| files | array[binary] | Yes | Multiple image files (max 50) |

**Response (200 OK)**
```json
{
  "status": "success",
  "total_files": 5,
  "analyzed": 5,
  "failed": 0,
  
  "results": [
    {
      "filename": "image1.jpg",
      "size_bytes": 125000,
      "analysis_id": "550e8400-e29b-41d4-a716-446655440002",
      
      "detection_results": {
        "face_count": 1,
        "is_deepfake": false,
        "confidence": 0.28
      },
      "metadata_results": {
        "anomaly_score": 0.18,
        "is_suspicious": false
      },
      "overall_risk": {
        "level": "low",
        "score": 0.235
      },
      "processing_time_ms": 3100
    },
    {
      "filename": "image2.jpg",
      "size_bytes": 180000,
      "analysis_id": "550e8400-e29b-41d4-a716-446655440003",
      
      "detection_results": {
        "face_count": 0,
        "is_deepfake": false,
        "confidence": 0.0
      },
      "metadata_results": {
        "anomaly_score": 0.12,
        "is_suspicious": false
      },
      "overall_risk": {
        "level": "low",
        "score": 0.06
      },
      "processing_time_ms": 1800
    }
  ],
  
  "summary": {
    "high_risk_count": 0,
    "medium_risk_count": 0,
    "low_risk_count": 5,
    "average_confidence": 0.1786,
    "total_processing_time_ms": 9200
  }
}
```

**Notes**
- Max 50 files per batch
- Processed sequentially or in parallel (depending on config)
- Individual file failures don't stop batch
- Good for bulk scanning

---

## Response Objects

### Detection Result Object

```json
{
  "face_count": 0,
  "is_deepfake": false,
  "confidence": 0.32,
  "risk_factors": [
    "string: description of risk"
  ],
  "detections": [
    {
      "bbox": [x, y, width, height],
      "face_detection_confidence": 0.95,
      "deepfake_score": 0.25,
      "indicators": {
        "frequency_score": 0.35,
        "texture_score": 0.28,
        "blink_score": 0.22,
        "blend_score": 0.18
      },
      "risk_factors": ["string"]
    }
  ]
}
```

### Metadata Result Object

```json
{
  "exif_analysis": {
    "exif_present": true,
    "exif_stripped": false,
    "suspicious_fields": ["field_name"],
    "suspicion_score": 0.2
  },
  "compression_analysis": {
    "format": "JPEG",
    "has_double_compression": false,
    "suspicion_score": 0.2
  },
  "noise_analysis": {
    "noise_variance": 0.45,
    "noise_consistency": 0.9,
    "suspicion_score": 0.15
  },
  "anomaly_score": 0.2,
  "is_suspicious": false,
  "confidence": 0.2
}
```

### Risk Object

```json
{
  "level": "low|medium|high|critical",
  "score": 0.0-1.0
}
```

**Risk Level Mapping**

| Level | Score Range | Meaning |
|-------|------------|---------|
| low | 0.0 - 0.4 | Likely authentic |
| medium | 0.4 - 0.6 | Some anomalies |
| high | 0.6 - 0.8 | Likely fake |
| critical | 0.8 - 1.0 | Very likely fake |

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-04-01T12:34:56Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Common Errors

| Status | Code | Message | Solution |
|--------|------|---------|----------|
| 400 | INVALID_INPUT | "File type not allowed" | Use supported format |
| 400 | INVALID_URL | "Invalid URL format" | Check URL syntax |
| 413 | FILE_TOO_LARGE | "File size exceeds 50MB" | Use smaller file |
| 415 | UNSUPPORTED_MEDIA | "Content-Type not supported" | Use correct MIME type |
| 500 | PROCESSING_ERROR | "Error during analysis" | Retry or check logs |
| 503 | SERVICE_UNAVAILABLE | "Service temporarily unavailable" | Retry later |

---

## Rate Limiting

Recommended rate limiting (to implement):

```
- Free tier: 10 requests/minute per IP
- Pro tier: 100 requests/minute per IP
- Enterprise: Unlimited
```

---

## Caching

Recommended caching strategy:

```
- Health check: 0s (always fresh)
- Image analysis: 24 hours (same image, same result)
- Metadata: 48 hours
- Video: 12 hours (may contain temporal elements)
```

Cache key: `sha256(file_content or url)`

---

## Webhook Support (Future)

```http
POST /api/v1/analyze/image
Content-Type: application/json

{
  "url": "https://example.com/image.jpg",
  "webhook": "https://yourserver.com/callback",
  "webhook_secret": "secret_key"
}
```

Webhook called when analysis complete:
```json
{
  "analysis_id": "uuid",
  "status": "complete",
  "results": { ... }
}
```

---

## Python Client Example

```python
import requests
import json

class FakeDetectorClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def analyze_image(self, url=None, file_path=None):
        """Analyze an image"""
        if url:
            response = requests.post(
                f"{self.base_url}/api/v1/analyze/image",
                json={"url": url}
            )
        elif file_path:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.base_url}/api/v1/analyze/image",
                    files={"file": f}
                )
        
        return response.json()
    
    def analyze_video(self, url=None, file_path=None, sample_frames=10):
        """Analyze a video"""
        if url:
            response = requests.post(
                f"{self.base_url}/api/v1/analyze/video",
                json={
                    "url": url,
                    "sample_frames": sample_frames
                }
            )
        elif file_path:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.base_url}/api/v1/analyze/video",
                    files={"file": f},
                    data={"sample_frames": sample_frames}
                )
        
        return response.json()
    
    def health_check(self):
        """Check service health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage
client = FakeDetectorClient()

# Check health
print(client.health_check())

# Analyze image
result = client.analyze_image(url="https://example.com/image.jpg")
print(f"Risk Level: {result['overall_risk']['level']}")
print(f"Confidence: {result['overall_risk']['score']:.2%}")

# Analyze video
video_result = client.analyze_video(
    url="https://example.com/video.mp4",
    sample_frames=15
)
print(f"Frames analyzed: {video_result['frames_analyzed']}")
```

---

## JavaScript/Fetch Example

```javascript
async function analyzeImage(imageUrl) {
    const response = await fetch('http://localhost:5000/api/v1/analyze/image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: imageUrl
        })
    });
    
    const result = await response.json();
    return result;
}

async function analyzeFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:5000/api/v1/analyze/image', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    return result;
}

// Usage
const result = await analyzeImage('https://example.com/image.jpg');
console.log(`Risk: ${result.overall_risk.level}`);
console.log(`Confidence: ${(result.overall_risk.score * 100).toFixed(1)}%`);
```

---

## cURL Examples

```bash
# Health check
curl http://localhost:5000/health

# Analyze image from URL
curl -X POST http://localhost:5000/api/v1/analyze/image \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}'

# Analyze local image
curl -X POST http://localhost:5000/api/v1/analyze/image \
  -F "file=@/path/to/image.jpg"

# Analyze video
curl -X POST http://localhost:5000/api/v1/analyze/video \
  -F "file=@/path/to/video.mp4" \
  -F "sample_frames=10"

# Batch analysis
curl -X POST http://localhost:5000/api/v1/analyze/batch \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg"
```

---

## Performance Metrics

All responses include processing time:

```json
{
  "processing_time_ms": 3200,
  "gpu_used": true
}
```

**Expected Times**:
- Image (GPU): 2-5s
- Image (CPU): 5-10s  
- Video per frame: 1-2s (GPU), 2-5s (CPU)
- Metadata: <500ms

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-01 | Initial release |

## Future Versions

- [ ] Streaming upload support
- [ ] Webhook notifications
- [ ] Advanced filtering options
- [ ] Multi-model comparison
- [ ] Audio deepfake detection
- [ ] Blockchain verification

---

**Last Updated**: April 2026 | **API Version**: 1.0
