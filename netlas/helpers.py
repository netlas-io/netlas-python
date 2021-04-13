import yaml
import json
import pygments

from pygments.lexers.data import YamlLexer
from pygments.formatters.terminal import TerminalFormatter


def dump_object(data, format: str = "json"):
    if format == "json":
        return json.dumps(data)
    elif format == "yaml":
        return pygments.highlight(yaml.safe_dump(data), YamlLexer(),
                                  TerminalFormatter())
    else:
        return "Unknown output format"