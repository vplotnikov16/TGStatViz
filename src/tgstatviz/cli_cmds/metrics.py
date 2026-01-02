"""
Команда вывода списка доступных метрик
"""
from argparse import ArgumentParser, Namespace

from tgstatviz.cli_cmds.base import BaseCommand
from tgstatviz.domain.metrics.registry import list_metrics


class MetricsCommand(BaseCommand):
    """
    Команда для вывода списка доступных метрик.
    """

    @staticmethod
    def get_name() -> str:
        return 'metrics'

    @staticmethod
    def get_help() -> str:
        return 'Показать список доступных метрик'

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        """
        Команда не требует аргументов
        """

    @classmethod
    def execute(cls, args: Namespace):
        """
        Вывод списка метрик
        """
        metrics = list_metrics()

        if not metrics:
            print("Метрики не найдены")
            return

        print("Доступные метрики:")
        print()

        # Группировка по префиксам
        personal = [m for m in metrics if m.startswith("personal.")]
        group = [m for m in metrics if m.startswith("group.")]
        other = [m for m in metrics if not m.startswith(("personal.", "group."))]

        if personal:
            print("Метрики личных чатов:")
            for metric in sorted(personal):
                print(f"  - {metric}")
            print()

        if group:
            print("Метрики групповых чатов:")
            for metric in sorted(group):
                print(f"  - {metric}")
            print()

        if other:
            print("Прочие метрики:")
            for metric in sorted(other):
                print(f"  - {metric}")
            print()
