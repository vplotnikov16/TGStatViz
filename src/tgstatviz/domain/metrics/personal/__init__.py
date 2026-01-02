"""
Метрики для личных чатов
"""

# Импортируем все метрики для автоматической регистрации
from tgstatviz.domain.metrics.personal.cumulative_messages import (
    CumulativeMessagesMetric
)

__all__ = [
    "CumulativeMessagesMetric",
]
