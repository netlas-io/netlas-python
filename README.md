# Netlas.io Python SDK

This repository contains Netlas.io Python SDK package with CLI Tool.

**Netlas Python SDK**

The __Netlas Python SDK__ is a software development kit provided by the Netlas team to facilitate the integration of Netlas services into Python applications. The SDK provides a convenient way to interact with the API, performing tasks such as queries, routing and parsing the JSON responses from the Netlas API into Python objects, simplifying the process of integrating Netlas data into Python projects.

**Netlas CLI Tool**

To access Netlas using the command line interface, the Netlas team has developed the __Netlas CLI Tool__. With it, you can use Netlas just like any other command line application.

## Installation

Use the Python package installer to install the SDK and CLI Tool:

``` bash
pip install netlas
```

Or if you already have it installed and want to upgrade to the latest version:

``` bash
pip install --upgrade netlas
```

If you only need the CLI tool (without the SDK), use the Homebrew package manager:

``` bash
brew tap netlas-io/netlas 
brew install netlas
```

To update homebrew installation to the latest version:

``` bash
brew update  
brew upgrade netlas
```

## Checking the installation

Now you can interact with the Netlas platform using command line. Try to get information about your external IP address:

``` bash
netlas host -a "YOUR_API_KEY"
```

❓ [Where to find API key &rarr;](https://docs.netlas.io/automation/how_to_get_api_key/)

## Setting up API Key

There are two ways of API key usage when you work with Netlas CLI (command line interface). The first way is to enter the key each time you enter a command with the `-a` option. Another way is to save the key using `savekey` command.

``` bash
netlas savekey "YOUR_API_KEY"
```

## CLI Usage

Please refer to the built-in help for command and option information. To show help page:

```` bash
netlas --help
````
``` { class="no-copy" }
Usage: netlas [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  count           Calculate count of query results.
  datastore       Manage products in the datastore.
  download        Download data.
  host            Host (ip or domain) information.
  indices         Get available data indices.
  profile         Get user profile data.
  savekey         Save API key to the local system.
  search (query)  Search query.
  stat            Get statistics for query.
```

To view specific command help use `--help` key with `netlas command`, e.g.:

```` bash
netlas count --help
````
``` { class="no-copy" }
Usage: netlas count [OPTIONS] QUERYSTRING

  Calculate count of query results.

Options:
  -d, --datatype [response|cert|domain|whois-ip|whois-domain]
                                  Query data type  [default: response]
  -a, --apikey TEXT               User API key (can be saved to system using
                                  command `netlas savekey`)
  -f, --format [json|yaml]        Output format  [default: yaml]
  --server TEXT                   Netlas API server  [default:
                                  https://app.netlas.io]
  --indices TEXT                  Specify comma-separated data index
                                  collections
  -h, --help                      Show this message and exit.
```

Here are a few examples of CLI usage:

- Equivalent to [https://app.netlas.io/host/1.1.1.1/](https://app.netlas.io/host/1.1.1.1/)
  ``` bash
  netlas host "1.1.1.1"			
  ```
- Equivalent to [https://app.netlas.io/responses/?q=host%3A1.1.1.1](https://app.netlas.io/responses/?q=host%3A1.1.1.1)
  ``` bash
  netlas search "host:1.1.1.1"
  ```
- Equivalent to [https://app.netlas.io/domains/?q=domain%3A%2A.netlas.io](https://app.netlas.io/domains/?q=domain%3A%2A.netlas.io)
  ``` bash
  netlas search --datatype domain "domain:*.netlas.io"
  ```

You can find more bash examples on the [Netlas Docs &rarr;](https://docs.netlas.io/automation/).

## Python SDK Usage

The following code sample routes the request `port:7001` to the Netlas response search and prints search results to stdout.

``` python
import netlas

# you can access saved API key using this helper
apikey = netlas.helpers.get_api_key()

# create new connection to Netlas
netlas_connection = netlas.Netlas(api_key=apikey)

# retrieve data from responses by query `port:7001`
netlas_query = netlas_connection.query(query="port:7001")

# iterate over data and print: IP address, port, path and protocol
for response in netlas_query['items']:
    print(f"{response['data']['ip']}:{response['data']['port']}{response['data']['path']} [{response['data']['protocol']}]")
pass
```

Please keep in mind that the example is simplified. When developing automation, it is necessary at least to provide procedures for exception handling. And it is also necessary to take into account that the API key may not be saved.

You can find more Python examples on the [Netlas Docs &rarr;](https://docs.netlas.io/automation/).

