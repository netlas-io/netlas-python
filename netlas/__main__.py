import netlas
import click
import appdirs
import os
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, MofNCompleteColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.style import Style
from netlas.helpers import ClickAliasedGroup, MutuallyExclusiveOption, dump_object, get_api_key
from netlas.exception import APIError, ThrottlingError

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
         index_type, disable_colors):
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
def profile(apikey, server, format, disable_colors):
    """Get user profile data."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.profile()
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
def list_datasets(apikey, server, format, disable_colors):
    """Get available datasets."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        query_res = ns_con.datasets()
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
    "--label",
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
def create_scan(apikey, server, format, targets, label, disable_colors):
    """Create scan."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.scan_create(targets=targets, label=label)
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
    "--label",
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
def rename_scan(apikey, server, format, id, label, disable_colors):
    """Rename scan."""
    try:
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.scan_rename(id=id, label=label)
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
    help="ID of scan",
    required=True
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
        ns_con = netlas.Netlas(api_key=apikey, apibase=server)
        res = ns_con.scan_delete(id=id)
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


if __name__ == "__main__":
    main()
