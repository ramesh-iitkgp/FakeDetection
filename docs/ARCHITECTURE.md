# System Architecture & Design Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Design](#architecture-design)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [AI Model Integration](#ai-model-integration)
6. [Security Architecture](#security-architecture)
7. [Scalability & Performance](#scalability--performance)

## System Overview

The Fake Content Detection System is a distributed application that combines multiple AI models and forensic analysis techniques to detect deepfakes and manipulated media with high accuracy.

### Key Characteristics
- **Multi-Model Ensemble**: Combines 4+ different detection approaches
- **Browser-Native**: Chrome extension for seamless integration
- **Python Backend**: Flexible Flask API for model management
- **Real-time Processing**: GPU-accelerated analysis
- **Privacy-Focused**: No data storage or tracking
- **Scalable Architecture**: Horizontal scaling ready

## Architecture Design

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                  User's Browser                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │    Chrome Extension (UI + Content Scripts)       │  │
│  │  ┌─────────────┬─────────┬──────────────────┐   │  │
│  │  │   Popup     │ Content │  Service Worker  │   │  │
│  │  │   Interface │ Script  │  (Background)    │   │  │
│  │  └─────────────┴─────────┴──────────────────┘   │  │
│  │         ↓ REST API Calls ↓                      │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↕ HTTP/HTTPS
┌─────────────────────────────────────────────────────────┐
│             Detection Backend Server                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │         Flask REST API Server                    │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ Route Handlers & Request Validation       │  │  │
│  │  │ • /api/v1/analyze/image                   │  │  │
│  │  │ • /api/v1/analyze/video                   │  │  │
│  │  │ • /api/v1/analyze/batch                   │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Detection Pipeline                        │  │  │
│  │  │  ┌──────────────────────────────────────┐  │  │  │
│  │  │  │  Content Detector (Deepfakes)        │  │  │  │
│  │  │  │  • MediaPipe Face Detection          │  │  │  │
│  │  │  │  • CNN Classification                │  │  │  │
│  │  │  │  • Frequency Analysis                │  │  │  │
│  │  │  │  • Texture Analysis                  │  │  │  │
│  │  │  │  • Eye Consistency Checks            │  │  │  │
│  │  │  │  • Blend Boundary Detection          │  │  │  │
│  │  │  └──────────────────────────────────────┘  │  │  │
│  │  │  ┌──────────────────────────────────────┐  │  │  │
│  │  │  │  Metadata Analyzer                   │  │  │  │
│  │  │  │  • EXIF Analysis                     │  │  │  │
│  │  │  │  • Compression Detection             │  │  │  │
│  │  │  │  • Noise Consistency                 │  │  │  │
│  │  │  │  • Visual Inconsistencies            │  │  │  │
│  │  │  └──────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Ensemble Scorer                         │  │  │
│  │  │  • Combines all detector outputs        │  │  │
│  │  │  • Calculates overall risk              │  │  │
│  │  │  • Generates detailed report            │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐    │
│  │  Data Layer                                   │    │
│  │  • File Upload Storage (Temporary)            │    │
│  │  • Cache (Redis) - Optional                   │    │
│  │  • Logs Storage                               │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
         ↕
    GPU/CPU Processing
```

### Three-Tier Architecture

#### Tier 1: Presentation Layer (Browser)
- **Chrome Extension UI**: User interface for analysis
- **Content Scripts**: Page manipulation and image detection
- **Service Worker**: Background task management
- **Responsibility**: User interaction, image collection, result display

#### Tier 2: Application Layer (Flask API)
- **Request Routing**: Directs requests to appropriate processors
- **Input Validation**: Validates file types and sizes
- **Orchestration**: Manages detector pipeline
- **Response Formatting**: Structures results for UI
- **Responsibility**: Business logic, model coordination

#### Tier 3: Processing Layer (AI Models)
- **Deepfake Detector**: Multiple face and texture analysis models
- **Metadata Analyzer**: File properties and artifact detection
- **Ensemble Scorer**: Combines results into final verdict
- **Responsibility**: Actual analysis and detection

## Component Details

### 1. Chrome Extension

#### Popup Interface (`popup.html/js`)
**Purpose**: Main user interface

**Features**:
- Tab-based navigation (Analyze, History, Help)
- URL input and file upload
- Real-time result display
- Settings management
- Analysis history tracking

**Key Classes**:
```javascript
class PopupUI {
    - init()                    // Initialize UI
    - analyzeURL()             // Analyze image URL
    - analyzeFile()            // Upload and analyze file
    - displayResults()         // Show results to user
    - switchTab()              // Tab navigation
    - saveSettings()           // Persist user preferences
}
```

#### Content Script (`content-script.js`)
**Purpose**: Inject functionality into web pages

**Features**:
- Extract images from page
- Inject warning badges on suspicious images
- Context menu integration
- Page-level analysis coordination

#### Service Worker (`service-worker.js`)
**Purpose**: Background processing and API communication

**Features**:
- API communication with backend
- Context menu setup
- Tab monitoring
- Message routing

### 2. Flask Backend

#### Main Application (`app.py`)
```python
# Route Handlers
@app.route('/api/v1/analyze/image', methods=['POST'])
@app.route('/api/v1/analyze/video', methods=['POST'])
@app.route('/api/v1/analyze/batch', methods=['POST'])
@app.route('/health', methods=['GET'])

# Utility Functions
calculate_overall_risk()
allowed_file()
```

#### Content Detector (`utils/detector.py`)
**Class**: `ContentDetector`

**Methods**:
```python
class ContentDetector:
    analyze_image(image_source)        # Single image analysis
    analyze_video(video_source, frames) # Video frame sampling
    _load_image()                      # Image loading
    _detect_faces()                    # Face detection
    _analyze_face()                    # Per-face analysis
    _frequency_analysis()              # FFT-based detection
    _texture_analysis()                # Texture pattern detection
    _check_eye_consistency()           # Eye symmetry check
    _detect_blend_boundaries()         # Pasting artifact detection
```

**Detection Pipeline**:
1. Load and preprocess image/frame
2. Detect faces using MediaPipe
3. For each detected face:
   - Extract face region
   - Apply frequency analysis
   - Apply texture analysis
   - Check eye consistency
   - Detect blend boundaries
4. Calculate deepfake score (average of indicators)
5. Return results with confidence

#### Metadata Analyzer (`utils/metadata_analyzer.py`)
**Class**: `MetadataAnalyzer`

**Methods**:
```python
class MetadataAnalyzer:
    analyze_image()                    # Complete image metadata
    analyze_video()                    # Video metadata
    _analyze_exif()                    # EXIF data validation
    _analyze_compression()             # JPEG artifact detection
    _analyze_noise()                   # Noise pattern consistency
    _analyze_inconsistencies()         # Visual inconsistencies
```

**Metadata Checks**:
1. **EXIF Analysis**:
   - Check EXIF present/missing
   - Validate timestamp consistency
   - Check GPS data integrity
   - Verify camera model consistency

2. **Compression Analysis**:
   - Detect JPEG block artifacts
   - Identify double compression
   - Analyze quality consistency

3. **Noise Analysis**:
   - Compare noise in different regions
   - Detect noise pattern inconsistencies
   - Identify noise reduction artifacts

4. **Visual Consistency**:
   - Analyze color distribution
   - Check lighting consistency
   - Detect perspective distortions

### 3. Error Handling

**Error Handler** (`utils/error_handler.py`):
```python
class APIError(Exception)       # Base API error
class DetectionError(APIError)  # Detection failures
class MetadataError(APIError)   # Metadata analysis failures
```

**HTTP Status Codes**:
- 200: Success
- 400: Bad request (invalid input)
- 413: File too large
- 500: Server error
- 503: Service unavailable

## Data Flow

### Image Analysis Flow

```
User uploads image
        ↓
Browser sends POST request
        ↓
Flask validates input
        ↓
Save file temporarily
        ↓
ContentDetector.analyze_image()
    ├→ Load image
    ├→ Detect faces
    ├→ For each face:
    │   ├→ Frequency analysis
    │   ├→ Texture analysis
    │   ├→ Eye consistency
    │   └→ Blend boundary detection
    └→ Return deepfake_score + risk_factors
        ↓
MetadataAnalyzer.analyze_image()
    ├→ Extract EXIF data
    ├→ Analyze compression
    ├→ Analyze noise patterns
    ├→ Check inconsistencies
    └→ Return anomaly_score
        ↓
Calculate overall_risk
    ├→ Combine detection + metadata scores
    ├→ Determine risk level
    └→ Return final verdict
        ↓
Delete temporary file
        ↓
Return JSON response
        ↓
Extension displays results to user
```

### Video Analysis Flow

```
User uploads video
        ↓
Flask validates input
        ↓
Save file temporarily
        ↓
ContentDetector.analyze_video()
    ├→ Open video file
    ├→ Sample N frames uniformly
    ├→ For each frame:
    │   ├→ analyze_image() [single frame detection]
    │   └→ Collect score
    ├→ Calculate mean/std of scores
    └→ Return frame_scores + overall confidence
        ↓
MetadataAnalyzer.analyze_video()
    ├→ Extract video metadata
    ├→ Analyze frame compression
    └→ Check temporal consistency
        ↓
Calculate overall_risk
        ↓
Delete temporary file
        ↓
Return JSON response
```

## AI Model Integration

### Detection Models Ensemble

#### Model 1: Face Detection (MediaPipe)
**Purpose**: Locate and identify faces in images

**Process**:
```
Input Image
    ↓
MediaPipe Face Detection
    ├→ Returns: bounding boxes
    ├→ Returns: confidence scores
    └→ Returns: facial landmarks (optional)
    ↓
Output: Face locations and confidence
```

**Advantages**:
- Real-time performance
- Multi-face detection
- Robust to angles and lighting
- Free and open-source

#### Model 2: Frequency Domain Analysis
**Purpose**: Detect synthetic patterns in frequency spectrum

**Process**:
```
Face Region
    ↓
Convert to Grayscale
    ↓
Apply 2D FFT
    ↓
Compute Power Spectrum
    ↓
Analyze Distribution
    ├→ Synthetic faces show different patterns
    └→ Natural faces have characteristic spectrum
    ↓
Output: Frequency anomaly score (0-1)
```

**Detection Logic**:
- Real faces: Normal frequency distribution
- Synthetic faces: Unusual peaks/valleys in spectrum
- Compressed images: Artifacts at block boundaries

#### Model 3: Texture Analysis
**Purpose**: Identify artificial texture patterns

**Process**:
```
Face Region
    ↓
Apply Laplacian Filter
    ↓
Compute Texture Variance
    ↓
Compare with Expected Values
    ├→ Synthetic: Different texture patterns
    └→ Real: Natural skin texture variations
    ↓
Output: Texture anomaly score (0-1)
```

#### Model 4: Eye Consistency (Liveness Check)
**Purpose**: Detect unnatural eye characteristics

**Process**:
```
Face Region
    ↓
Extract Left and Right Eyes
    ↓
Compare Eye Characteristics
    ├→ Correlation analysis
    ├→ Symmetry check
    └→ Blink pattern (for video)
    ↓
Output: Eye consistency score (0-1)
```

#### Model 5: Blend Boundary Detection
**Purpose**: Detect face swapping/pasting artifacts

**Process**:
```
Face Region
    ↓
Apply Canny Edge Detection
    ↓
Analyze Edge Distribution
    ├→ Boundary regions
    ├→ Interior regions
    └→ Boundary-to-total ratio
    ↓
High boundary edges = Likely face splicing
    ↓
Output: Blend artifact score (0-1)
```

### Ensemble Scoring Algorithm

**Final Score Calculation**:
```python
# Individual scores from each detector
frequency_score = 0-1
texture_score = 0-1
eye_score = 0-1
blend_score = 0-1
metadata_score = 0-1

# Ensemble combination (weighted average)
ensemble_score = (
    frequency_score * 0.2 +
    texture_score * 0.2 +
    eye_score * 0.15 +
    blend_score * 0.15 +
    metadata_score * 0.3
)

# Map to risk level
if ensemble_score > 0.8:
    risk_level = "CRITICAL"
elif ensemble_score > 0.6:
    risk_level = "HIGH"
elif ensemble_score > 0.4:
    risk_level = "MEDIUM"
else:
    risk_level = "LOW"
```

## Security Architecture

### Data Security

#### Input Validation
```python
# File type validation
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm'}

# File size limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# MIME type verification
validate_mime_type(file)
```

#### Temporary File Management
```python
# Generate secure filenames
filename = f"{uuid.uuid4()}_{original_filename}"

# Delete after processing
os.remove(file_path)

# Cleanup on error
try:
    process()
finally:
    cleanup()
```

### Privacy Protection

#### No Data Persistence
- ❌ No user accounts required
- ❌ No data storage
- ❌ No analytics/tracking
- ❌ No cookies (except essential)

#### Local Processing
- ✅ Analysis runs locally (or in user's server)
- ✅ Files not sent to third parties
- ✅ Metadata not collected

### Communication Security

#### HTTPS/TLS
```python
# Production config
if production:
    PREFERRED_PROTOCOL = "https"
    FORCE_HTTPS = True
    HSTS_ENABLED = True
```

#### CORS Configuration
```python
# Extension-only access
CORS_ALLOWED_ORIGINS = [
    'chrome-extension://*',
    'https://fakedetector.example.com'
]
```

## Scalability & Performance

### Performance Characteristics

| Operation | Time (CPU) | Time (GPU) |
|-----------|-----------|-----------|
| Image Analysis | 5-10s | 2-5s |
| Frequency Analysis | 1-2s | <500ms |
| Metadata Analysis | <500ms | <500ms |
| Video Frame | 5-10s | 2-5s |

### Optimization Strategies

#### 1. GPU Acceleration
```python
# Enable CUDA for PyTorch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
```

#### 2. Batch Processing
```python
# Process multiple images efficiently
@app.route('/api/v1/analyze/batch', methods=['POST'])
def batch_analysis():
    # Parallel processing with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(analyze_single, files))
```

#### 3. Caching
```python
# Optional Redis caching
if CACHE_ENABLED:
    cache.set(image_hash, result, ttl=3600)
```

#### 4. Image Preprocessing
```python
# Resize for faster processing if needed
MAX_DIMENSION = 1024
if image.width > MAX_DIMENSION:
    image = resize_image(image, MAX_DIMENSION)
```

### Horizontal Scaling

**Load Balancer Setup**:
```yaml
# Multiple backend instances
- Instance 1: api1.example.com:5000
- Instance 2: api2.example.com:5000
- Instance 3: api3.example.com:5000

# Nginx configuration
upstream fakedetector {
    server api1.example.com:5000;
    server api2.example.com:5000;
    server api3.example.com:5000;
}
```

**Database/Cache Sharing**:
```python
# Shared Redis instance
redis_host = "cache.example.com"  # Shared across instances
```

### Resource Management

**Memory Optimization**:
```python
# Stream video instead of loading entirely
cap = cv2.VideoCapture(video_path)  # Reads frames on demand

# Delete intermediate data
del image_data
gc.collect()  # Force garbage collection
```

### Monitoring & Logging

```python
# Structured logging
import logging
logger = logging.getLogger(__name__)

logger.info("Analysis started", extra={
    'image_size': img.shape,
    'timestamp': datetime.now(),
    'user_id': request.remote_addr
})
```

---

**Document Version**: 1.0 | **Last Updated**: April 2026
