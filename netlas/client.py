import requests
import json
import time

from netlas.exception import APIError, ThrottlingError
from netlas.helpers import check_status_code


class Netlas:
    def __init__(
        self,
        api_key: str = "",
        apibase: str = "https://app.netlas.io",
        debug: bool = False,
    ) -> None:
        """Netlas class constructor

        :param api_key: Personal API key
        :param apibase: Netlas API server address
        :param debug: Debug flag
        """
        self.api_key: str = api_key
        self.apibase: str = apibase.rstrip("/")
        self.debug: bool = debug
        self.verify_ssl: bool = True
        if self.apibase != "https://app.netlas.io":
            self.verify_ssl = False
        self.headers = {"Content-Type": "application/json",
                        "X-Api-Key": self.api_key}

    def _request(self, endpoint: str = "/api/", params: object = {}, throttling: bool = True, retry: int = 1, method: str = 'get') -> dict:
        """Private requests wrapper.
        Sends a request to Netlas API endpoint and process result.

        :param endpoint: API endpoint
        :param params: HTTP parameters for request
        :param throttling: Wait and retry request if 429 error (Too many requests) occured, defaults to True
        :param retry: Retry count, defaults to 1
        :param method: HTTP method, defaults to GET
        :raises APIError: Failed to parse JSON response
        :raises APIError: Other HTTP error
        :raises HTTPError: Error of HTTP
        :raises ThrottlingError: Request throttled, rate-limit exceeded
        :return: parsed JSON response
        """
        ret: dict = {}
        try:
            if method.lower() == 'get':
                r = requests.get(
                    f"{self.apibase}{endpoint}",
                    params=params,
                    headers=self.headers,
                    verify=self.verify_ssl,
                )
            elif method.lower() == 'patch':
                r = requests.patch(
                    f"{self.apibase}{endpoint}",
                    json=params,
                    headers=self.headers,
                    verify=self.verify_ssl,
                )
            elif method.lower() == 'delete':
                r = requests.delete(
                    f"{self.apibase}{endpoint}",
                    params=params,
                    headers=self.headers,
                    verify=self.verify_ssl,
                )
            elif method.lower() == 'post':
                r = requests.post(
                    f"{self.apibase}{endpoint}",
                    json=params,
                    headers=self.headers,
                    verify=self.verify_ssl
                )
            else:
                raise APIError(f"HTTP method '{method.lower}' is not supported")
        except requests.HTTPError as ex:
            ret["error"] = f"{r.status_code}: {r.reason}"
            if self.debug:
                ret["error"] += "\nDescription: " + r.reason
                ret["error"] += "\nData: " + r.text
            raise ex

        try:
            check_status_code(response=r, debug=self.debug, ret=ret)
        except APIError as api_ex:
            if api_ex.type == "request_was_throttled":
                if throttling == True and retry > 0:
                    throttling_time = int(r.headers.get('Retry-after', 0))
                    if self.debug:
                        print(f"Throttling request for {throttling_time} seconds", flush=True)
                    time.sleep(throttling_time)
                    return self._request(endpoint=endpoint, params=params, throttling=throttling, retry=retry-1, method=method)
                else:
                    throttling_time = int(r.headers.get('Retry-after', 0))
                    raise ThrottlingError(retry_after=throttling_time)
            else:
                raise api_ex

        try:
            response_data = json.loads(r.text) if r.text else {}
        except json.JSONDecodeError:
            ret["error"] = "Failed to parse response data to JSON"
            if self.debug:
                ret["error"] += "\nDescription: " + r.reason
                ret["error"] += "\nData: " + r.text
            raise APIError(ret["error"])

        ret = response_data
        return ret

    def _stream_request(self, endpoint: str = "/api/", params: object = {}) -> bytes:
        """Private stream requests wrapper.
        Sends a request to Netlas API endpoint and yield data from stream.

        :param endpoint: API endpoint
        :param params: GET parameters for request
        :raises APIError: Failed to parse JSON response
        :raises APIError: Other HTTP error
        :return: Iterator of raw bytes from response
        """
        ret: dict = {}
        try:
            with requests.post(
                f"{self.apibase}{endpoint}",
                json=params,
                headers=self.headers,
                verify=self.verify_ssl,
                stream=True,
                timeout=60.0
            ) as r:
                check_status_code(response=r, debug=self.debug, ret=ret)
                for chunk in r.iter_lines():
                    # skip keep-alive chunks
                    if chunk:
                        yield chunk
        except requests.exceptions.RequestException as ex:
            try:
                ret["error"] = str(ex)
            except:
                ret["error"] = "Unexpected Stream error"
            raise APIError(ret["error"])

    def search(
        self,
        query: str,
        datatype: str = "response",
        page: int = 0,
        indices: str = "",
        fields: str = None,
        exclude_fields: bool = False,
        throttling: bool = True,
        retry: int = 1
    ) -> dict:
        """Send search query to Netlas API.

        :param query: Search query string
        :param datatype: Data type (choices: response, cert, domain, whois-ip, whois-domain)
        :param page: Page number of data
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method)
        :param fields: Comma-separated list of fields to include/exclude
        :param exclude_fields: Exclude fields from output (instead include)
        :param throttling: Wait and retry request if 429 error (Too many requests) occurred, defaults to True
        :param retry: Retry count, defaults to 1
        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises ThrottlingError: If the request is throttled and retry attempts are exhausted.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: Search query result.
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
            throttling=throttling,
            retry=retry
        )
        return ret

    query = search  # for backward compatibility

    def count(
        self,
        query: str,
        datatype: str = "response",
        indices: str = "",
        throttling: bool = True,
        retry: int = 1
    ) -> dict:
        """Calculate total count of query string results.

        :param query: Search query string
        :param datatype: Data type (choices: response, cert, domain, whois-ip, whois-domain)
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method)
        :param throttling: Wait and retry request if 429 error (Too many requests) occurred, defaults to True
        :param retry: Retry count, defaults to 1
        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises ThrottlingError: If the request is throttled and retry attempts are exhausted.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: JSON object with total count of query string results.
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
        ret = self._request(
            endpoint=endpoint,
            params={
                "q": query,
                "indices": indices
            },
            throttling=throttling,
            retry=retry
        )
        return ret

    def facet(
        self,
        query: str,
        facets: str,
        indices: str = "",
        size: int = 100,
        index_type: str = "responses",
        throttling: bool = True,
        retry: int = 1,
    ) -> dict:
        """Get statistics of responses query string results.

        :param query: Search query string
        :param group_fields: Comma-separated fields used for aggregating data
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method)
        :param size: Aggregation size
        :param index_type: Index type (choices: responses, certificates, domains)
        :param throttling: Wait and retry request if 429 error (Too many requests) occurred, defaults to True
        :param retry: Retry count, defaults to 1
        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises ThrottlingError: If the request is throttled and retry attempts are exhausted.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: JSON object with statistics of responses query string results.
        """
        endpoint = "/api/responses_facet/"
        if index_type == 'domain':
            endpoint = "/api/domains_facet/"
        elif index_type == 'whois-ip':
            endpoint = "/api/whois_ip_facet/"
        elif index_type == 'whois-domain':
            endpoint = "/api/whois_domains_facet/"
        ret = self._request(
            endpoint=endpoint,
            params={
                "q": query,
                "facets": facets,
                "size": size,
                "indices": indices,
            },
            throttling=throttling,
            retry=retry
        )
        return ret

    def profile(self) -> dict:
        """Get user profile data.

        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises ThrottlingError: If the request is throttled and retry attempts are exhausted.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: JSON object with user profile data.
        """
        endpoint = "/api/users/current/"
        ret = self._request(endpoint=endpoint)
        return ret

    def update_profile(self, first_name, last_name) -> dict:
        params = {
            "first_name": f"{first_name}",
        }
        if last_name != None:
            params["last_name"] = f"{last_name}"
        endpoint = "/api/users/current/"
        ret = self._request(endpoint=endpoint, method='patch', params=params)
        return ret

    def profile_data(self, ) -> dict:
        endpoint = "/api/users/profile_data/"
        ret = self._request(endpoint=endpoint)
        return ret

    def host(
        self,
        host: str,
        fields: str = None,
        exclude_fields: bool = False,
        throttling: bool = True,
        retry: int = 1
    ) -> dict:
        """Get full information about a host (IP or domain).

        :param host: IP or domain string
        :param fields: Comma-separated output fields. If empty, it will output all data.
        :param exclude_fields: Exclude fields from output (instead include)
        :param throttling: Wait and retry request if 429 error (Too many requests) occurred, defaults to True
        :param retry: Retry count, defaults to 1
        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises ThrottlingError: If the request is throttled and retry attempts are exhausted.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: JSON object with full information about the host.
        """
        endpoint = f"/api/host/{host}" if host else "/api/host/"
        ret = self._request(
            endpoint=endpoint,
            params={
                "fields": fields,
                "source_type": "exclude" if exclude_fields else "include"
            },
            throttling=throttling,
            retry=retry
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
        """Download data from Netlas.

        :param query: Search query string
        :param fields: Comma-separated list of fields to include/exclude
        :param exclude_fields: Exclude fields from output (instead include)
        :param datatype: Data type (choices: response, cert, domain, whois-ip, whois-domain)
        :param size: Number of documents to download
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method)
        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises ThrottlingError: If the request is throttled and retry attempts are exhausted.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: Iterator of raw data.
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

        if fields == None:  # for non-params cli download
            fields = "*"

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

    def download_all(
        self,
        query: str,
        fields: str = None,
        exclude_fields: bool = False,
        datatype: str = "response",
        indices: str = "",
    ) -> bytes:
        """Download all available data for a given query.

        :param query: Search query string
        :param fields: Comma-separated list of fields to include/exclude
        :param exclude_fields: Exclude fields from output (instead include)
        :param datatype: Data type (choices: response, cert, domain, whois-ip, whois-domain)
        :param indices: Comma-separated IDs of selected data indices (can be retrieved by `indices` method)
        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises ThrottlingError: If the request is throttled and retry attempts are exhausted.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: Iterator of raw data.
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

        if fields == None:  # for non-params cli download
            fields = "*"

        count = None
        count_res = self.count(query=query, datatype=datatype, indices=indices)
        if count_res["count"] > 0:
            count = count_res["count"]

        if count is not None:
            for ret in self._stream_request(
                endpoint=endpoint,
                params={
                    "q": query,
                    "size": count,
                    "indices": indices,
                    "raw": True,
                    "fields": fields,
                    "source_type": "exclude" if exclude_fields else "include",
                },
            ):
                yield ret
        else:
            raise APIError({
                "error": "No data is available"
            })

    def indices(self) -> list:
        """Get available data indices.

        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: List of available indices.
        """
        endpoint = "/api/indices/"
        ret = self._request(endpoint=endpoint)
        return ret

    def datasets(self) -> list:
        """Get available datasets.

        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: List of available datasets with full information.
        """
        endpoint = "/api/datastore/products/"
        ret = self._request(endpoint=endpoint)
        return ret

    def dataset_info(self, id) -> list:
        """Get info about product by `id`

        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: JSON object containing information about dataset.
        """
        endpoint = f"/api/datastore/products/{id}"
        ret = self._request(endpoint=endpoint)
        return ret

    def get_dataset_link(self, id) -> list:
        """Get the link of a dataset by its ID.

        :param id: Dataset ID
        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: JSON object containing the link and name of the dataset.
        """
        endpoint = f"/api/datastore/get_dataset_link/{id}"
        ret = self._request(endpoint=endpoint)
        return ret

    def scans(self) -> list:
        endpoint = "/api/scanner/"
        ret = self._request(endpoint=endpoint)
        return ret

    def scan_get(self, id: int):
        endpoint = f"/api/scanner/{id}/"
        ret = self._request(endpoint=endpoint)
        return ret

    def scan_create(self, targets: list[str], label: str):
        params = {
            "targets": targets.split(','),
            "label": label
        }
        endpoint = "/api/scanner/"
        ret = self._request(endpoint=endpoint, params=params, method='post')
        return ret

    def scan_rename(self, id: int, label: str):  # patch
        params = {
            "label": label
        }
        endpoint = f"/api/scanner/{id}/"
        ret = self._request(endpoint=endpoint, params=params, method='patch')
        return ret

    def scan_delete(self, id: int):  # delete
        endpoint = f"/api/scanner/{id}/"
        ret = self._request(endpoint=endpoint, method='delete')
        return ret

    def scan_bulk_delete(self, ids: list):
        params = {
            "ids": ids
        }
        endpoint = "/api/scanner/bulk_delete/"
        ret = self._request(endpoint=endpoint, method='post', params=params)
        return ret

    def scan_priority(self, id: int, shift: int):
        params = {
            "id": id,
            "shift": shift
        }
        endpoint = "/api/scanner/change_priority/"
        ret = self._request(endpoint=endpoint, params=params, method='post')
        return ret

    def mapping(self, datatype: str, is_facet: bool):
        """Get mapping of facet or default search.

        :raises APIError: If the API response contains an error or cannot be parsed.
        :raises HTTPError: If an HTTP error occurs during the request.
        :return: JSON object with all mapping for default search or facet.
        """
        if datatype == 'response':
            datatype = 'responses'
        elif datatype == 'domain':
            datatype = 'domains'
        elif datatype == 'whois-domain':
            datatype = 'whois_domains'
        elif datatype == 'whois-ip':
            datatype = 'whois_ip'
        endpoint = f"/api/mapping/{datatype}/"
        if is_facet == True:
            endpoint = endpoint = f"/api/mapping/{datatype}/facet/"
        ret = self._request(endpoint=endpoint, method='get')
        return ret

    def discovery_node_count(self, node_type, node_value):
        params = {
            "node_type": node_type,
            "node_value": node_value
        }
        endpoint = "/api/discovery/node_count/"
        ret = self._request(endpoint=endpoint, params=params, method='post')
        return ret

    def discovery_node_result(self, x_count_id, node_type, node_value, search_field_id):
        params = {
            "x_count_id": x_count_id,
            "node_type": node_type,
            "node_value": node_value,
            "search_field_id": search_field_id
        }
        endpoint = "/api/discovery/node_result/"
        ret = self._request(endpoint=endpoint, params=params, method='post')
        return ret

    def discovery_group_count(self, node_type, node_value):
        params = {
            "node_type": node_type,
            "node_value": node_value
        }
        endpoint = "/api/discovery/group_of_nodes_count/"
        ret = self._request(endpoint=endpoint, params=params, method='post')
        return ret

    def discovery_group_result(self, x_count_id, node_type, node_value, search_field_id):
        params = {
            "x_count_id": x_count_id,
            "node_type": node_type,
            "node_value": node_value,
            "search_field_id": search_field_id
        }
        endpoint = "/api/discovery/group_of_nodes_result/"
        ret = self._request(endpoint=endpoint, params=params, method='post')
        return ret

    def discovery_status(self, x_stream_id):
        endpoint = f"/api/discovery/node_count/{x_stream_id}/"
        ret = self._request(endpoint=endpoint)
        return ret
