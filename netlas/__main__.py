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
    type=click.Choice(["URI", "CRT", "DOM"], case_sensitive=False),
    default="URI",
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
@click.option("-p", "--pretty", help="Pretty print output", is_flag=True)
@click.argument("querystring")
def query(datatype, apikey, querystring, pretty):
    if datatype == "URI":
        ns_con = netlas.Netlas(api_key=apikey)
        query_res = ns_con.query(query=querystring)
        if pretty:
            print(json.dumps(query_res, indent=4))
        else:
            print(query_res)
    else:
        print("Sorry, this type is not supported yet")


@main.command()
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["URI", "CRT", "DOM"], case_sensitive=False),
    default="URI",
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
@click.option("-p", "--pretty", help="Pretty print output", is_flag=True)
@click.argument("querystring")
def count(datatype, apikey, querystring, pretty):
    """Calculate count of query results."""
    if datatype == "URI":
        ns_con = netlas.Netlas(api_key=apikey)
        query_res = ns_con.count(query=querystring)
        if pretty:
            print(json.dumps(query_res, indent=4))
        else:
            print(query_res)
    else:
        print("Sorry, this type is not supported yet")


@main.command()
@click.option(
    "-d",
    "--datatype",
    help="Query data type",
    type=click.Choice(["URI", "CRT", "DOM"], case_sensitive=False),
    default="URI",
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
@click.option("-p", "--pretty", help="Pretty print output", is_flag=True)
@click.argument("querystring")
def stat(datatype, apikey, querystring, pretty):
    if datatype == "URI":
        ns_con = netlas.Netlas(api_key=apikey)
        query_res = ns_con.stat(query=querystring)
        if pretty:
            print(json.dumps(query_res, indent=4))
        else:
            print(query_res)
    else:
        print("Sorry, this type is not supported yet")


if __name__ == "__main__":
    main()
