"""
Tests de andi.webservice.main
"""
import shlex
import sys
import andi.webservice.main as target

from typing import List


def command_split(cmd: str) -> List[str]:
    if sys.platform == "win32":
        return cmd.split()
    return shlex.split(cmd)


def test_help():
    parser = target.make_arg_parser()
    help_text = parser.format_help()
    assert "--help" in help_text
    assert "--config-file" in help_text
    assert "--version" in help_text
    assert "--dump-default-config" in help_text


def test_dump_default_config():
    command = shlex.split("--dump-default-config")
    parser = target.make_arg_parser()
    args = parser.parse_args(command)
    assert args.dump_default_config


def test_config_file(data_directory):
    config_file = data_directory / "customconfig.py"
    command = command_split(f"--config-file {config_file}")
    parser = target.make_arg_parser()
    args = parser.parse_args(command)
    assert args.config_file.mode == "r"
    assert args.config_file.name == str(config_file)
