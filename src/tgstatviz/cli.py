"""
TODO: докстринг модуля
"""

from argparse import ArgumentParser

from tgstatviz.cli_cmds import command_types, mapping
from tgstatviz.cli_cmds.base import BaseCommand


def main():
    """
    TODO: докстринг функции
    :return:
    """
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')

    for command_type in command_types:
        command: BaseCommand = command_type()
        command_parser = subparsers.add_parser(name=command.name, help=command.help)
        command.add_arguments(command_parser)

    args = parser.parse_args()
    exec_func = mapping.get(args.command)
    if exec_func is None:
        raise RuntimeError(f'Неизвестная команда: {args.command}')
    exec_func(args)


if __name__ == '__main__':
    main()
