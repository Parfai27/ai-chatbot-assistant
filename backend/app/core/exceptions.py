class ValidationError(Exception):
    status_code = 400
    message = "Validation failed"

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)


class NotFoundError(Exception):
    status_code = 404
    message = "Resource not found"

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)


class ServiceError(Exception):
    status_code = 503
    message = "Service temporarily unavailable"

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)


class AuthenticationError(Exception):
    status_code = 401
    message = "Authentication required"

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)
