from requests import HTTPError


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


class SDKHTTPError(Exception):
    def __init__(self, ex: HTTPError, value):
        self.value = value
        self.__response = ex.response

    def __str__(self):
        return self.value

    @property
    def status_code(self):
        return self.__response.status_code if self.__response else None

    @property
    def url(self):
        return self.__response.url if self.__response else None

    @property
    def headers(self):
        return self.__response.headers if self.__response else None

    @property
    def reason(self):
        return self.__response.reason if self.__response else None

    @property
    def request(self):
        return self.__response.request if self.__response else None

    @property
    def cookies(self):
        return self.__response.cookies if self.__response else None

    @property
    def encoding(self):
        return self.__response.encoding if self.__response else None

    @property
    def text(self):
        return self.__response.text if self.__response else None
