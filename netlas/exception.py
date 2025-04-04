class APIError(Exception):
    """Basic Netlas.io Exception class"""

    def __init__(self, value="", err_type="", detail=""):
        self.value = value
        self.type = err_type
        self.title = value
        self.detail = detail

    def __str__(self):
        return self.value


class ThrottlingError(Exception):
    """
    Exception raised when a throttling limit is encountered.

    Attributes:
        retry_after (int): The amount of time (in seconds) to wait before retrying.
    """

    def __init__(self, retry_after: int):
        """
        Initialize the ThrottlingError.

        Args:
            retry_after (int): The time to wait before retrying, in seconds.
        """
        self.retry_after = retry_after

    def __str__(self):
        """Return the retry time in seconds as a string."""
        return str(self.retry_after)
