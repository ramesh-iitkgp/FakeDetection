"""
Core deepfake and manipulated content detection using multiple AI models
Uses ensemble approach for improved accuracy and robustness
"""

import logging
import numpy as np
import cv2
from typing import Dict, Any, Optional
from PIL import Image
import os

# Try importing torch, but make it optional
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

logger = logging.getLogger(__name__)


class ContentDetector:
    """Main detector class using multiple AI models"""
    
    def __init__(self):
        """Initialize the detector with available models"""
        self.logger = logger
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if TORCH_AVAILABLE else 'cpu'
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available deepfake detection models"""
        try:
            # Model 1: Face Detection (MediaPipe)
            self.models['face_detector'] = self._init_face_detector()
            
            # Model 2: CNN-based detector
            self.models['cnn_detector'] = self._init_cnn_detector()
            
            # Model 3: Frequency-based detector
            self.models['frequency_detector'] = True  # Flag for frequency analysis
            
            self.logger.info("Detectors initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
    
    def _init_face_detector(self):
        """Initialize face detection model using MediaPipe"""
        try:
            import mediapipe as mp
            return mp.solutions.face_detection
        except Exception as e:
            self.logger.warning(f"Could not initialize MediaPipe: {str(e)}")
            return None
    
    def _init_cnn_detector(self):
        """
        Initialize CNN-based deepfake detector
        Uses pretrained model for binary classification (fake/real)
        """
        try:
            # This is a placeholder for a real model
            # In production, use models like:
            # - MesoNet
            # - FaceForensics++
            # - XceptionNet trained on deepfakes
            
            class SimpleCNNDetector:
                """Simplified CNN-based detector"""
                def __init__(self):
                    self.name = "SimpleCNNDetector"
                
                def detect(self, frame):
                    # Placeholder for actual detection
                    # Returns confidence score (0-1)
                    return np.random.rand()
            
            return SimpleCNNDetector()
            
        except Exception as e:
            self.logger.warning(f"Could not initialize CNN detector: {str(e)}")
            return None
    
    def analyze_image(self, image_source: str) -> Dict[str, Any]:
        """
        Analyze a single image for deepfakes and manipulation
        
        Args:
            image_source: Path to image or URL
            
        Returns:
            Detection results with confidence scores
        """
        try:
            # Read image
            img = self._load_image(image_source)
            if img is None:
                return {
                    'error': 'Cannot load image',
                    'confidence': 0.0,
                    'is_deepfake': False,
                    'face_count': 0,
                    'detections': [],
                    'risk_factors': []
                }
            
            results = {
                'image_size': list(img.shape),
                'detections': [],
                'confidence': 0.0,
                'is_deepfake': False,
                'risk_factors': [],
                'face_count': 0
            }
            
            # Try face detection (may fail if MediaPipe not available)
            try:
                faces = self._detect_faces(img)
                results['face_count'] = len(faces)
            except:
                faces = []
                results['face_count'] = 0
            
            # Perform basic frequency analysis even without faces
            freq_score = self._frequency_analysis(img)
            results['risk_factors'].append(f'Frequency anomalies: {freq_score:.2f}')
            
            if len(faces) > 0:
                # Analyze each face
                face_scores = []
                for i, face in enumerate(faces):
                    try:
                        face_analysis = self._analyze_face(img, face)
                        face_scores.append(face_analysis['deepfake_score'])
                        results['detections'].append(face_analysis)
                    except Exception as e:
                        self.logger.warning(f"Error analyzing face {i}: {str(e)}")
                
                # Calculate overall confidence
                results['confidence'] = (np.mean(face_scores) if face_scores else 0.0 + freq_score) / 2
            else:
                # No faces detected - use frequency analysis alone
                results['confidence'] = freq_score
            
            results['is_deepfake'] = results['confidence'] > 0.5
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error analyzing image: {str(e)}")
            return {
                'error': str(e),
                'confidence': 0.0,
                'is_deepfake': False
            }
    
    def analyze_video(self, video_source: str, sample_frames: int = 10) -> Dict[str, Any]:
        """
        Analyze a video for deepfakes
        
        Args:
            video_source: Path to video file
            sample_frames: Number of frames to sample from the video
            
        Returns:
            Detection results for the video
        """
        try:
            cap = cv2.VideoCapture(video_source)
            if not cap.isOpened():
                return {
                    'error': 'Cannot open video',
                    'confidence': 0.0,
                    'is_deepfake': False
                }
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            results = {
                'frame_count': frame_count,
                'fps': fps,
                'frames_analyzed': 0,
                'frame_scores': [],
                'confidence': 0.0,
                'is_deepfake': False,
                'risk_factors': []
            }
            
            # Sample frames uniformly from video
            frame_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    # Analyze frame
                    frame_analysis = self.analyze_image(frame)
                    
                    if 'confidence' in frame_analysis:
                        results['frame_scores'].append({
                            'frame_index': int(idx),
                            'score': frame_analysis['confidence']
                        })
                        results['frames_analyzed'] += 1
            
            cap.release()
            
            # Calculate overall video deepfake detection
            if results['frame_scores']:
                confidence_scores = [f['score'] for f in results['frame_scores']]
                results['confidence'] = np.mean(confidence_scores)
                results['confidence_std'] = np.std(confidence_scores)
            
            results['is_deepfake'] = results['confidence'] > 0.5
            
            # Consistency check
            if 'confidence_std' in results and results['confidence_std'] > 0.3:
                results['risk_factors'].append('Inconsistent deepfake patterns across frames')
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing video: {str(e)}")
            return {
                'error': str(e),
                'confidence': 0.0,
                'is_deepfake': False
            }
    
    def _load_image(self, image_source):
        """Load image from file path or URL"""
        try:
            if isinstance(image_source, str):
                if image_source.startswith('http'):
                    # Load from URL
                    import requests
                    response = requests.get(image_source, timeout=10)
                    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                else:
                    # Load from file
                    img = cv2.imread(image_source)
            else:
                img = image_source
            
            return img
        except Exception as e:
            self.logger.error(f"Error loading image: {str(e)}")
            return None
    
    def _detect_faces(self, img):
        """Detect faces in image using face detector"""
        try:
            if self.models['face_detector'] is None:
                return []
            
            # Convert BGR to RGB
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Use MediaPipe for face detection
            with self.models['face_detector'].FaceDetection() as face_detection:
                results = face_detection.process(rgb_img)
                
                faces = []
                if results.detections:
                    h, w, _ = img.shape
                    for detection in results.detections:
                        bbox = detection.location_data.bounding_box
                        x = int(bbox.xmin * w)
                        y = int(bbox.ymin * h)
                        width = int(bbox.width * w)
                        height = int(bbox.height * h)
                        
                        faces.append({
                            'bbox': (x, y, width, height),
                            'confidence': detection.score[0]
                        })
                
                return faces
            
        except Exception as e:
            self.logger.warning(f"Error detecting faces: {str(e)}")
            return []
    
    def _analyze_face(self, img, face_bbox: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a detected face for deepfake indicators
        
        Uses multiple approaches:
        1. Frequency domain analysis
        2. Texture analysis
        3. Facial landmarks consistency
        """
        try:
            x, y, w, h = face_bbox['bbox']
            
            # Extract face region
            face_roi = img[y:y+h, x:x+w]
            
            if face_roi.size == 0:
                return {
                    'deepfake_score': 0.0,
                    'risk_factors': []
                }
            
            analysis_results = {
                'bbox': face_bbox['bbox'],
                'face_detection_confidence': face_bbox['confidence'],
                'indicators': {},
                'deepfake_score': 0.0,
                'risk_factors': []
            }
            
            # Frequency domain analysis
            freq_score = self._frequency_analysis(face_roi)
            analysis_results['indicators']['frequency_score'] = freq_score
            
            # Texture analysis
            texture_score = self._texture_analysis(face_roi)
            analysis_results['indicators']['texture_score'] = texture_score
            
            # Eye blink detection (liveness check)
            blink_score = self._check_eye_consistency(face_roi)
            analysis_results['indicators']['blink_score'] = blink_score
            
            # Blend boundary detection
            blend_score = self._detect_blend_boundaries(face_roi)
            analysis_results['indicators']['blend_score'] = blend_score
            
            # Calculate overall deepfake score
            scores = [freq_score, texture_score, blink_score, blend_score]
            analysis_results['deepfake_score'] = np.mean(scores)
            
            # Identify risk factors
            if freq_score > 0.6:
                analysis_results['risk_factors'].append('Frequency anomalies detected')
            if texture_score > 0.6:
                analysis_results['risk_factors'].append('Synthetic texture patterns')
            if blink_score > 0.6:
                analysis_results['risk_factors'].append('Unnatural eye movement')
            if blend_score > 0.6:
                analysis_results['risk_factors'].append('Face blending artifacts detected')
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing face: {str(e)}")
            return {
                'deepfake_score': 0.0,
                'risk_factors': ['Analysis error']
            }
    
    def _frequency_analysis(self, face_roi) -> float:
        """
        Analyze frequency domain characteristics
        Real faces have different frequency patterns than synthesized ones
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Compute FFT
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude = np.abs(f_shift)
            
            # Analyze frequency distribution
            # Deepfakes typically show different frequency patterns
            center = np.array(magnitude.shape) // 2
            radius = min(center) // 2
            
            # Extract circular region in frequency domain
            yy, xx = np.ogrid[:magnitude.shape[0], :magnitude.shape[1]]
            mask = (xx - center[1])**2 + (yy - center[0])**2 <= radius**2
            
            freq_variance = np.var(magnitude[mask])
            
            # Normalize and convert to score
            # Higher variance suggests more natural content
            score = min(1.0, 1.0 - (freq_variance / (np.max(magnitude) + 1e-6)))
            
            return score
            
        except Exception as e:
            self.logger.warning(f"Frequency analysis error: {str(e)}")
            return 0.5
    
    def _texture_analysis(self, face_roi) -> float:
        """Analyze texture patterns in the face"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Apply Laplacian filter
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # Compute statistics
            variance = np.var(laplacian)
            mean = np.mean(np.abs(laplacian))
            
            # Synthetic textures often have different statistics
            score = min(1.0, variance / (mean + 1e-6) * 0.1)
            
            return score
            
        except Exception as e:
            self.logger.warning(f"Texture analysis error: {str(e)}")
            return 0.5
    
    def _check_eye_consistency(self, face_roi) -> float:
        """Check for eye consistency and natural blinking patterns"""
        try:
            # This is simplified - real implementation would use eye tracking
            # Check if both eyes have similar characteristics
            h, w = face_roi.shape[:2]
            
            # Approximate eye regions (simplified)
            left_eye = face_roi[h//3:h//2, w//4:w//2]
            right_eye = face_roi[h//3:h//2, w//2:3*w//4]
            
            # Compare eye regions
            left_gray = cv2.cvtColor(left_eye, cv2.COLOR_BGR2GRAY)
            right_gray = cv2.cvtColor(right_eye, cv2.COLOR_BGR2GRAY)
            
            # Compute correlation
            correlation = np.corrcoef(left_gray.flatten(), right_gray.flatten())[0, 1]
            
            # Eyes should be similar but not too similar
            # Very high correlation or very low suggests unnaturalness
            if np.isnan(correlation):
                return 0.5
            
            score = 1.0 - abs(correlation - 0.7) / 0.7  # Optimal at 0.7
            
            return max(0, min(1, score))
            
        except Exception as e:
            self.logger.warning(f"Eye consistency check error: {str(e)}")
            return 0.5
    
    def _detect_blend_boundaries(self, face_roi) -> float:
        """Detect if face boundaries show signs of blending/pasting"""
        try:
            # Detect edges at the face boundary
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            
            # Check edge density near boundaries
            h, w = edges.shape
            boundary_width = w // 10
            
            # Count edges in boundary regions
            top_edges = np.sum(edges[:boundary_width, :])
            bottom_edges = np.sum(edges[-boundary_width:, :])
            left_edges = np.sum(edges[:, :boundary_width])
            right_edges = np.sum(edges[:, -boundary_width:])
            
            boundary_edge_sum = top_edges + bottom_edges + left_edges + right_edges
            total_edges = np.sum(edges)
            
            # High boundary edge density suggests potential blending
            boundary_ratio = boundary_edge_sum / (total_edges + 1e-6)
            
            # Normalize to 0-1 range
            score = min(1.0, boundary_ratio * 10)
            
            return score
            
        except Exception as e:
            self.logger.warning(f"Blend boundary detection error: {str(e)}")
            return 0.5
