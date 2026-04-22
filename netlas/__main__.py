import netlas
import click
import appdirs
import os
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, MofNCompleteColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.style import Style
from rich.console import Console
from netlas.helpers import ClickAliasedGroup, MutuallyExclusiveOption, dump_object, get_api_key
from netlas.exception import APIError, ThrottlingError
from time import sleep

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

# Default entry point for CLI


@click.group(context_settings=CONTEXT_SETTINGS, cls=ClickAliasedGroup)
@click.version_option()
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
    type=click.Choice(["response", "cert", "domain", "whois-ip",
                      "whois-domain"], case_sensitive=False),
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
@click.option("--no-color",
              "disable_colors",
              is_flag=True,
              default=False,
              help="Disable output colors")
def search(datatype, apikey, format, querystring, server, indices, include, exclude, page, disable_colors):
    """Search query."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.search(query=querystring,
                                  datatype=datatype,
                                  page=page,
                                  indices=indices,
                                  fields=include if include else exclude,
                                  exclude_fields=True if exclude else False)
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@main.command()
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["response", "cert", "domain", "whois-ip",
                      "whois-domain"], case_sensitive=False),
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
@click.option("--indices",
              help="Specify comma-separated data index collections")
def count(datatype, apikey, querystring, server, format, indices, disable_colors):
    """Calculate count of query results."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.count(query=querystring,
                                 datatype=datatype,
                                 indices=indices)
        print(dump_object(query_res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@main.command(aliases=['facet'])
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
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
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
    default="response",
    show_default=True,
    type=click.Choice(["response", "whois-domain", "domain", "whois-ip"],
                      case_sensitive=False),
    help="Index type",
)
@click.option("--indices",
              help="Specify comma-separated data index collections")
def stat(apikey, querystring, server, format, indices, group_fields, size,
         index_type, disable_colors):
    """Get statistics for query."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.stat(
            query=querystring,
            facets=group_fields,
            indices=indices,
            size=size,
            index_type=index_type,
        )
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@main.group()
def profile():
    """Manage user profile."""
    pass


@profile.command("info")
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def profile_info(apikey, server, format, disable_colors):
    """Get user profile data."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.profile()
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@profile.command("update")
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
@click.option(
    "--first",
    "first_name",
    required=True,
    help="First name for profile.",
)
@click.option(
    "--last",
    "last_name",
    default=None,
    required=False,
    help="Last name for profile.",
)
def update_profile(apikey, server, format, disable_colors, first_name, last_name):
    """Update user profile."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.update_profile(first_name=first_name, last_name=last_name)
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@profile.command("counters")
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def counters_profile(apikey, server, format, disable_colors):
    """Update user profile."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.profile_data()
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
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
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
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
def host(apikey, format, host, server, include, exclude, disable_colors):
    """Host (ip or domain) information."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.host(host=host,
                                fields=include if include else exclude,
                                exclude_fields=True if exclude else False)
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
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
    type=click.Choice(["response", "cert", "domain", "whois-ip",
                      "whois-domain"], case_sensitive=False),
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
              help="Download specific count of data",
              default=10,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["all"],
              show_default=True)
@click.option("--all",
              "all_",
              help="Download all available data",
              is_flag=True,
              default=False,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["count", "-c"],
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
    all_,
    output_file,
    querystring,
    server,
    indices,
    include,
    exclude
):
    """Download data of specific query."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        if all_:
            count_res = ns_con.count(
                query=querystring, datatype=datatype, indices=indices)
            if count_res["count"] > 0:
                count = count_res["count"]
        progress = None
        downloaded_docs_count = 0
        if output_file.name != "<stdout>":
            bar_style = Style(color="bright_white", blink=False, bold=True)
            bar_complete_style = Style(
                color="dodger_blue1", blink=False, bold=True)
            bar_finished_style = Style(
                color="dodger_blue2", blink=False, bold=True)
            progress = Progress(SpinnerColumn(style=bar_finished_style),
                                TextColumn(
                                    "[progress.description]{task.description}"),
                                BarColumn(
                                    style=bar_style, finished_style=bar_finished_style, complete_style=bar_complete_style),
                                TaskProgressColumn(),
                                TimeRemainingColumn(),
                                MofNCompleteColumn())
            pg_bar = progress.add_task(
                "[dodger_blue1]Downloading...", total=count)
            progress.start()
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
            downloaded_docs_count = i + 1
            if progress:
                progress.update(pg_bar, advance=1)

        if progress:
            progress.update(pg_bar,
                            total=downloaded_docs_count,
                            description="[dodger_blue2]Completed     ",
                            completed=downloaded_docs_count,
                            refresh=True)
            progress.stop()
        else:
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def indices(apikey, server, format, disable_colors):
    """Get available data indices."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.indices()
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@main.group()
def datastore():
    """Manage products in the datastore."""
    pass


@datastore.command("list")
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
@click.argument("id", required=False)
def list_datasets(apikey, server, format, disable_colors, id):
    """Get available datasets."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        if id == None:
            query_res = ns_con.datasets()
        else:
            query_res = ns_con.dataset_info(id=id)
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@datastore.command("get")
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
@click.argument(
    'id',
    type=int,
    required=True
)
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def get_dataset(apikey, server, format, id, disable_colors):
    """Get the link of a dataset by its ID."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.get_dataset_link(id=id)
        print(dump_object(data=query_res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@main.group()
def scanner():
    """Manage scans."""
    pass


@scanner.command("list")
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def list_scans(apikey, server, format, disable_colors):
    """List all existing private scans."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.scans()
        print(dump_object(data=res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@scanner.command("get")
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
@click.argument(
    'id',
    type=int,
    required=True
)
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def scan_get(apikey, server, format, id, disable_colors):
    """Get info about scan."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.scan_get(id=id)
        print(dump_object(data=res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@scanner.command("create")
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
@click.option(
    "--targets",
    help="Targets to scan.",
    required=True,
    type=str
)
@click.option(
    "--name",
    help="Name of new scan.",
    required=True
)
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def create_scan(apikey, server, format, targets, name, disable_colors):
    """Create scan."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.scan_create(targets=targets, name=name)
        print(dump_object(data=res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@scanner.command("rename")
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
@click.option(
    "--id",
    help="ID of scan",
    required=True
)
@click.option(
    "--name",
    help="New of scan name.",
    required=True
)
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def rename_scan(apikey, server, format, id, name, disable_colors):
    """Rename scan."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.scan_rename(id=id, name=name)
        print(dump_object(data=res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@scanner.command("delete")
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
@click.option(
    "--id",
    help="ID/IDs of scan, comma-separated",
    required=True,
)
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def delete_scan(apikey, server, format, id, disable_colors):
    """Delete scan of `id`."""
    try:
        ids = id.split(',')
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        if len(ids) > 1:
            res = ns_con.scan_bulk_delete(ids=ids)
        else:
            res = ns_con.scan_delete(id=ids[0])
        print(dump_object(data=res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@scanner.command("priority")
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
@click.option(
    "--id",
    help="ID of scan",
    type=int,
    required=True
)
@click.option(
    "--shift",
    help="Priority number",
    type=int,
    required=True
)
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def priority_scan(apikey, server, format, id, shift, disable_colors):
    """Change priority scan of `id`."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.scan_priority(id=id, shift=shift)
        print(dump_object(data=res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@scanner.command("report")
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
@click.option(
    "--id",
    help="ID of scan",
    required=True,
    type=int,
)
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
def report_scan(apikey, server, format, id, disable_colors):
    """Get report scan of `id`."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.get_scan_report(id=id)
        print(dump_object(data=res, format=format, disable_colors=disable_colors))
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
@click.option(
    "--facet",
    "is_facet",
    is_flag=True,
    default=False,
    help="Choose mapping type",
)
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["response", "domain", "whois-ip",
                      "whois-domain"], case_sensitive=False),
    default="response",
    show_default=True,
)
def mapping(apikey, server, format, disable_colors, is_facet, datatype):
    """Get mapping of index type."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.mapping(datatype=datatype, is_facet=is_facet)
        print(dump_object(data=res, format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@main.group()
def discovery():
    """Attack Surface Discovery methods."""
    pass


@discovery.command("searches")
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
@click.option(
    "-t",
    "--node-type",
    "node_type",
    help="Type of node to search",
    default="domain",
    type=click.Choice(["address", "as_name", "asn", "dns_txt", "domain", "email", "favicon", "http_tracker", "ip", "ip-range", "jarm", "network_name", "organization", "person", "phone", "text"], case_sensitive=False),
    show_default=True,
    required=True,
)
@click.argument("node_value", required=True)
@click.option(
    "--disable-status",
    is_flag=True,
    default=False,
    help="Disable progress status output",
)
def discovery_searches(apikey, server, format, disable_colors, node_value, node_type, disable_status):
    """Retrieve a list of available searches for a node/group of nodes."""
    try:
        records = [v.strip() for v in node_value.split(",") if v.strip()]
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)

        if len(records) > 1:
            query_res = ns_con.discovery_group_count(node_type=node_type, node_value=records)
        else:
            query_res = ns_con.discovery_node_count(node_type=node_type, node_value=node_value)

        x_stream_id = query_res.get("x_stream_id")

        if x_stream_id and not disable_status:
            bar_style = Style(color="bright_white", blink=False, bold=True)
            bar_complete_style = Style(color="dodger_blue1", blink=False, bold=True)
            bar_finished_style = Style(color="dodger_blue2", blink=False, bold=True)

            progress = Progress(
                SpinnerColumn(style=bar_finished_style),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(
                    style=bar_style,
                    finished_style=bar_finished_style,
                    complete_style=bar_complete_style,
                ),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=Console(stderr=True),
                transient=True,
            )

            task_id = progress.add_task("[dodger_blue1]Preparing searches...", total=100)
            progress.start()

            last_percentage = -1

            while True:
                status_res = ns_con.discovery_status(x_stream_id=x_stream_id)
                status_data = status_res.get("data", {})

                percentage = status_data.get("percentage", 0) or 0
                message = status_data.get("message", "Processing")
                status = (status_data.get("status") or "").lower()

                if percentage != last_percentage:
                    progress.update(
                        task_id,
                        completed=percentage,
                        description=f"[dodger_blue1]{message}",
                        refresh=True,
                    )
                    last_percentage = percentage

                if status in {"done", "completed", "success", "finished"} or percentage >= 100:
                    break

                if status in {"failed", "error"}:
                    progress.stop()
                    raise APIError(message)

                sleep(0.5)

            progress.update(
                task_id,
                completed=100,
                description="[dodger_blue2]Completed     ",
                refresh=True,
            )
            progress.stop()

        print(dump_object(data=query_res["data"], format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


@discovery.command("fetch")
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
@click.option(
    "--no-color",
    "disable_colors",
    is_flag=True,
    default=False,
    help="Disable output colors",
)
@click.option(
    "-t",
    "--node-type",
    "node_type",
    help="Type of node to search",
    default="domain",
    type=click.Choice(["address", "as_name", "asn", "dns_txt", "domain", "email", "favicon", "http_tracker", "ip", "ip-range", "jarm", "network_name", "organization", "person", "phone", "text"], case_sensitive=False),
    show_default=True,
)
@click.argument(
    "node_value",
    required=True,
)
@click.argument(
    "search_id",
    required=True,
    type=int,
)
@click.option(
    "--disable-status",
    is_flag=True,
    default=False,
    help="Disable progress status output",
)
def discovery_fetch(apikey, server, format, disable_colors, node_value, search_id, node_type, disable_status):
    """Execute a search for a node/group and retrieve the corresponding results."""
    try:
        records = [v.strip() for v in node_value.split(",") if v.strip()]
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)

        if len(records) > 1:
            count_res = ns_con.discovery_group_count(node_type=node_type, node_value=records)
        else:
            count_res = ns_con.discovery_node_count(node_type=node_type, node_value=node_value)

        x_count_id = count_res.get("x_count_id")
        x_stream_id = count_res.get("x_stream_id")

        if not x_count_id:
            raise APIError("X-Count-Id header was not returned by discovery count")

        progress = None
        task_id = None

        if not disable_status:
            bar_style = Style(color="bright_white", blink=False, bold=True)
            bar_complete_style = Style(color="dodger_blue1", blink=False, bold=True)
            bar_finished_style = Style(color="dodger_blue2", blink=False, bold=True)

            progress = Progress(
                SpinnerColumn(style=bar_finished_style),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(
                    style=bar_style,
                    finished_style=bar_finished_style,
                    complete_style=bar_complete_style,
                ),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=Console(stderr=True),
                transient=True,
            )

            task_id = progress.add_task("[dodger_blue1]Preparing search...", total=100)
            progress.start()

        if x_stream_id and not disable_status:
            last_percentage = -1

            while True:
                status_res = ns_con.discovery_status(x_stream_id=x_stream_id)
                status_data = status_res.get("data", {})

                percentage = status_data.get("percentage", 0) or 0
                message = status_data.get("message", "Processing")
                status = (status_data.get("status") or "").lower()

                if percentage != last_percentage:
                    progress.update(
                        task_id,
                        completed=percentage,
                        description=f"[dodger_blue1]{message}",
                        refresh=True,
                    )
                    last_percentage = percentage

                if status in {"done", "completed", "success", "finished"} or percentage >= 100:
                    break

                if status in {"failed", "error"}:
                    progress.stop()
                    raise APIError(message)

                sleep(0.5)

        if len(records) > 1:
            result_res = ns_con.discovery_group_result(
                x_count_id=x_count_id,
                node_type=node_type,
                node_value=records,
                search_field_id=search_id,
            )
        else:
            result_res = ns_con.discovery_node_result(
                x_count_id=x_count_id,
                node_type=node_type,
                node_value=node_value,
                search_field_id=search_id,
            )

        x_stream_id = result_res.get("x_stream_id")

        if x_stream_id and not disable_status:
            progress.update(
                task_id,
                completed=0,
                description="[dodger_blue1]Executing search...",
                refresh=True,
            )

            last_percentage = -1

            while True:
                status_res = ns_con.discovery_status(x_stream_id=x_stream_id)
                status_data = status_res.get("data", {})

                percentage = status_data.get("percentage", 0) or 0
                message = status_data.get("message", "Processing")
                status = (status_data.get("status") or "").lower()

                if percentage != last_percentage:
                    progress.update(
                        task_id,
                        completed=percentage,
                        description=f"[dodger_blue1]{message}",
                        refresh=True,
                    )
                    last_percentage = percentage

                if status in {"done", "completed", "success", "finished"} or percentage >= 100:
                    break

                if status in {"failed", "error"}:
                    progress.stop()
                    raise APIError(message)

                sleep(0.5)

        if progress is not None:
            progress.update(
                task_id,
                completed=100,
                description="[dodger_blue2]Completed     ",
                refresh=True,
            )
            progress.stop()

        print(dump_object(data=result_res["data"], format=format, disable_colors=disable_colors))
    except APIError as ex:
        print(dump_object(ex))


if __name__ == "__main__":
    main()
