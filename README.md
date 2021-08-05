# Netlas.io API Package

This is a Netlas.io API package with CLI tool.

[Documentation](https://netlas-python.readthedocs.io/)

## Installation

Before using Python library for Netlas.io, get [API key](https://app.netlas.io/profile/).

Installation:

```
$ pip install netlas
```

Or if you already have it installed and want to upgrade to the latest version:

```
$ pip install --upgrade netlas
```

## API usage

Simple Netlas API example. 
Send query `port:7001` to retrieve all responses available in Netlas.io with port=7001.

```
import netlas

apikey = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

netlas_connection = netlas.Netlas(api_key=apikey)
query_res = netlas_connection.query(query="port:7001")
print(netlas.helpers.dump_object(data=query_res))
```

## CLI usage

Show global help:
```
user@pc:~$ netlas --help
Usage: netlas [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  count     Calculate count of query results.
  download  Download data.
  host      Host (ip or domain) information.
  indices   Get available data indices.
  profile   Get user profile data.
  query     Search query.
  savekey   Save API key to the local system.
  stat      Get statistics for query.
```

Show specific command help:
```
user@pc:~$ netlas query --help
Usage: netlas query [OPTIONS] QUERYSTRING

  Search query.

Options:
  -d, --datatype [response|cert|domain]
                                  Query data type  [default: response]
  -a, --apikey TEXT               User API key  [required]
  -f, --format [json|yaml]        Output format  [default: yaml]
  -s, --server TEXT               Netlas API server  [default:
                                  https://app.netlas.io]

  -i, --indices TEXT              Specify comma-separated data index
                                  collections

  -h, --help                      Show this message and exit.
```

# netlas package


### class netlas.client.Netlas(api_key: str = '', apibase: str = 'https://app.netlas.io', debug: bool = False)
Bases: `object`


#### count(query: str, datatype: str = 'response', indices: str = '')
Calculate total count of query string results


* **Parameters**

    
    * **query** (*str*) – Search query string


    * **datatype** (*str**, **optional*) – Data type (choises: response, cert, domain), defaults to “response”


    * **indices** (*str**, **optional*) – Comma-separated IDs of selected data indices (can be retrieved by indices method), defaults to “”



* **Returns**

    JSON object with total count of query string results



* **Return type**

    dict



#### download(query: str, datatype: str = 'response', size: int = 10, indices: str = '')
Download data from Netlas


* **Parameters**

    
    * **query** (*str*) – Search query string


    * **datatype** (*str**, **optional*) – Data type (choises: response, cert, domain), defaults to “response”


    * **size** (*int**, **optional*) – Download documents count, defaults to 10


    * **indices** (*str**, **optional*) – Comma-separated IDs of selected data indices (can be retrieved by indices method), defaults to “”



* **Returns**

    Iterator of raw data



* **Return type**

    Iterator[bytes]



#### host(host: str, hosttype: str = 'ip', index: str = '')
Get full information about host (ip or domain)


* **Parameters**

    
    * **host** (*str*) – IP or domain string


    * **hosttype** (*str**, **optional*) – “ip” or “domain”, defaults to “ip”


    * **index** (*str**, **optional*) – ID of selected data indices (can be retrieved by indices method), defaults to “”



* **Returns**

    JSON object with full information about host



* **Return type**

    dict



#### indices()
Get available data indices


* **Returns**

    List of available indices



* **Return type**

    list



#### profile()
Get user profile data


* **Returns**

    JSON object with user profile data



* **Return type**

    dict



#### query(query: str, datatype: str = 'response', indices: str = '')
Send search query to Netlas API


* **Parameters**

    
    * **query** (*str*) – Search query string


    * **datatype** (*str**, **optional*) – Data type (choises: response, cert, domain), defaults to “response”


    * **indices** (*str**, **optional*) – Comma-separated IDs of selected data indices (can be retrieved by indices method), defaults to “”



* **Returns**

    search query result



* **Return type**

    dict



#### stat(query: str, indices: str = '')
Get statistics of responses query string results


* **Parameters**

    
    * **query** (*str*) – Search query string


    * **indices** (*str**, **optional*) – Comma-separated IDs of selected data indices (can be retrieved by indices method), defaults to “”



* **Returns**

    JSON object with statistics of responses query string results



* **Return type**

    dict


## Exception


### exception netlas.exception.APIError(value)
Bases: `Exception`

Basic Netlas.io Exception class