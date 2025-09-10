class ServiceError(Exception):
    """Base exception for all service-related errors"""
    pass

class VideoUnavailable(ServiceError):
    """Exception raised when video service is unavailable"""
    pass