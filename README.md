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