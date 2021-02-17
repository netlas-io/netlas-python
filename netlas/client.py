import requests
import json


class Netlas:
    debug: bool = False

    def __init__(self, api_key: str,
                 endpoint="https://app.netlas.io/api") -> None:
        self.api_key: str = api_key
        self.endpoint: str = endpoint

    def query(self, query: str) -> dict:
        ret: dict = {}
        params = {'q': query, 'api_key': self.api_key}
        try:
            r = requests.get(
                f"{self.endpoint}/search/", params=params)
            response_data = json.loads(r.text)
        except json.JSONDecodeError:
            ret['error'] = "Failed to decode response data to JSON"
            if self.debug:
                ret['error_description'] = r.reason
                ret['error_data'] = r.text
        except requests.HTTPError:
            ret['error'] = "HTTP error"
            if self.debug:
                ret['error_description'] = r.reason
                ret['error_data'] = r.text
        if r.status_code == 200:
            ret['data'] = response_data
        else:
            ret['error'] = "Non 200 response code"
            if self.debug:
                ret['error_description'] = r.reason
                ret['error_data'] = r.text
        return ret
