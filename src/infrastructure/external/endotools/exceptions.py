class ExternalAPIError(Exception):
    """Base exception for external API errors"""
    pass


class ExternalAPITimeoutError(ExternalAPIError):
    """Raised when API request times out"""
    pass


class ExternalAPINotFoundError(ExternalAPIError):
    """Raised when resource is not found (404)"""
    pass


class ExternalAPIAuthenticationError(ExternalAPIError):
    """Raised when authentication fails (401)"""
    pass


class ExternalAPIPermissionError(ExternalAPIError):
    """Raised when permission is denied (403)"""
    pass


class ExternalAPIServerError(ExternalAPIError):
    """Raised when server error occurs (5xx)"""
    pass
