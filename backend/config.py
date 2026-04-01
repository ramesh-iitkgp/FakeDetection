"""
Configuration management for the backend
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # API endpoints
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # File management
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/fakedetector')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))  # 50MB
    
    # Detection settings
    DETECTION_CONFIDENCE_THRESHOLD = float(os.getenv('DETECTION_CONFIDENCE_THRESHOLD', 0.5))
    ENABLE_FREQUENCY_ANALYSIS = os.getenv('ENABLE_FREQUENCY_ANALYSIS', 'true').lower() == 'true'
    ENABLE_METADATA_ANALYSIS = os.getenv('ENABLE_METADATA_ANALYSIS', 'true').lower() == 'true'
    ENABLE_DEEPFAKE_DETECTION = os.getenv('ENABLE_DEEPFAKE_DETECTION', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/tmp/fakedetector/logs/api.log')
    
    # Cache settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'false').lower() == 'true'
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # API settings
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    
    # External APIs
    ROBOFLOW_API_KEY = os.getenv('ROBOFLOW_API_KEY', '')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    
    # CORS
    CORS_ORIGINS = ['*']


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    CORS_ORIGINS = [
        'https://fakedetector.example.com',
        'chrome-extension://*'
    ]


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    UPLOAD_FOLDER = '/tmp/fakedetector_test'


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration object"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
