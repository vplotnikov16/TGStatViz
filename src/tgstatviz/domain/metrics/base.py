"""
TODO: докстринг модуля
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from tgstatviz.domain.models import Chat


@dataclass
class MetricResult:
    """
    Результат вычисления метрики
    """
    metric_id: str
    metric_title: str
    data: Any
    # Дополнительная информация для рендереров
    metadata: dict[str, Any]


class Metric(ABC):
    """
    Абстрактная метрика
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Уникальный идентификатор (например, 'personal.cumulative_messages')
        """

    @property
    @abstractmethod
    def title(self) -> str:
        """
        Человеко-читаемое название
        """

    @abstractmethod
    def compute(self, chat: Chat, **params) -> MetricResult:
        """
        Вычислить метрику по чату с параметрами из storyboard
        """
