class APIError(Exception):
    """Basic Netlas.io Exception class"""
    def __init__(self, value, description={}):
        self.value = value
        self.description: dict = description

    def __str__(self):
        return self.value


class ThrottlingError(Exception):
    def __init__(self, retry_after):
        self.retry_after = retry_after

    def __str__(self):
        return self.retry_after
