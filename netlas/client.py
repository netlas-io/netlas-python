import requests
import json
import yaml


class Netlas:
    debug: bool = False

    def __init__(self, api_key: str, apibase="https://app.netlas.io") -> None:
        self.api_key: str = api_key
        self.apibase: str = apibase

    def _request(self, endpoint: str = "/api/", params: object = {}) -> dict:
        ret: dict = {}
        try:
            r = requests.get(f"{self.apibase}{endpoint}",
                             params=params,
                             verify=False)
            response_data = json.loads(r.text)
        except json.JSONDecodeError:
            ret["error"] = "Failed to decode response data to JSON"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
            return ret
        except requests.HTTPError:
            ret["error"] = "HTTP error"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
            return ret
        if r.status_code == 200:
            ret["data"] = response_data
        else:
            ret["error"] = "Non 200 response code"
            if self.debug:
                ret["error_description"] = r.reason
                ret["error_data"] = r.text
        return ret

    def _return(self, data, format: str = "json"):
        if format == "json":
            return data
        elif format == "yaml":
            return yaml.safe_dump(data)
        else:
            return "Unknown output format"

    def query(self,
              query: str,
              datatype: str = "uri",
              output_format: str = "json") -> dict:
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
        return self._return(ret, format=output_format)

    def count(self,
              query: str,
              datatype: str = "uri",
              output_format: str = "json") -> dict:
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
        return self._return(ret, format=output_format)

    def stat(self, query: str, output_format: str = "json") -> dict:
        ret = self._request(
            endpoint="/api/uri_stat/",
            params={
                "q": query,
                "api_key": self.api_key
            },
        )
        return self._return(ret, format=output_format)

    def profile(self, output_format: str = "json") -> dict:
        ret = self._request(endpoint="/api/profile/",
                            params={"api_key": self.api_key})
        return self._return(ret, format=output_format)

    def host(self,
             host: str,
             hosttype: str = "ip",
             output_format: str = "json") -> dict:
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
        return self._return(ret, format=output_format)
