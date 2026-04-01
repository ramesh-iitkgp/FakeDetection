"""
Metadata Analysis for detecting manipulated content
Analyzes EXIF data, compression artifacts, noise patterns, and other metadata
"""

import logging
from typing import Dict, Any
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import exifread
import os

logger = logging.getLogger(__name__)


class MetadataAnalyzer:
    """Analyzes metadata and physical properties of images/videos"""
    
    def __init__(self):
        """Initialize the metadata analyzer"""
        self.logger = logger
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image metadata and properties
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            results = {
                'exif_analysis': self._analyze_exif(image_path),
                'compression_analysis': self._analyze_compression(image_path),
                'noise_analysis': self._analyze_noise(image_path),
                'inconsistency_analysis': self._analyze_inconsistencies(image_path),
                'anomaly_score': 0.0,
                'is_suspicious': False
            }
            
            # Calculate overall anomaly score
            scores = [
                results['exif_analysis'].get('suspicion_score', 0),
                results['compression_analysis'].get('suspicion_score', 0),
                results['noise_analysis'].get('suspicion_score', 0),
                results['inconsistency_analysis'].get('suspicion_score', 0)
            ]
            
            results['anomaly_score'] = sum(scores) / len(scores) if scores else 0
            results['is_suspicious'] = results['anomaly_score'] > 0.6
            results['confidence'] = results['anomaly_score']
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing image metadata: {str(e)}")
            return {
                'error': str(e),
                'anomaly_score': 0.5,
                'confidence': 0.5
            }
    
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        Analyze video metadata
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            results = {
                'frame_count': 0,
                'frame_rate': 0,
                'frame_metadata': [],
                'anomaly_score': 0.0,
                'is_suspicious': False
            }
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {'error': 'Cannot open video file', 'anomaly_score': 0.5}
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            results['frame_count'] = frame_count
            results['frame_rate'] = fps
            
            # Sample frames for analysis
            sample_indices = np.linspace(0, frame_count - 1, min(5, frame_count), dtype=int)
            
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    # Analyze individual frame
                    frame_analysis = self._analyze_compression_array(frame)
                    results['frame_metadata'].append({
                        'frame_index': int(idx),
                        'compression_score': frame_analysis.get('suspicion_score', 0)
                    })
            
            cap.release()
            
            # Calculate overall video metadata anomaly score
            if results['frame_metadata']:
                scores = [f['compression_score'] for f in results['frame_metadata']]
                results['anomaly_score'] = sum(scores) / len(scores)
            
            results['is_suspicious'] = results['anomaly_score'] > 0.6
            results['confidence'] = results['anomaly_score']
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing video metadata: {str(e)}")
            return {
                'error': str(e),
                'anomaly_score': 0.5,
                'confidence': 0.5
            }
    
    def _analyze_exif(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze EXIF metadata for tampering signs
        
        Signs of manipulation:
        - Missing EXIF data
        - Inconsistent timestamps
        - Modified or removed GPS data
        - Camera model mismatches
        """
        try:
            results = {
                'exif_present': False,
                'exif_stripped': False,
                'suspicious_fields': [],
                'suspicion_score': 0.0
            }
            
            with open(image_path, 'rb') as f:
                exif_tags = exifread.process_file(f, details=False)
            
            if not exif_tags:
                results['exif_present'] = False
                results['exif_stripped'] = True
                results['suspicion_score'] = 0.3  # Moderate suspicion
            else:
                results['exif_present'] = True
                
                # Check for inconsistencies
                suspicious_indicators = 0
                
                # Check if EXIF modification time differs from file creation
                creation_time = exif_tags.get('EXIF DateTimeOriginal')
                modification_time = exif_tags.get('EXIF DateTimeDigitized')
                
                if creation_time and modification_time:
                    if str(creation_time) != str(modification_time):
                        results['suspicious_fields'].append('Timestamp mismatch')
                        suspicious_indicators += 1
                
                # Check for GPS inconsistencies
                gps_latitude = exif_tags.get('GPS GPSLatitude')
                gps_longitude = exif_tags.get('GPS GPSLongitude')
                
                if (gps_latitude and not gps_longitude) or (gps_longitude and not gps_latitude):
                    results['suspicious_fields'].append('Incomplete GPS data')
                    suspicious_indicators += 1
                
                # Check software field
                software = exif_tags.get('Image Software')
                if software and 'photoshop' in str(software).lower():
                    results['suspicious_fields'].append('Edited with Photoshop')
                    suspicious_indicators += 0.3
                
                results['suspicion_score'] = min(suspicious_indicators * 0.2, 1.0)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing EXIF: {str(e)}")
            return {
                'exif_present': False,
                'error': str(e),
                'suspicion_score': 0.5
            }
    
    def _analyze_compression(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze compression artifacts and quality inconsistencies
        
        Signs of manipulation:
        - Uniform JPEG artifacts in patched areas
        - Double JPEG compression boundaries
        - Inconsistent quality levels
        """
        try:
            img = Image.open(image_path)
            
            results = {
                'format': img.format,
                'has_double_compression': False,
                'suspicious_areas': 0,
                'suspicion_score': 0.0
            }
            
            # Convert to numpy array for analysis
            img_array = np.array(img)
            
            if len(img_array.shape) == 3:
                # Analyze compression patterns
                suspicion = self._analyze_compression_array(img_array)
                results['suspicion_score'] = suspicion.get('suspicion_score', 0)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing compression: {str(e)}")
            return {
                'error': str(e),
                'suspicion_score': 0.3
            }
    
    def _analyze_compression_array(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze compression artifacts in image array"""
        try:
            # Detect compression blocking artifacts
            # JPEG blocks are typically 8x8 pixels
            
            # Apply Laplacian filter to detect edges
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Detect 8x8 block boundaries
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # Check for periodic patterns (compression artifacts)
            frequency_spectrum = np.abs(np.fft.fft2(laplacian))
            
            # Calculate anomaly in frequency domain
            mean_freq = np.mean(frequency_spectrum)
            std_freq = np.std(frequency_spectrum)
            
            # Anomalies indicate potential compression artifacts
            anomaly_score = min(std_freq / (mean_freq + 1e-6) * 0.1, 1.0)
            
            return {
                'suspicion_score': anomaly_score,
                'detection_method': 'compression_artifacts'
            }
            
        except Exception as e:
            logger.error(f"Error in compression array analysis: {str(e)}")
            return {'suspicion_score': 0.3}
    
    def _analyze_noise(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze noise patterns and inconsistencies
        
        Signs of manipulation:
        - Inconsistent noise levels between regions
        - Gaussian vs. natural noise mismatch
        - Noise reduction artifacts
        """
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return {'error': 'Cannot read image', 'suspicion_score': 0.3}
            
            # Analyze noise in different regions
            h, w = img.shape
            region_size = min(h, w) // 4
            
            noise_variances = []
            
            # Sample noise from corners (usually less edited)
            for y in [0, h - region_size]:
                for x in [0, w - region_size]:
                    region = img[y:y+region_size, x:x+region_size].astype(float)
                    # Laplacian variance as noise measure
                    laplacian = cv2.Laplacian(region.astype(np.uint8), cv2.CV_64F)
                    variance = np.var(laplacian)
                    noise_variances.append(variance)
            
            # Check for inconsistent noise levels
            if noise_variances:
                mean_variance = np.mean(noise_variances)
                variance_of_variance = np.var(noise_variances)
                
                # High variance in noise levels indicates inconsistency
                suspicion_score = min(variance_of_variance / (mean_variance + 1e-6) * 0.1, 1.0)
            else:
                suspicion_score = 0.3
            
            return {
                'noise_variance': float(np.mean(noise_variances)) if noise_variances else 0,
                'noise_consistency': 1 - suspicion_score,
                'suspicion_score': suspicion_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing noise: {str(e)}")
            return {
                'error': str(e),
                'suspicion_score': 0.3
            }
    
    def _analyze_inconsistencies(self, image_path: str) -> Dict[str, Any]:
        """
        Detect visual inconsistencies that suggest manipulation
        
        Signs:
        - Lighting inconsistencies
        - Shadow misalignment
        - Perspective distortions
        - Color space inconsistencies
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'Cannot read image', 'suspicion_score': 0.3}
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Analyze color distribution consistency
            h_hist = cv2.calcHist([hsv], [0], None, [256], [0, 256])
            s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
            v_hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])
            
            # Calculate entropy as measure of color consistency
            h_entropy = self._calculate_entropy(h_hist)
            s_entropy = self._calculate_entropy(s_hist)
            v_entropy = self._calculate_entropy(v_hist)
            
            # High entropy variance indicates potential inconsistency
            entropy_variance = np.var([h_entropy, s_entropy, v_entropy])
            suspicion_score = min(entropy_variance / 10, 1.0)
            
            return {
                'color_consistency_score': 1 - suspicion_score,
                'entropy_variance': float(entropy_variance),
                'suspicion_score': suspicion_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing inconsistencies: {str(e)}")
            return {
                'error': str(e),
                'suspicion_score': 0.3
            }
    
    @staticmethod
    def _calculate_entropy(histogram):
        """Calculate entropy of a histogram"""
        hist = histogram.flatten() / histogram.sum()
        hist = hist[hist > 0]
        if len(hist) == 0:
            return 0
        return -np.sum(hist * np.log2(hist))
