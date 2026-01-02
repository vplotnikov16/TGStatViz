"""
TODO: докстринг модуля
"""

from argparse import ArgumentParser, Namespace

from tgstatviz.cli_cmds.base import BaseCommand


class RenderCommand(BaseCommand):
    """
    TODO: докстринг класса
    """

    @property
    def name(self) -> str:
        return 'render'

    @property
    def help(self) -> str:
        return ''

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        parser.add_argument('export_dir')
        parser.add_argument('config')
        parser.add_argument('-o', '--output')
        parser.add_argument(
            '-q', '--quality',
            choices=['low', 'medium', 'high'],
            default='low',
        )

    @classmethod
    def execute(cls, args: Namespace):
        pass
