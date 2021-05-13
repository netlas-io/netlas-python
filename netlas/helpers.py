import yaml
import json
import pygments
import orjson

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
        try:
            error_text = orjson.loads(request.text)
            ret["error"] = error_text["error"]
        except:
            ret["error"] = f"{request.status_code}: {request.reason}"
        if debug:
            ret["error"] += "\nDescription: " + request.reason
            ret["error"] += "\nData: " + request.text
        raise APIError(ret['error'])
