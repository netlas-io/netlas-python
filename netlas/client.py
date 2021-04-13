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
        self.api_key: str = api_key
        self.apibase: str = apibase.rstrip("/")
        self.debug: bool = debug
        self.verify_ssl: bool = True
        if self.apibase != "https://app.netlas.io":
            verify = False

    def _request(self, endpoint: str = "/api/", params: object = {}) -> dict:
        ret: dict = {}
        try:
            if self.api_key == "":
                ret["error"] = "API key is empty"

            r = requests.get(f"{self.apibase}{endpoint}",
                             params=params,
                             verify=self.verify_ssl)
            response_data = orjson.loads(r.text)
        except orjson.JSONDecodeError:
            ret["error"] = "Failed to parse response data to JSON"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
        except requests.HTTPError:
            ret["error"] = "HTTP error"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
        if r.status_code != 200:
            ret["error"] = "Non 200 response code"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text

        if ret.get('error', None):
            raise APIError(ret['error'])

        ret = response_data
        return ret

    def _stream_request(self,
                        file_name: str,
                        endpoint: str = "/api/",
                        params: object = {}) -> dict:
        ret: dict = {}
        if self.api_key == "":
            ret["error"] = "API key is empty"
        try:
            with requests.get(f"{self.apibase}{endpoint}",
                              params=params,
                              verify=self.verify_ssl,
                              stream=True) as r:
                with open(file_name, "wb") as out_file:
                    for chunk in r.iter_lines(chunk_size=2048):
                        #skip keep-alive chunks
                        if chunk:
                            out_file.write(chunk)
        except requests.HTTPError:
            ret["error"] = "HTTP error"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
        if r.status_code == 200:
            ret["competed"] = True
        else:
            ret["error"] = "Non 200 response code"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
        if ret.get('error', None):
            raise APIError(ret['error'])
        return ret

    def query(self, query: str, datatype: str = "uri") -> dict:
        endpoint = "/api/uri/"
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

    def count(self, query: str, datatype: str = "uri") -> dict:
        endpoint = "/api/uri_count/"
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
        ret = self._request(
            endpoint="/api/uri_stat/",
            params={
                "q": query,
                "api_key": self.api_key
            },
        )
        return ret

    def profile(self) -> dict:
        ret = self._request(endpoint="/api/profile/",
                            params={"api_key": self.api_key})
        return ret

    def host(self, host: str, hosttype: str = "ip") -> dict:
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
                 file_name: str,
                 datatype: str = "uri",
                 size: int = 10) -> dict:
        endpoint = "/api/uri/download"
        if datatype == "cert":
            endpoint = "/api/certs/download"
        elif datatype == "domain":
            endpoint == "/api/domains/download"
        ret = self._stream_request(
            file_name=file_name,
            endpoint=endpoint,
            params={
                "q": query,
                "size": size,
                "api_key": self.api_key
            },
        )
        return ret