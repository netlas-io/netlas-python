class APIError(Exception):
    """Basic Netlas.io Exception class"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
