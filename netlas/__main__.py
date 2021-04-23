import netlas
import click
import json
import tqdm
from netlas.helpers import dump_object
from netlas.exception import APIError

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

# Default entry point for CLI


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@main.command()
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["response", "cert", "domain"], case_sensitive=False),
    default="response",
    show_default=True,
)
@click.option(
    "-a",
    "--apikey",
    help="User API key",
    required=True,
    prompt=True,
    hide_input=True,
)
@click.option("-f",
              "--format",
              help="Output format",
              default="yaml",
              type=click.Choice(['json', 'yaml'], case_sensitive=False),
              show_default=True)
@click.argument("querystring")
@click.option("-s",
              "--server",
              help="Netlas API server",
              default="https://app.netlas.io",
              show_default=True)
@click.option("-i",
              "--indices",
              help="Specify comma-separated data index collections")
def query(datatype, apikey, format, querystring, server, indices):
    """Search query."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.query(query=querystring,
                                 datatype=datatype,
                                 indices=indices)
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["response", "cert", "domain"], case_sensitive=False),
    default="response",
    show_default=True,
)
@click.option(
    "-a",
    "--apikey",
    help="User API key",
    required=True,
    prompt=True,
    hide_input=True,
)
@click.option("-f",
              "--format",
              help="Output format",
              default="yaml",
              type=click.Choice(['json', 'yaml'], case_sensitive=False),
              show_default=True)
@click.argument("querystring")
@click.option("-s",
              "--server",
              help="Netlas API server",
              default="https://app.netlas.io",
              show_default=True)
@click.option("-i",
              "--indices",
              help="Specify comma-separated data index collections")
def count(datatype, apikey, querystring, server, format, indices):
    """Calculate count of query results."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.count(query=querystring,
                                 datatype=datatype,
                                 indices=indices)
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-a",
    "--apikey",
    help="User API key",
    required=True,
    prompt=True,
    hide_input=True,
)
@click.option("-f",
              "--format",
              help="Output format",
              default="yaml",
              type=click.Choice(['json', 'yaml'], case_sensitive=False),
              show_default=True)
@click.argument("querystring")
@click.option("-s",
              "--server",
              help="Netlas API server",
              default="https://app.netlas.io",
              show_default=True)
@click.option("-i",
              "--indices",
              help="Specify comma-separated data index collections")
def stat(apikey, querystring, server, format, indices):
    """Get statistics for query."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.stat(query=querystring, indices=indices)
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-a",
    "--apikey",
    help="User API key",
    required=True,
    prompt=True,
    hide_input=True,
)
@click.option("-f",
              "--format",
              help="Output format",
              default="yaml",
              type=click.Choice(['json', 'yaml'], case_sensitive=False),
              show_default=True)
@click.option("-s",
              "--server",
              help="Netlas API server",
              default="https://app.netlas.io",
              show_default=True)
def profile(apikey, server, format):
    """Get user profile data."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.profile()
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-t",
    "--hosttype",
    help="Query data type",
    type=click.Choice(["ip", "domain"], case_sensitive=False),
    default="ip",
    show_default=True,
)
@click.option(
    "-a",
    "--apikey",
    help="User API key",
    required=True,
    prompt=True,
    hide_input=True,
)
@click.option("-f",
              "--format",
              help="Output format",
              default="yaml",
              type=click.Choice(['json', 'yaml'], case_sensitive=False),
              show_default=True)
@click.argument("host")
@click.option("-s",
              "--server",
              help="Netlas API server",
              default="https://app.netlas.io",
              show_default=True)
@click.option("-i", "--index", help="Specify data index collection")
def host(hosttype, apikey, format, host, server, index):
    """Host (ip or domain) information"""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.host(host=host, hosttype=hosttype, index=index)
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-a",
    "--apikey",
    help="User API key",
    required=True,
    prompt=True,
    hide_input=True,
)
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["response", "cert", "domain"], case_sensitive=False),
    default="response",
    show_default=True,
)
@click.option("-c",
              "--count",
              help="Count of results",
              default=10,
              show_default=True)
@click.option("-o",
              "--output_file",
              help="Output file",
              default="out.data",
              type=click.File('wb'),
              show_default=True)
@click.argument("querystring")
@click.option("-s",
              "--server",
              help="Netlas API server",
              default="https://app.netlas.io",
              show_default=True)
@click.option("-i",
              "--indices",
              help="Specify comma-separated data index collections")
def download(apikey, datatype, count, output_file, querystring, server,
             indices):
    """Download data."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        for query_res in tqdm.tqdm(
                ns_con.download(query=querystring,
                                datatype=datatype,
                                size=count,
                                indices=indices)):
            output_file.write(query_res)
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-a",
    "--apikey",
    help="User API key",
    required=True,
    prompt=True,
    hide_input=True,
)
@click.option("-f",
              "--format",
              help="Output format",
              default="yaml",
              type=click.Choice(['json', 'yaml'], case_sensitive=False),
              show_default=True)
@click.option("-s",
              "--server",
              help="Netlas API server",
              default="https://app.netlas.io",
              show_default=True)
def indices(apikey, server, format):
    """Get available data indices."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.indices()
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


if __name__ == "__main__":
    main()
