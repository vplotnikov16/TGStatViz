"""
TODO: докстринг модуля
"""

from abc import ABC
from argparse import ArgumentParser, Namespace


class BaseCommand(ABC):
    """
    TODO: докстринг класса
    """

    @staticmethod
    def get_name() -> str:
        """
        Имя команды через геттер для удобства
        """
        raise NotImplementedError

    @staticmethod
    def get_help() -> str:
        """
        Описание команды через геттер для удобства
        """
        raise NotImplementedError

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        """
        TODO: докстринг функции
        :param parser:
        :return:
        """

        raise NotImplementedError

    @classmethod
    def execute(cls, args: Namespace):
        """
        TODO: докстринг функции
        :param args:
        :return:
        """

        raise NotImplementedError
