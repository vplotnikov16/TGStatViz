"""
Вспомогательные функции для метрик
"""
from collections import defaultdict
from datetime import datetime, date
from typing import Sequence

from tgstatviz.domain.models import Message


def to_date(dt: datetime) -> date:
    """
    Преобразование datetime в date (без времени)
    """
    return dt.date()


def group_messages_by_day(messages: Sequence[Message]) -> dict[date, int]:
    """
    Группировка сообщений по дням с подсчётом количества
    """
    messages_by_day = defaultdict(int)

    for message in messages:
        if message.date:
            msg_date = to_date(message.date)
            messages_by_day[msg_date] += 1

    return messages_by_day


def smooth_data(data: list[float], window: int) -> list[float]:
    """
    Сглаживание данных методом скользящего среднего
    """
    if window <= 1 or len(data) < window:
        return data

    smoothed = []
    for i in range(len(data)):
        # Берём окно вокруг текущей точки
        start = max(0, i - window // 2)
        end = min(len(data), i + window // 2 + 1)
        smoothed.append(sum(data[start:end]) / (end - start))

    return smoothed
