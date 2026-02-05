class UserAlreadyExistsError(Exception):
    """Raised when attempting to register a user that already exists"""
    pass

class UserPatientDataError(Exception):
    """Raised when patient data is incoherent"""
    pass