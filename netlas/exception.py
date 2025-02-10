class APIError(Exception):
    """Basic Netlas.io Exception class"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class ThrottlingError(Exception):
    def __init__(self, retry_after):
        self.retry_after = retry_after

    def __str__(self):
        return self.retry_after
