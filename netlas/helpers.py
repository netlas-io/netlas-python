import yaml
import json
import pygments
import orjson
import appdirs
import os
from click import Option, UsageError, Group

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


class ClickAliasedGroup(Group):
    def __init__(self, *args, **kwargs):
        super(ClickAliasedGroup, self).__init__(*args, **kwargs)
        self._commands = {}
        self._aliases = {}

    def command(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super(ClickAliasedGroup, self).command(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def group(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super(ClickAliasedGroup, self).group(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def resolve_alias(self, cmd_name):
        if cmd_name in self._aliases:
            return self._aliases[cmd_name]
        return cmd_name

    def get_command(self, ctx, cmd_name):
        cmd_name = self.resolve_alias(cmd_name)
        command = super(ClickAliasedGroup, self).get_command(ctx, cmd_name)
        if command:
            return command

    def format_commands(self, ctx, formatter):
        rows = []

        sub_commands = self.list_commands(ctx)

        max_len = max(len(cmd) for cmd in sub_commands)
        limit = formatter.width - 6 - max_len

        for sub_command in sub_commands:
            cmd = self.get_command(ctx, sub_command)
            if cmd is None:
                continue
            if hasattr(cmd, 'hidden') and cmd.hidden:
                continue
            if sub_command in self._commands:
                aliases = ','.join(sorted(self._commands[sub_command]))
                sub_command = '{0} ({1})'.format(sub_command, aliases)
            cmd_help = cmd.get_short_help_str(limit)
            rows.append((sub_command, cmd_help))

        if rows:
            with formatter.section('Commands'):
                formatter.write_dl(rows)


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
