"""
DataNova - Custom Exceptions
"""


class DataNovaException(Exception):
    """Base exception for DataNova."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class FileUploadError(DataNovaException):
    """Raised when file upload fails."""
    def __init__(self, message: str = "File upload failed"):
        super().__init__(message, status_code=400)


class FileNotFoundError(DataNovaException):
    """Raised when dataset file is not found."""
    def __init__(self, message: str = "Dataset not found"):
        super().__init__(message, status_code=404)


class InvalidFileError(DataNovaException):
    """Raised when file format is invalid."""
    def __init__(self, message: str = "Invalid file format"):
        super().__init__(message, status_code=400)


class AnalysisError(DataNovaException):
    """Raised when analysis fails."""
    def __init__(self, message: str = "Analysis failed"):
        super().__init__(message, status_code=500)


class InsufficientDataError(DataNovaException):
    """Raised when data is insufficient for the requested analysis."""
    def __init__(self, message: str = "Insufficient data for this analysis"):
        super().__init__(message, status_code=400)


class MLError(DataNovaException):
    """Raised when machine learning operations fail."""
    def __init__(self, message: str = "Machine learning operation failed"):
        super().__init__(message, status_code=500)
