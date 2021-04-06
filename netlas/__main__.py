import netlas
import click
import json

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
    type=click.Choice(["uri", "cert", "domain"], case_sensitive=False),
    default="uri",
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
def query(datatype, apikey, format, querystring, server):
    """Search query."""
    ns_con = netlas.Netlas(api_key=apikey, apibase=server)
    query_res = ns_con.query(query=querystring,
                             output_format=format,
                             datatype=datatype)
    print(query_res)


@main.command()
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["uri", "cert", "domain"], case_sensitive=False),
    default="uri",
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
def count(datatype, apikey, querystring, server):
    """Calculate count of query results."""
    ns_con = netlas.Netlas(api_key=apikey, apibase=server)
    query_res = ns_con.count(query=querystring,
                             output_format=format,
                             datatype=datatype)
    print(query_res)


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
def stat(apikey, querystring, server):
    """Get statistics for query."""
    ns_con = netlas.Netlas(api_key=apikey, apibase=server)
    query_res = ns_con.stat(query=querystring, output_format=format)
    print(query_res)


@main.command()
@click.option(
    "-a",
    "--apikey",
    help="User API key",
    required=True,
    prompt=True,
    hide_input=True,
)
@click.option("-s",
              "--server",
              help="Netlas API server",
              default="https://app.netlas.io",
              show_default=True)
def profile(apikey, server):
    """Get user profile data."""
    ns_con = netlas.Netlas(api_key=apikey, apibase=server)
    profile = ns_con.profile()
    print(profile)


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
def host(hosttype, apikey, format, host, server):
    """Search query."""
    ns_con = netlas.Netlas(api_key=apikey, apibase=server)
    query_res = ns_con.host(host=host, output_format=format, hosttype=hosttype)
    print(query_res)


if __name__ == "__main__":
    main()
