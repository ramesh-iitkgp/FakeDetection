"""
Simplified fast deepfake detector
Returns results immediately without heavy ML dependencies
"""

import logging
import numpy as np
import cv2
from typing import Dict, Any
from PIL import Image
import os

logger = logging.getLogger(__name__)


class SimpleDetector:
    """Fast detector using basic image analysis"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_image(self, image_source: str) -> Dict[str, Any]:
        """Quick image analysis for both deepfakes and AI-generated images"""
        try:
            img = self._load_image(image_source)
            if img is None:
                return self._get_error_response()
            
            # Detect artifacts from deepfakes
            blur_score = self._detect_blur(img)
            noise_score = self._detect_noise(img)
            compression_score = self._detect_compression(img)
            deepfake_score = (blur_score + noise_score + compression_score) / 3
            
            # Detect AI-generated images
            ai_score = self._detect_ai_generated(img)
            
            # Combine scores - if either deepfake or AI detection is high, flag as fake
            confidence = float(max(deepfake_score, ai_score))
            
            # Determine risk factors
            risk_factors = []
            if deepfake_score > 0.3:
                risk_factors.append(f'Deepfake indicators: {float(deepfake_score):.1%}')
            if ai_score > 0.3:
                risk_factors.append(f'AI generation detected: {float(ai_score):.1%}')
            
            if not risk_factors:
                risk_factors.append('No significant artifacts detected')
            
            return {
                'status': 'success',
                'confidence': confidence,
                'is_deepfake': bool(confidence > 0.5),
                'face_count': 0,
                'detections': [],
                'risk_factors': risk_factors,
                'deepfake_score': float(deepfake_score),
                'ai_score': float(ai_score),
                'analysis_type': 'fast',
                'message': 'Analyzed for deepfakes and AI-generated content'
            }
        except Exception as e:
            self.logger.error(f"Error in analyze_image: {str(e)}")
            return self._get_error_response()
    
    def analyze_video(self, video_source: str, sample_frames: int = 5) -> Dict[str, Any]:
        """Quick video analysis"""
        try:
            cap = cv2.VideoCapture(video_source)
            if not cap.isOpened():
                return self._get_error_response()
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            scores = []
            frames_analyzed = 0
            
            # Sample frames
            if frame_count > 0:
                frame_indices = np.linspace(0, frame_count - 1, min(sample_frames, frame_count), dtype=int)
                
                for idx in frame_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        frame_result = self.analyze_image(frame)
                        if 'confidence' in frame_result:
                            scores.append(frame_result['confidence'])
                            frames_analyzed += 1
            
            cap.release()
            
            confidence = float(np.mean(scores)) if scores else 0.0
            
            return {
                'status': 'success',
                'confidence': float(confidence),
                'is_deepfake': bool(confidence > 0.5),
                'frame_count': int(frame_count),
                'fps': float(fps),
                'frames_analyzed': int(frames_analyzed),
                'frame_scores': [{'frame_index': int(i), 'score': float(s)} for i, s in enumerate(scores)],
                'risk_factors': ['Quick analysis performed'],
                'analysis_type': 'fast'
            }
        except Exception as e:
            self.logger.error(f"Error in analyze_video: {str(e)}")
            return self._get_error_response()
    
    def _load_image(self, image_source) -> Any:
        """Load image from file or URL"""
        try:
            if isinstance(image_source, str):
                if image_source.startswith(('http://', 'https://')):
                    # URL - skip for now
                    return None
                else:
                    # File path
                    if os.path.exists(image_source):
                        return cv2.imread(image_source)
            else:
                # Assume it's a numpy array (frame from video)
                return image_source
        except Exception as e:
            self.logger.error(f"Error loading image: {str(e)}")
        return None
    
    def _detect_blur(self, img) -> float:
        """Detect blur using Laplacian variance"""
        try:
            if img is None or len(img.shape) < 2:
                return 0.0
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-1 (lower variance = more blur)
            blur_score = float(min(1.0, max(0.0, 1.0 - (laplacian_var / 500.0))))
            return blur_score
        except:
            return 0.0
    
    def _detect_noise(self, img) -> float:
        """Detect inconsistent noise patterns"""
        try:
            if img is None or len(img.shape) < 2:
                return 0.0
            
            # Check noise variance across channels
            if len(img.shape) == 3:
                noise_vals = []
                for i in range(3):
                    channel = img[:, :, i].astype(float)
                    # Calculate local variance
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                    local_mean = cv2.filter2D(channel, -1, kernel / 25)
                    local_var = np.var(channel - local_mean)
                    noise_vals.append(local_var)
                
                # If noise is inconsistent across channels, higher score
                noise_score = float(np.std(noise_vals) / (np.mean(noise_vals) + 1e-6))
                return float(min(1.0, noise_score / 100.0))
        except:
            pass
        return 0.0
    
    def _detect_compression(self, img) -> float:
        """Detect JPEG compression artifacts"""
        try:
            if img is None or len(img.shape) < 2:
                return 0.0
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            
            # Detect block artifacts (8x8 JPEG blocks)
            h, w = gray.shape
            artifact_score = 0.0
            
            # Check for block grid patterns
            for y in range(0, h - 8, 8):
                for x in range(0, w - 8, 8):
                    block = gray[y:y+8, x:x+8]
                    # Check variance
                    if np.var(block) < 5:
                        artifact_score += 1
            
            total_blocks = ((h // 8) * (w // 8))
            if total_blocks > 0:
                compression_score = artifact_score / total_blocks
                return float(min(1.0, compression_score))
        except:
            pass
        return 0.0
    
    def _detect_ai_generated(self, img) -> float:
        """Aggressively detect AI-generated images using multiple heuristics"""
        try:
            if img is None or len(img.shape) < 2:
                return 0.0
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            
            scores = []
            
            # 1. Detect uniform/smooth regions (AI images often have too-smooth gradients)
            smoothness_score = self._analyze_smoothness(gray)
            # Boosting factors - very aggressive
            scores.append(smoothness_score * 2.0)  # Boost this detector
            
            # 2. Detect frequency domain anomalies
            freq_score = self._analyze_frequency_anomalies(gray)
            scores.append(freq_score * 2.0)  # Boost frequency analysis
            
            # 3. Detect color saturation anomalies
            if len(img.shape) == 3:
                color_score = self._analyze_color_anomalies(img)
                scores.append(color_score * 2.0)  # Boost color detection
            
            # 4. Detect edge inconsistencies
            edge_score = self._analyze_edge_inconsistencies(gray)
            scores.append(edge_score * 2.0)  # Boost edge detection
            
            # 5. Detect texture uniformity (new aggressive check)
            texture_score = self._analyze_texture_uniformity(gray)
            scores.append(texture_score * 2.0)  # Boost texture analysis
            
            # 6. NEW: Detect perfect gradient patterns
            gradient_score = self._detect_gradient_perfection(gray)
            scores.append(gradient_score * 2.0)  # NEW detector
            
            # 7. NEW: Detect color bleeding (common in AI)
            bleeding_score = self._detect_color_bleeding(img)
            scores.append(bleeding_score * 2.0)  # NEW detector
            
            # 8. NEW: Detect high frequency noise (AI often has different noise)
            noise_score = self._detect_ai_noise_pattern(gray)
            scores.append(noise_score * 2.0)  # NEW detector
            
            # Average with aggressive boosting
            ai_score = float(np.mean(scores)) if scores else 0.0
            
            # Much more aggressive boosting for agreement
            high_score_count = sum(1 for s in scores if s > 0.3)
            medium_score_count = sum(1 for s in scores if s > 0.1)
            
            if high_score_count >= 2:
                ai_score = min(1.0, ai_score * 1.8)  # 1.8x boost
            elif high_score_count >= 1 and medium_score_count >= 3:
                ai_score = min(1.0, ai_score * 1.6)  # 1.6x boost
            elif medium_score_count >= 3:
                ai_score = min(1.0, ai_score * 1.4)  # 1.4x boost
            
            return float(min(1.0, ai_score))
            
        except:
            return 0.0
    
    def _analyze_smoothness(self, gray) -> float:
        """Analyze if image has unusually smooth/uniform regions (AI trait)"""
        try:
            # Use Laplacian to detect edges
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # Count pixels with very low gradient (smooth regions)
            smooth_pixels = np.sum(np.abs(laplacian) < 10)  # Increased from 5
            total_pixels = gray.shape[0] * gray.shape[1]
            
            # AI images tend to have more smooth regions
            smoothness_ratio = smooth_pixels / total_pixels
            
            # Much more aggressive - lowered from 45% to 35%
            if smoothness_ratio > 0.35:
                return float(min(1.0, (smoothness_ratio - 0.35) * 3.0))
            return 0.0
        except:
            return 0.0
    
    def _analyze_frequency_anomalies(self, gray) -> float:
        """Analyze FFT for AI-generation patterns"""
        try:
            # Compute FFT
            dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
            dft_shift = np.fft.fftshift(dft)
            magnitude = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
            
            # Normalize
            magnitude = np.log(magnitude + 1)
            magnitude = (magnitude - magnitude.min()) / (magnitude.max() - magnitude.min() + 1e-6)
            
            # AI-generated images often have too-regular frequency patterns
            # Check for abnormal energy distribution
            h, w = magnitude.shape
            center_region = magnitude[h//4:3*h//4, w//4:3*w//4]
            outer_region = np.concatenate([
                magnitude[:h//4, :].flatten(),
                magnitude[3*h//4:, :].flatten(),
                magnitude[:, :w//4].flatten(),
                magnitude[:, 3*w//4:].flatten()
            ])
            
            # AI images have more energy in center (smooth background)
            center_energy = np.mean(center_region)
            outer_energy = np.mean(outer_region) if len(outer_region) > 0 else center_energy
            
            if outer_energy > 0:
                energy_ratio = center_energy / (outer_energy + 1e-6)
                # Much more aggressive - lowered from 1.2 to 1.0
                if energy_ratio > 1.0:
                    return float(min(1.0, (energy_ratio - 1.0) * 1.2))
            
            return 0.0
        except:
            return 0.0
    
    def _analyze_color_anomalies(self, img) -> float:
        """Analyze color distribution for AI generation markers"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Check saturation uniformity
            saturation = hsv[:, :, 1].astype(float)
            sat_std = np.std(saturation)
            sat_mean = np.mean(saturation)
            
            # AI images: higher saturation uniformity, lower variance
            # This indicates synthetic color generation
            if sat_mean > 20:  # Lowered from 30
                sat_ratio = sat_std / (sat_mean + 1e-6)
                # Much more aggressive - lowered from 0.22 to 0.18
                if sat_ratio < 0.18:
                    return float(min(1.0, (0.18 - sat_ratio) * 2.5))
            
            return 0.0
        except:
            return 0.0
    
    def _analyze_edge_inconsistencies(self, gray) -> float:
        """Analyze edge patterns for AI generation"""
        try:
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate edge density in different regions
            h, w = edges.shape
            quadrants = [
                edges[:h//2, :w//2],
                edges[:h//2, w//2:],
                edges[h//2:, :w//2],
                edges[h//2:, w//2:]
            ]
            
            # Calculate variance of edge density
            edge_densities = [np.sum(q > 0) / (q.shape[0] * q.shape[1]) for q in quadrants]
            edge_variance = np.std(edge_densities)
            
            # AI images have more consistent edge distribution (low variance)
            # Much more aggressive - lowered from 0.10 to 0.15
            if edge_variance < 0.15:
                return float(min(1.0, (0.15 - edge_variance) * 3))
            
            return 0.0
        except:
            return 0.0
    
    def _analyze_texture_uniformity(self, gray) -> float:
        """Aggressively detect overly uniform textures (strong AI trait)"""
        try:
            # Divide image into blocks and calculate texture variance
            h, w = gray.shape
            block_size = 32
            variances = []
            
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = gray[y:y+block_size, x:x+block_size]
                    # Calculate variance within block
                    var = np.var(block)
                    variances.append(var)
            
            if not variances:
                return 0.0
            
            # Calculate mean and std of variances
            var_mean = np.mean(variances)
            var_std = np.std(variances)
            
            # AI images: very uniform blocks (low variance between blocks)
            # Natural images: diverse block variances
            if var_mean > 5:  # Lowered from 10
                uniformity_ratio = var_std / var_mean
                # Much more aggressive - lowered from 0.15 to 0.20
                if uniformity_ratio < 0.20:
                    return float(min(1.0, (0.20 - uniformity_ratio) * 2.5))
            
            return 0.0
        except:
            return 0.0
    
    def _detect_gradient_perfection(self, gray) -> float:
        """Detect unnaturally perfect gradients (AI trait)"""
        try:
            # Calculate gradient with Sobel
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # AI images have smoother gradients with less variation
            # Calculate coefficient of variation of gradients
            grad_mean = np.mean(magnitude)
            grad_std = np.std(magnitude)
            
            if grad_mean > 0.5:  # Lowered from 1
                gradient_smoothness = grad_std / grad_mean
                # Much more aggressive - lowered from 0.08 to 0.12
                if gradient_smoothness < 0.12:
                    return float(min(1.0, (0.12 - gradient_smoothness) * 3.5))
            
            return 0.0
        except:
            return 0.0
    
    def _detect_color_bleeding(self, img) -> float:
        """Detect color bleeding/fringing at edges (AI generation artifact)"""
        try:
            if len(img.shape) != 3:
                return 0.0
            
            # Split channels
            b, g, r = cv2.split(img)
            
            # Find edges in each channel
            edges_b = cv2.Canny(b, 50, 150)
            edges_g = cv2.Canny(g, 50, 150)
            edges_r = cv2.Canny(r, 50, 150)
            
            # Calculate how much edges don't align between channels (color fringing)
            total_edges = np.sum(edges_b > 0) + np.sum(edges_g > 0) + np.sum(edges_r > 0)
            aligned_edges = np.sum((edges_b > 0) & (edges_g > 0) & (edges_r > 0))
            
            if total_edges > 0:
                alignment_ratio = aligned_edges / (total_edges / 3)
                # Much more aggressive - lowered from 0.5 to 0.65
                if alignment_ratio < 0.65:
                    return float(min(1.0, (0.65 - alignment_ratio) * 1.2))
            
            return 0.0
        except:
            return 0.0
    
    def _detect_ai_noise_pattern(self, gray) -> float:
        """Detect AI-specific noise patterns"""
        try:
            # Calculate local variance to detect noise
            h, w = gray.shape
            local_vars = []
            kernel_size = 5
            
            for y in range(0, h - kernel_size, kernel_size):
                for x in range(0, w - kernel_size, kernel_size):
                    patch = gray[y:y+kernel_size, x:x+kernel_size].astype(float)
                    local_vars.append(np.var(patch))
            
            if not local_vars:
                return 0.0
            
            # Calculate variance of variances
            var_of_vars = np.var(local_vars)
            mean_var = np.mean(local_vars)
            
            # AI images have more consistent noise patterns
            if mean_var > 50:  # Lowered from 100
                noise_consistency = var_of_vars / mean_var
                # Much more aggressive - lowered from 0.2 to 0.30
                if noise_consistency < 0.30:
                    return float(min(1.0, (0.30 - noise_consistency) * 1.8))
            
            return 0.0
        except:
            return 0.0
    
    def _get_error_response(self) -> Dict[str, Any]:
        """Return error response"""
        return {
            'status': 'error',
            'confidence': 0.0,
            'is_deepfake': False,
            'error': 'Could not analyze image',
            'risk_factors': []
        }
