import netlas
import click
import appdirs
import os
from netlas.helpers import dump_object, get_api_key
from netlas.exception import APIError

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

# Default entry point for CLI


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@main.command()
@click.argument("api_key")
@click.option(
    "-s",
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
    "-s",
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option("-i",
              "--indices",
              help="Specify comma-separated data index collections")
@click.option("-p",
              "--page",
              type=int,
              default=0,
              show_default=True,
              help="Specify data page")
def query(datatype, apikey, format, querystring, server, indices, page):
    """Search query."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.query(query=querystring,
                                 datatype=datatype,
                                 page=page,
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
    "-s",
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
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
    "-s",
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
@click.option("-l",
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
@click.option("-i",
              "--indices",
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
    "-s",
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
    "-s",
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option(
    "-l",
    "--fields",
    help="Comma-separated output fields. Default all fields",
    default=None,
)
def host(apikey, format, host, server, fields):
    """Host (ip or domain) information."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.host(host=host, fields=fields)
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
    type=click.Choice(["response", "cert", "domain"], case_sensitive=False),
    default="response",
    show_default=True,
)
@click.option(
    "-f",
    "--fields",
    help="Comma-separated data of fields to include/exclude",
)
@click.option(
    "-st",
    "--source_type",
    help="Include or exclude fields",
    type=click.Choice(["include", "exclude"], case_sensitive=False),
    default="exclude",
    show_default=True,
)
@click.option("-c",
              "--count",
              help="Count of results",
              default=10,
              show_default=True)
@click.option(
    "-o",
    "--output_file",
    help="Output file",
    default="out.data",
    type=click.File("wb"),
    show_default=True,
)
@click.argument("querystring")
@click.option(
    "-s",
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option("-i",
              "--indices",
              help="Specify comma-separated data index collections")
def download(
    apikey,
    datatype,
    count,
    output_file,
    querystring,
    server,
    indices,
    fields,
    source_type,
):
    """Download data."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        c_bytes: int = 0
        fields = list() if not fields else fields.split(",")
        for i, query_res in enumerate(
                ns_con.download(
                    query=querystring,
                    datatype=datatype,
                    size=count,
                    indices=indices,
                    fields=fields,
                    source_type=source_type,
                )):
            if i > 0:
                output_file.write(b"\n")
            output_file.write(query_res)
            c_bytes += len(query_res)
            print(f"{c_bytes} bytes has been written to {output_file.name}",
                  end="\r")
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
    "-s",
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
    "-s",
    "--server",
    help="Netlas API server",
    default="https://app.netlas.io",
    show_default=True,
)
@click.option("-i",
              "--indices",
              help="Specify comma-separated data index collections")
@click.option("-p",
              "--page",
              type=int,
              default=0,
              show_default=True,
              help="Specify data page")
def whois_ip(apikey, format, querystring, server, indices, page):
    """Get WHOIS IP data."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.whois_ip(query=querystring,
                                    page=page,
                                    indices=indices)
        print(dump_object(data=query_res, format=format))
    except APIError as ex:
        print(dump_object(ex))


if __name__ == "__main__":
    main()
