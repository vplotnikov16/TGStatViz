"""
Команда вывода списка доступных рендереров
"""
from argparse import ArgumentParser, Namespace

from tgstatviz.cli_cmds.base import BaseCommand
from tgstatviz.viz.manim_renderers.registry import list_renderers


class RenderersCommand(BaseCommand):
    """
    Команда для вывода списка доступных рендереров.
    """

    @staticmethod
    def get_name() -> str:
        return 'renderers'

    @staticmethod
    def get_help() -> str:
        return 'Показать список доступных рендереров'

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        """
        Команда не требует аргументов
        """

    @classmethod
    def execute(cls, args: Namespace):
        """
        Вывод списка рендереров
        """
        renderers = list_renderers()

        if not renderers:
            print("Рендереры не найдены")
            return

        print("Доступные рендереры:")
        for renderer in sorted(renderers):
            print(f"  - {renderer}")
        print()
