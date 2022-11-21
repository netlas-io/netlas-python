import netlas
import click
import appdirs
import os
from netlas.helpers import ClickAliasedGroup, MutuallyExclusiveOption, dump_object, get_api_key
from netlas.exception import APIError

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

# Default entry point for CLI


@click.group(context_settings=CONTEXT_SETTINGS, cls=ClickAliasedGroup)
def main():
    pass


@main.command()
@click.argument("api_key")
@click.option(
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
def savekey(api_key, server):
    """Save API key to the local system."""
    config_path = appdirs.user_config_dir(appname="netlas")
    key_file = "netlas.key"
    if not os.path.isdir(config_path):
        try:
            os.makedirs(config_path)
        except OSError:
            print(
                dump_object(
                    APIError(
                        f"Can't create Netlas config directory: {config_path}")
                ))
            return
    api_key = api_key.strip()
    if api_key.isalnum():
        try:
            ns_con = netlas.Netlas(api_key=api_key, apibase=server)
            query_res = ns_con.profile()
            with open(f"{config_path}{os.path.sep}{key_file}",
                      "w") as h_key_file:
                h_key_file.write(api_key)
                print("API key successfully saved")
        except APIError as ex:
            print(dump_object(ex))
    else:
        print(dump_object(APIError("Wrong API key format")))
        return


@main.command(aliases=['query'])
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["response", "cert", "domain", "whois-ip", "whois-domain"], case_sensitive=False),
    default="response",
    show_default=True,
)
@click.option(
    "-a",
    "--apikey",
    help="User API key (can be saved to system using command `netlas savekey`)",
    required=False,
    default=lambda: get_api_key(),
)
@click.option(
    "-f",
    "--format",
    help="Output format",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    show_default=True,
)
@click.argument("querystring")
@click.option(
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option("--indices",
              help="Specify comma-separated data index collections")
@click.option("-i",
              "--include",
              required=False,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["exclude", "-e"],
              help="Specify comma-separated fields that will be in the output")
@click.option("-e",
              "--exclude",
              required=False,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["include", "-i"],
              help="Specify comma-separated fields that will be excluded from the output")
@click.option("-p",
              "--page",
              type=int,
              default=0,
              show_default=True,
              help="Specify data page")
def search(datatype, apikey, format, querystring, server, indices, include, exclude, page):
    """Search query."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.search(query=querystring,
                                 datatype=datatype,
                                 page=page,
                                 indices=indices,
                                 fields=include if include else exclude,
                                 exclude_fields=True if exclude else False)
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["response", "cert", "domain", "whois-ip", "whois-domain"], case_sensitive=False),
    default="response",
    show_default=True,
)
@click.option(
    "-a",
    "--apikey",
    help="User API key (can be saved to system using command `netlas savekey`)",
    required=False,
    default=lambda: get_api_key(),
)
@click.option(
    "-f",
    "--format",
    help="Output format",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    show_default=True,
)
@click.argument("querystring")
@click.option(
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option("--indices",
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
    help="User API key (can be saved to system using command `netlas savekey`)",
    required=False,
    default=lambda: get_api_key(),
)
@click.option(
    "-f",
    "--format",
    help="Output format",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    show_default=True,
)
@click.argument("querystring")
@click.option(
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option(
    "-g",
    "--group_fields",
    required=True,
    help="Comma-separated fields using for aggregate data",
)
@click.option("-s",
              "--size",
              default=100,
              show_default=True,
              help="Aggregation size")
@click.option(
    "-t",
    "--index_type",
    default="responses",
    show_default=True,
    type=click.Choice(["responses", "certificates", "domains"],
                      case_sensitive=False),
    help="Index type",
)
@click.option("--indices",
              help="Specify comma-separated data index collections")
def stat(apikey, querystring, server, format, indices, group_fields, size,
         index_type):
    """Get statistics for query."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.stat(
            query=querystring,
            group_fields=group_fields,
            indices=indices,
            size=size,
            index_type=index_type,
        )
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-a",
    "--apikey",
    help="User API key (can be saved to system using command `netlas savekey`)",
    required=False,
    default=lambda: get_api_key(),
)
@click.option(
    "-f",
    "--format",
    help="Output format",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    show_default=True,
)
@click.option(
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
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
    "-a",
    "--apikey",
    help="User API key (can be saved to system using command `netlas savekey`)",
    required=False,
    default=lambda: get_api_key(),
)
@click.option(
    "-f",
    "--format",
    help="Output format",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    show_default=True,
)
@click.argument("host", required=False, default=None)
@click.option(
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option("-i",
              "--include",
              required=False,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["exclude", "-e"],
              help="Specify comma-separated fields that will be in the output")
@click.option("-e",
              "--exclude",
              required=False,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["include", "-i"],
              help="Specify comma-separated fields that will be excluded from the output")
def host(apikey, format, host, server, include, exclude):
    """Host (ip or domain) information."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.host(host=host, 
                                fields=include if include else exclude,
                                exclude_fields=True if exclude else False)
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-a",
    "--apikey",
    help="User API key (can be saved to system using command `netlas savekey`)",
    required=True,
    default=lambda: get_api_key(),
)
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["response", "cert", "domain", "whois-ip", "whois-domain"], case_sensitive=False),
    default="response",
    show_default=True,
)
@click.option("-i",
              "--include",
              required=False,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["exclude", "-e"],
              help="Specify comma-separated fields that will be in the output")
@click.option("-e",
              "--exclude",
              required=False,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["include", "-i"],
              help="Specify comma-separated fields that will be excluded from the output")
@click.option("-c",
              "--count",
              help="Count of results",
              default=10,
              show_default=True)
@click.option(
    "-o",
    "--output_file",
    help="Output file (stdout by default)",
    default="-",
    type=click.File("wb"),
    show_default=True,
)
@click.argument("querystring")
@click.option(
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option("--indices",
              help="Specify comma-separated data index collections")
def download(
    apikey,
    datatype,
    count,
    output_file,
    querystring,
    server,
    indices,
    include,
    exclude,
):
    """Download data."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        for i, query_res in enumerate(
                ns_con.download(
                    query=querystring,
                    datatype=datatype,
                    size=count,
                    indices=indices,
                    fields=include if include else exclude,
                    exclude_fields=True if exclude else False,
                )):
            if i > 0:
                output_file.write(b"\n")
            output_file.write(query_res)
        print("\n")
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-a",
    "--apikey",
    help="User API key (can be saved to system using command `netlas savekey`)",
    required=False,
    default=lambda: get_api_key(),
)
@click.option(
    "-f",
    "--format",
    help="Output format",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    show_default=True,
)
@click.option(
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
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
