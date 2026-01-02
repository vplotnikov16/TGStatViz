"""
Метрики для личных чатов
"""

# Импортируем все метрики для автоматической регистрации
from tgstatviz.domain.metrics.personal.cumulative_messages import (
    CumulativeMessagesMetric
)
from tgstatviz.domain.metrics.personal.daily_messages import (
    DailyMessagesMetric
)

__all__ = [
    "CumulativeMessagesMetric",
    "DailyMessagesMetric",
]
