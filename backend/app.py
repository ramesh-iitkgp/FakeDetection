"""
Fake Content Detection System - Flask Backend
Advanced AI-powered system for detecting deepfakes and manipulated media
"""

import os
from flask import Flask, request, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from werkzeug.utils import secure_filename
import uuid
import numpy as np
import json

from utils.detector import ContentDetector
from utils.metadata_analyzer import MetadataAnalyzer
from utils.error_handler import APIError
from utils.simple_detector import SimpleDetector


class NumpyEncoder(DefaultJSONProvider):
    """Custom JSON encoder for numpy types"""
    def default(self, o):
        if isinstance(o, (np.integer, np.floating)):
            return float(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.json = NumpyEncoder(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/fakedetector')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'mp4', 'avi', 'mov', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize detectors
content_detector = SimpleDetector()
metadata_analyzer = MetadataAnalyzer()

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - welcome message"""
    return jsonify({
        'status': 'online',
        'service': 'Fake Content Detection System',
        'version': '1.0.0',
        'endpoints': {
            'health': 'GET /health',
            'analyze_image': 'POST /api/v1/analyze/image',
            'analyze_video': 'POST /api/v1/analyze/video',
            'analyze_batch': 'POST /api/v1/analyze/batch'
        },
        'docs': 'See README.md for full API documentation'
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Fake Content Detection System',
        'version': '1.0.0'
    })


@app.route('/api/v1/analyze/image', methods=['POST'])
def analyze_image():
    """
    Analyze an image for fake/manipulated content
    
    Expects:
    - file: Image file (multipart/form-data)
    - url: Image URL (optional, if not sending file)
    
    Returns:
    - Detection results with confidence scores
    - Metadata analysis
    - Overall risk assessment
    """
    try:
        image_data = None
        image_path = None
        
        # Handle file upload or URL
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                raise APIError('No file selected', 400)
            
            if not allowed_file(file.filename):
                raise APIError(f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}', 400)
            
            # Save the file
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_path)
            image_data = image_path
            
        elif 'url' in request.json:
            image_data = request.json.get('url')
        else:
            raise APIError('Either file or URL must be provided', 400)
        
        # Analyze the image
        detection_results = content_detector.analyze_image(image_data)
        metadata_results = metadata_analyzer.analyze_image(image_data)
        
        # Combine results
        overall_risk = calculate_overall_risk(detection_results, metadata_results)
        
        response = {
            'status': 'success',
            'analysis_id': str(uuid.uuid4()),
            'content_type': 'image',
            'detection_results': detection_results,
            'metadata_results': metadata_results,
            'overall_risk': overall_risk,
            'confidence': (detection_results.get('confidence', 0) + 
                          metadata_results.get('confidence', 0)) / 2
        }
        
        # Cleanup
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
        return jsonify(response), 200
        
    except APIError as e:
        return jsonify({'status': 'error', 'message': e.message}), e.status_code
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@app.route('/api/v1/analyze/video', methods=['POST'])
def analyze_video():
    """
    Analyze a video for fake/manipulated content
    
    Expects:
    - file: Video file (multipart/form-data)
    - url: Video URL (optional)
    - sample_frames: Number of frames to sample (default: 10)
    
    Returns:
    - Frame-by-frame detection results
    - Audio analysis
    - Overall verdict
    """
    try:
        video_data = None
        video_path = None
        sample_frames = request.json.get('sample_frames', 10) if request.json else 10
        
        # Handle file upload or URL
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                raise APIError('No file selected', 400)
            
            if not allowed_file(file.filename):
                raise APIError(f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}', 400)
            
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            video_data = video_path
            
        elif 'url' in request.json:
            video_data = request.json.get('url')
        else:
            raise APIError('Either file or URL must be provided', 400)
        
        # Analyze the video
        detection_results = content_detector.analyze_video(video_data, sample_frames)
        metadata_results = metadata_analyzer.analyze_video(video_data)
        
        # Combine results
        overall_risk = calculate_overall_risk(detection_results, metadata_results)
        
        response = {
            'status': 'success',
            'analysis_id': str(uuid.uuid4()),
            'content_type': 'video',
            'frame_count': detection_results.get('frame_count', 0),
            'frames_analyzed': detection_results.get('frames_analyzed', 0),
            'detection_results': detection_results,
            'metadata_results': metadata_results,
            'overall_risk': overall_risk,
            'confidence': (detection_results.get('confidence', 0) + 
                          metadata_results.get('confidence', 0)) / 2
        }
        
        # Cleanup
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        
        return jsonify(response), 200
        
    except APIError as e:
        return jsonify({'status': 'error', 'message': e.message}), e.status_code
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@app.route('/api/v1/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Batch analyze multiple images
    
    Expects:
    - files: List of image files (multipart/form-data)
    
    Returns:
    - Results for each analyzed image
    """
    try:
        if 'files' not in request.files:
            raise APIError('No files provided', 400)
        
        files = request.files.getlist('files')
        if len(files) == 0:
            raise APIError('No files selected', 400)
        
        results = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                try:
                    detection = content_detector.analyze_image(file_path)
                    metadata = metadata_analyzer.analyze_image(file_path)
                    risk = calculate_overall_risk(detection, metadata)
                    
                    results.append({
                        'filename': file.filename,
                        'detection_results': detection,
                        'metadata_results': metadata,
                        'overall_risk': risk
                    })
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        return jsonify({
            'status': 'success',
            'total_files': len(files),
            'analyzed': len(results),
            'results': results
        }), 200
        
    except APIError as e:
        return jsonify({'status': 'error', 'message': e.message}), e.status_code
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


def calculate_overall_risk(detection_results, metadata_results):
    """
    Calculate overall risk score based on multiple analyses
    
    Risk levels: low, medium, high, critical
    """
    detection_score = detection_results.get('confidence', 0)
    ai_score = detection_results.get('ai_score', 0)
    metadata_score = metadata_results.get('anomaly_score', 0)
    
    # Use maximum of detection and AI scores, heavily weighted
    # If either AI or deepfake is detected strongly, flag it
    combined_score = max(detection_score, ai_score * 1.1)
    
    # Also consider metadata
    combined_score = max(combined_score, metadata_score * 0.9)
    
    # If AI score > 0.4, boost to guarantee high risk
    if ai_score > 0.4:
        combined_score = max(combined_score, 0.65)
    
    # If AI score > 0.35 AND detection shows signs, boost further
    if ai_score > 0.35 and detection_score > 0.2:
        combined_score = max(combined_score, 0.60)
    
    if combined_score >= 0.8:
        return {'level': 'critical', 'score': combined_score}
    elif combined_score >= 0.6:
        return {'level': 'high', 'score': combined_score}
    elif combined_score >= 0.4:
        return {'level': 'medium', 'score': combined_score}
    else:
        return {'level': 'low', 'score': combined_score}


@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle custom API errors"""
    return jsonify({'status': 'error', 'message': error.message}), error.status_code


@app.errorhandler(413)
def request_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'status': 'error',
        'message': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f}MB'
    }), 413


if __name__ == '__main__':
    # Development server
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=debug
    )
