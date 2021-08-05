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

    apikey = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    netlas_connection = netlas.Netlas(api_key=apikey)
    query_res = netlas_connection.query(query="port:7001")
    print(netlas.helpers.dump_object(data=query_res))


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
