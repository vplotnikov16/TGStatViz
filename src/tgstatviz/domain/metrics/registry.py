"""
TODO: докстринг модуля
"""
from typing import Type

from tgstatviz.domain.metrics.base import Metric

_METRICS: dict[str, Type[Metric]] = {}


def register_metric(metric_cls: Type[Metric]) -> Type[Metric]:
    """
    Декоратор для автоматической регистрации метрики
    """
    instance = metric_cls()
    _METRICS[instance.id] = metric_cls
    return metric_cls


def get_metric(metric_id: str) -> Type[Metric]:
    """
    Геттер класса метрики по ID
    """
    if metric_id not in _METRICS:
        raise ValueError(f"Метрика '{metric_id}' не зарегистрирована")
    return _METRICS[metric_id]


def list_metrics() -> list[str]:
    """
    Список всех зарегистрированных метрик
    """
    return list(_METRICS.keys())
