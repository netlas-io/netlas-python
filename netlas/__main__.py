import netlas
import click


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# Default entry point for CLI


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@main.command()
@click.option('--datatype', help='Query data type', default="URI")
@click.option('--apikey', help='User API key', required=True)
@click.argument('querystring')
def query(datatype, apikey, querystring):
    if datatype == "URI":
        ns_con = netlas.Netlas(api_key=apikey)
        query_res = ns_con.query(query=querystring)
        print(query_res)


if __name__ == '__main__':
    main()
