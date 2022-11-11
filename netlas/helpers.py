import yaml
import json
import pygments
import orjson
import appdirs
import os
from click import Option, UsageError

from requests import Request
from pygments.lexers.data import YamlLexer
from pygments.formatters.terminal import TerminalFormatter

from netlas.exception import APIError


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class MutuallyExclusiveOption(Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help + (
                ' NOTE: This argument is mutually exclusive with '
                ' arguments: [' + ex_str + '].'
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )


def dump_object(data, format: str = "json"):
    if type(data).__name__ == "APIError":
        return bcolors.FAIL + str(data) + bcolors.ENDC
    if format == "json":
        return json.dumps(data)
    elif format == "yaml":
        return pygments.highlight(yaml.safe_dump(data), YamlLexer(),
                                  TerminalFormatter())
    else:
        return "Unknown output format"


def check_status_code(request: Request, debug: bool = False, ret: dict = {}):
    if request.status_code != 200:
        if request.status_code == 401:
            ret["error"] = "Account required"
        elif request.status_code == 402:
            ret["error"] = "Insufficiently amount of Netlas Coins"
        elif request.status_code == 403:
            ret["error"] = "Account restrictions. Upgrade account to make this request"
        elif request.status_code == 429:
            ret["error"] = "Request limit"
        else:
            try:
                error_text = orjson.loads(request.text)
                ret["error"] = error_text["error"]
            except:
                ret["error"] = f"{request.status_code}: {request.reason}"
        if debug:
            ret["error"] += "\nDescription: " + request.reason
            ret["error"] += "\nData: " + request.text
        raise APIError(ret['error'])


def get_api_key():
    key_file_name = "netlas.key"
    key_file_path = f'{appdirs.user_config_dir(appname="netlas")}{os.path.sep}{key_file_name}'
    try:
        with open(key_file_path, 'r') as key_file:
            api_key = key_file.readline()
            api_key = api_key.strip()
            if api_key.isalnum():
                return api_key
    except:
        return None
    return None
