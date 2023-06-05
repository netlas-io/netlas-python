Getting Started
===============

Installation
------------------

Before using Python library for Netlas.io, get `API key <https://app.netlas.io/profile/>`_.

Installation:

.. code-block:: bash
	
	$ pip install netlas

Or if you already have it installed and want to upgrade to the latest version:

.. code-block:: bash
	
	$ pip install --upgrade netlas


API usage
---------

Simple Netlas API example.

Send query `port:7001` to retrieve all responses available in Netlas.io with port=7001.

.. code-block:: python

    import netlas

    apikey = "YOUR_API_KEY"

    # create new connection to Netlas
    netlas_connection = netlas.Netlas(api_key=apikey)

    # retrieve data from responses by query `port:7001`
    netlas_query = netlas_connection.query(query="port:7001")

    # iterate over data and print: IP address, port, path and protocol
    for response in netlas_query['items']:
        print(f"{response['data']['ip']}:{response['data']['port']}{response['data']['path']} [{response['data']['protocol']}]")
    pass


CLI usage
----------

Show global help:

.. code-block:: bash
	
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


Show specific command help:

.. code-block:: bash
	
    user@pc:~$ netlas query --help
    Usage: python -m netlas query [OPTIONS] QUERYSTRING

    Search query.

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
    -i, --include TEXT              Specify comma-separated fields that will be
                                    in the output NOTE: This argument is
                                    mutually exclusive with  arguments: [-e,
                                    exclude].
    -e, --exclude TEXT              Specify comma-separated fields that will be
                                    excluded from the output NOTE: This argument
                                    is mutually exclusive with  arguments:
                                    [include, -i].
    -p, --page INTEGER              Specify data page  [default: 0]
    

Bootstraping:
------------
  
You may want to registry your API key. 

.. code-block:: bash

    netlas query savekey YOUR_API_KEY


netlas as now saved your key, you can now use the CLI as such:

.. code-block:: bash

    netlas query 'THE_QUERY'
