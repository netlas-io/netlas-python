# Netlas.io API Package

This is a Netlas.io API package with CLI tool.

## API usage

Simple Netlas API example. 
Send query `port:7001` to retrieve all responses available in Netlas.io with port=7001.

```
import netlas

out_format = "yaml"
apikey = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
datatype = "response"

netlas_connection = netlas.Netlas(api_key=apikey)
query_res = netlas_connection.query(query="port:7001", datatype=datatype)
print(netlas.helpers.dump_object(data=query_res, format=format))
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
  host      Host (ip or domain) information
  profile   Get user profile data.
  query     Search query.
  stat      Get statistics for query.
```

Show specific command help:
```
user@pc:~$ netlas query --help
Usage: netlas query [OPTIONS] QUERYSTRING

  Search query.

Options:
  -d, --datatype [uri|cert|domain]
                                  Query data type  [default: uri]
  -a, --apikey TEXT               User API key  [required]
  -f, --format [json|yaml]        Output format  [default: yaml]
  -s, --server TEXT               Netlas API server  [default:
                                  https://app.netlas.io]

  -h, --help                      Show this message and exit.
```

# netlas package


### class netlas.client.Netlas(api_key: str = '', apibase: str = 'https://app.netlas.io', debug: bool = False)
Bases: `object`


#### count(query: str, datatype: str = 'response')
Calculate total count of query string results


* **Parameters**

    
    * **query** (*str*) – Search query string


    * **datatype** (*str**, **optional*) – Data type (choises: response, cert, domain), defaults to “response”



* **Returns**

    JSON object with total count of query string results



* **Return type**

    dict



#### download(query: str, datatype: str = 'response', size: int = 10)
Download data from Netlas


* **Parameters**

    
    * **query** (*str*) – Search query string


    * **datatype** (*str**, **optional*) – Data type (choises: response, cert, domain), defaults to “response”


    * **size** (*int**, **optional*) – Download documents count, defaults to 10



* **Returns**

    Iterator of raw data



* **Return type**

    Iterator[bytes]



#### host(host: str, hosttype: str = 'ip')
Get full information about host (ip or domain)


* **Parameters**

    
    * **host** (*str*) – IP or domain string


    * **hosttype** (*str**, **optional*) – “ip” or “domain”, defaults to “ip”



* **Returns**

    JSON object with full information about host



* **Return type**

    dict



#### profile()
Get user profile data


* **Returns**

    JSON object with user profile data



* **Return type**

    dict



#### query(query: str, datatype: str = 'response')
Send search query to Netlas API


* **Parameters**

    
    * **query** (*str*) – Search query string


    * **datatype** (*str**, **optional*) – Data type (choises: response, cert, domain), defaults to “response”



* **Returns**

    search query result



* **Return type**

    dict



#### stat(query: str)
Get statistics of responses query string results


* **Parameters**

    **query** (*str*) – Search query string



* **Returns**

    JSON object with statistics of responses query string results



* **Return type**

    dict


## Module contents
