import requests
import orjson
import yaml
from io import TextIOWrapper

from netlas.exception import APIError
from netlas.helpers import check_status_code


class Netlas:
    def __init__(
        self,
        api_key: str = "",
        apibase: str = "https://app.netlas.io",
        debug: bool = False,
    ) -> None:
        """Netlas class constructor

        :param api_key: Personal API key, defaults to ""
        :type api_key: str
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
        self.headers = {"Content-Type": "application/json",
                        "X-Api-Key": self.api_key}

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
            r = requests.get(
                f"{self.apibase}{endpoint}",
                params=params,
                headers=self.headers,
                verify=self.verify_ssl,
            )
            response_data = orjson.loads(r.text)
        except orjson.JSONDecodeError:
            ret["error"] = "Failed to parse response data to JSON"
            if self.debug:
                ret["error"] += "\nDescription: " + r.reason
                ret["error"] += "\nData: " + r.text
        except requests.HTTPError:
            ret["error"] = f"{r.status_code}: {r.reason}"
            if self.debug:
                ret["error"] += "\nDescription: " + r.reason
                ret["error"] += "\nData: " + r.text

        if ret.get("error", None):
            raise APIError(ret["error"])
        check_status_code(request=r, debug=self.debug, ret=ret)

        ret = response_data
        return ret

    def _stream_request(self, endpoint: str = "/api/", params: object = {}) -> bytes:
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
        try:
            with requests.post(
                f"{self.apibase}{endpoint}",
                json=params,
                headers=self.headers,
                verify=self.verify_ssl,
                stream=True,
            ) as r:
                check_status_code(request=r, debug=self.debug, ret=ret)
                for chunk in r.iter_lines():
                    # skip keep-alive chunks
                    if chunk:
                        yield chunk
        except:
            ret["error"] = f"Unexpected Stream error"
            raise APIError(ret["error"])

    def search(
        self, query: str, datatype: str = "response", page: int = 0, indices: str = "", fields: str = None, exclude_fields: bool = False
    ) -> dict:
        """Send search query to Netlas API

        :param query: Search query string
        :type query: str
        :param datatype: Data type (choises: response, cert, domain, whois-ip, whois-domain), defaults to "response"
        :type datatype: str, optional
        :param page: Page number of data, defaults to 0
        :type page: int, optional
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method), defaults to ""
        :type indices: str, optional
        :param fields: Comma-separated list of fields to include/exclude, default: all fields
        :type fields: str
        :param exclude_fields: Exclude fields from output (instead include), defaults to False
        :type exclude_fields: bool
        :return: search query result
        :rtype: dict
        """
        endpoint = "/api/responses/"
        if datatype == "cert":
            endpoint = "/api/certs/"
        elif datatype == "domain":
            endpoint = "/api/domains/"
        elif datatype == "whois-ip":
            endpoint = "/api/whois_ip/"
        elif datatype == "whois-domain":
            endpoint = "/api/whois_domains/"
        ret = self._request(
            endpoint=endpoint,
            params={
                "q": query,
                "indices": indices,
                "start": page * 20,
                "fields": fields,
                "source_type": "exclude" if exclude_fields else "include"
            },
        )
        return ret

    query = search # for backward compatibility

    def count(self, query: str, datatype: str = "response", indices: str = "") -> dict:
        """Calculate total count of query string results

        :param query: Search query string
        :type query: str
        :param datatype: Data type (choises: response, cert, domain, whois-ip, whois-domain), defaults to "response"
        :type datatype: str, optional
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method), defaults to ""
        :type indices: str, optional
        :return: JSON object with total count of query string results
        :rtype: dict
        """
        endpoint = "/api/responses_count/"
        if datatype == "cert":
            endpoint = "/api/certs_count/"
        elif datatype == "domain":
            endpoint = "/api/domains_count/"
        elif datatype == "whois-ip":
            endpoint = "/api/whois_ip_count/"
        elif datatype == "whois-domain":
            endpoint = "/api/whois_domains_count/"
        ret = self._request(endpoint=endpoint, params={
                            "q": query, "indices": indices})
        return ret

    def stat(
        self,
        query: str,
        group_fields: str,
        indices: str = "",
        size: int = 100,
        index_type: str = "responses",
    ) -> dict:
        """Get statistics of responses query string results

        :param query: Search query string
        :type query: str
        :param group_fields: Comma-separated fields using for aggregate data
        :type group_fields: str
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method), defaults to ""
        :type indices: str, optional
        :param size: Aggregation size, default 100
        :type size: int
        :param index_type: Index type (choises: responses, certificates, domains), defaults to "responses"
        :type index_type: str
        :return: JSON object with statistics of responses query string results
        :rtype: dict
        """
        ret = self._request(
            endpoint="/api/stat/",
            params={
                "q": query,
                "size": size,
                "fields": group_fields,
                "index_type": index_type,
                "indices": indices,
            },
        )
        return ret

    def profile(self) -> dict:
        """Get user profile data

        :return: JSON object with user profile data
        :rtype: dict
        """
        endpoint = "/api/users/current/"
        ret = self._request(endpoint=endpoint)
        return ret

    def host(self, host: str, fields: str = None, exclude_fields: bool = False) -> dict:
        """Get full information about host (ip or domain)

        :param host: IP or domain string
        :type host: str
        :param fields: Comma-separated output fields. If empty it will output all data
        :type fields: str, optional
        :return: JSON object with full information about host
        :rtype: dict
        """
        endpoint = f"/api/host/{host}" if host else "/api/host/"
        ret = self._request(
            endpoint=endpoint,
            params={
                "fields": fields,
                "source_type": "exclude" if exclude_fields else "include"
            },
        )
        return ret

    def download(
        self,
        query: str,
        fields: str = None, 
        exclude_fields: bool = False,
        datatype: str = "response",
        size: int = 10,
        indices: str = "",
    ) -> bytes:
        """Download data from Netlas

        :param query: Search query string
        :type query: str
        :param fields: Comma-separated list of fields to include/exclude, default: all fields
        :type fields: str
        :param exclude_fields: Exclude fields from output (instead include), defaults to False
        :type exclude_fields: bool
        :param datatype: Data type (choices: response, cert, domain, whois-ip, whois-domain), defaults to "response"
        :type datatype: str, optional
        :param size: Download documents count, defaults to 10
        :type size: int, optional
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method), defaults to ""
        :type indices: list, optional
        :return: Iterator of raw data
        :rtype: Iterator[bytes]
        """
        endpoint = "/api/responses/download/"
        if datatype == "cert":
            endpoint = "/api/certs/download/"
        elif datatype == "domain":
            endpoint = "/api/domains/download/"
        elif datatype == "whois-ip":
            endpoint = "/api/whois_ip/download/"
        elif datatype == "whois-domain":
            endpoint = "/api/whois_domains/download/"

        for ret in self._stream_request(
            endpoint=endpoint,
            params={
                "q": query,
                "size": size,
                "indices": indices,
                "raw": True,
                "fields": fields,
                "source_type": "exclude" if exclude_fields else "include",
            },
        ):
            yield ret

    def indices(self) -> list:
        """Get available data indices

        :return: List of available indices
        :rtype: list
        """
        endpoint = "/api/indices/"
        ret = self._request(endpoint=endpoint)
        return ret

