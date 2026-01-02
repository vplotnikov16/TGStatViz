"""
TODO: докстринг модуля
"""

from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace


class BaseCommand(ABC):
    """
    TODO: докстринг класса
    """

    @abstractmethod
    @property
    def name(self) -> str:
        """
        TODO: докстринг функции
        :return:
        """

    @abstractmethod
    @property
    def help(self) -> str:
        """
        TODO: докстринг функции
        :return:
        """

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
