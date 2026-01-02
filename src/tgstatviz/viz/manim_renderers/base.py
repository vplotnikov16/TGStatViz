"""
Базовый класс для рендереров Manim-сцен
"""
from abc import ABC, abstractmethod
from typing import Type

from manim import Scene

from tgstatviz.domain.metrics.base import MetricResult


class Renderer(ABC):
    """
    Абстрактный рендерер Manim-сцен

    Каждый рендерер должен:
    1. Иметь уникальный id
    2. Реализовывать метод render(), который возвращает класс Scene
    3. Поддерживать параметр wait_time для финальной паузы
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
            wait_time: float = 1.0,
            **params
    ) -> Type[Scene]:
        """
        Создать класс Manim-сцены из результата метрики

        Args:
            result: результат вычисления метрики
            duration: длительность анимации (без учёта финальной паузы)
            wait_time: время финальной паузы в секундах (по умолчанию 1.0)
            **params: дополнительные параметры рендерера из storyboard

        Returns:
            Класс (не экземпляр!) Scene, который Manim сможет отрендерить

        Notes:
            - Если duration=0 и wait_time=0, сцена должна быть пропущена
            - Если duration=0 и wait_time>0, сцена отрисовывается без анимации
            - Финальная пауза реализуется через self.wait(wait_time)
        """
