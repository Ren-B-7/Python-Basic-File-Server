"""
Custom exceptions for the file server environment.
"""

class InactivityTimeoutException(Exception):
    """Raised when server has been inactive for too long."""

class MajorThreadedHttpServerException(Exception):
    """Raised when the HTTP server encounters a critical initialization error."""

class WebSocketError(Exception):
    """Raised when WebSocket connection encounters an error."""

class LengthException(Exception):
    """Raised when content length cannot be determined or is invalid."""

class DecodeException(Exception):
    """Raised when data cannot be decoded or deserialized."""
    def __init__(self, message: str, code: int = 400):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.code}] {self.message}"

