"""
TODO: докстринг модуля
"""
from abc import ABC, abstractmethod
from typing import Type
from manim import Scene

from tgstatviz.domain.metrics.base import MetricResult


class Renderer(ABC):
    """
    Абстрактный рендерер Manim-сцен
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Уникальный идентификатор рендерера
        """

    @abstractmethod
    def render(
            self,
            result: MetricResult,
            duration: float,
            **renderer_params
    ) -> Type[Scene]:
        """
        Создает класс Manim-сцены из результата метрики.

        Returns:
            Класс (не экземпляр!) Scene, который Manim сможет отрендерить
        """
