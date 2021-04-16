import requests
import orjson
import yaml
from io import TextIOWrapper

from netlas.exception import APIError


class Netlas:
    def __init__(self,
                 api_key: str = "",
                 apibase: str = "https://app.netlas.io",
                 debug: bool = False) -> None:
        """Netlas class constructor

        :param api_key: Personal API key, defaults to ""
        :type api_key: str, optional
        :param apibase: Netlas API server address, defaults to "https://app.netlas.io"
        :type apibase: str, optional
        :param debug: Debug flag, defaults to False
        :type debug: bool, optional
        """
        self.api_key: str = api_key
        self.apibase: str = apibase.rstrip("/")
        self.debug: bool = debug
        self.verify_ssl: bool = True
        if self.apibase != "https://app.netlas.io":
            self.verify_ssl = False
        self.headers = {'Content-Type': 'application/json'}

    def _request(self, endpoint: str = "/api/", params: object = {}) -> dict:
        """Private requests wrapper.
        Sends a request to Netlas API endpoint and process result.

        :param endpoint: API endpoint, defaults to "/api/"
        :type endpoint: str
        :param params: GET parameters for request, defaults to {}
        :type params: object, optional
        :raises APIError: Failed to parse JSON response
        :raises APIError: Other HTTP error
        :return: parsed JSON response
        :rtype: dict
        """
        ret: dict = {}
        try:
            if self.api_key == "":
                ret["error"] = "API key is empty"
                raise APIError(ret['error'])

            r = requests.get(f"{self.apibase}{endpoint}",
                             params=params,
                             headers=self.headers,
                             verify=self.verify_ssl)
            response_data = orjson.loads(r.text)
        except orjson.JSONDecodeError:
            ret["error"] = "Failed to parse response data to JSON"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
        except requests.HTTPError:
            ret["error"] = f"{r.status_code}: {r.reason}"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
        if r.status_code != 200:
            ret["error"] = f"{r.status_code}: {r.reason}"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text

        if ret.get('error', None):
            raise APIError(ret['error'])

        ret = response_data
        return ret

    def _stream_request(self,
                        endpoint: str = "/api/",
                        params: object = {}) -> bytes:
        """Private stream requests wrapper.
        Sends a request to Netlas API endpoint and yield data from stream.

        :param endpoint: API endpoint, defaults to "/api/"
        :type endpoint: str
        :param params: GET parameters for request, defaults to {}
        :type params: object, optional
        :raises APIError: Failed to parse JSON response
        :raises APIError: Other HTTP error
        :return: Iterator of raw bytes from response
        :rtype: Iterator[bytes]
        """
        ret: dict = {}
        if self.api_key == "":
            ret["error"] = "API key is empty"
            raise APIError(ret['error'])
        try:
            with requests.get(f"{self.apibase}{endpoint}",
                              params=params,
                              headers=self.headers,
                              verify=self.verify_ssl,
                              stream=True) as r:
                for chunk in r.iter_content(chunk_size=2048):
                    if r.status_code != 200:
                        ret["error"] = f"{r.status_code}: {r.reason}"
                        if self.debug:
                            ret["error_description"] = r.reason
                            ret["error_data"] = r.text
                        raise APIError(ret['error'])
                    #skip keep-alive chunks
                    if chunk:
                        yield chunk
        except requests.HTTPError:
            ret["error"] = f"{r.status_code}: {r.reason}"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
            raise APIError(ret['error'])

    def query(self, query: str, datatype: str = "response") -> dict:
        """Send search query to Netlas API

        :param query: Search query string
        :type query: str
        :param datatype: Data type (choises: response, cert, domain), defaults to "response"
        :type datatype: str, optional
        :return: search query result
        :rtype: dict
        """
        endpoint = "/api/responses/"
        if datatype == "cert":
            endpoint = "/api/certs/"
        elif datatype == "domain":
            endpoint = "/api/domains/"
        ret = self._request(
            endpoint=endpoint,
            params={
                "q": query,
                "api_key": self.api_key
            },
        )
        return ret

    def count(self, query: str, datatype: str = "response") -> dict:
        """Calculate total count of query string results

        :param query: Search query string
        :type query: str
        :param datatype: Data type (choises: response, cert, domain), defaults to "response"
        :type datatype: str, optional
        :return: JSON object with total count of query string results
        :rtype: dict
        """
        endpoint = "/api/responses_count/"
        if datatype == "cert":
            endpoint = "/api/certs_count/"
        elif datatype == "domain":
            endpoint = "/api/domains_count/"
        ret = self._request(
            endpoint=endpoint,
            params={
                "q": query,
                "api_key": self.api_key
            },
        )
        return ret

    def stat(self, query: str) -> dict:
        """Get statistics of responses query string results

        :param query: Search query string
        :type query: str
        :return: JSON object with statistics of responses query string results
        :rtype: dict
        """
        ret = self._request(
            endpoint="/api/responses_stat/",
            params={
                "q": query,
                "api_key": self.api_key
            },
        )
        return ret

    def profile(self) -> dict:
        """Get user profile data

        :return: JSON object with user profile data
        :rtype: dict
        """
        ret = self._request(endpoint="/api/profile/",
                            params={"api_key": self.api_key})
        return ret

    def host(self, host: str, hosttype: str = "ip") -> dict:
        """Get full information about host (ip or domain)

        :param host: IP or domain string
        :type host: str
        :param hosttype: `"ip"` or `"domain"`, defaults to "ip"
        :type hosttype: str, optional
        :return: JSON object with full information about host
        :rtype: dict
        """
        endpoint = "/api/ip/"
        if hosttype == "domain":
            endpoint = "/api/domain/"
        ret = self._request(
            endpoint=endpoint,
            params={
                "q": host,
                "api_key": self.api_key
            },
        )
        return ret

    def download(self,
                 query: str,
                 datatype: str = "response",
                 size: int = 10) -> bytes:
        """Download data from Netlas

        :param query: Search query string
        :type query: str
        :param datatype: Data type (choises: response, cert, domain), defaults to "response"
        :type datatype: str, optional
        :param size: Download documents count, defaults to 10
        :type size: int, optional
        :return: Iterator of raw data
        :rtype: Iterator[bytes]
        """
        endpoint = "/api/responses/download/"
        if datatype == "cert":
            endpoint = "/api/certs/download/"
        elif datatype == "domain":
            endpoint = "/api/domains/download/"
        for ret in self._stream_request(
                endpoint=endpoint,
                params={
                    "q": query,
                    "size": size,
                    "api_key": self.api_key
                },
        ):
            yield ret