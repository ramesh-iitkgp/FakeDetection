"""
Custom error handling for the API
"""


class APIError(Exception):
    """Custom API error class"""
    
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DetectionError(APIError):
    """Error during content detection"""
    pass


class MetadataError(APIError):
    """Error during metadata analysis"""
    pass
