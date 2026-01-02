"""
Метрика: накопительное количество сообщений по дням
"""
from collections import defaultdict
from datetime import datetime, date

from tgstatviz.domain.metrics.base import Metric, MetricResult
from tgstatviz.domain.metrics.registry import register_metric
from tgstatviz.domain.models import Chat


@register_metric
class CumulativeMessagesMetric(Metric):
    """
    Вычисление накопительного количества сообщений по дням.

    Для каждого дня подсчитывает, сколько всего сообщений было написано
    с начала истории чата до этого дня включительно
    """

    @property
    def id(self) -> str:
        return "personal.cumulative_messages"

    @property
    def title(self) -> str:
        return "Накопительное количество сообщений"

    def compute(self, chat: Chat, **params) -> MetricResult:
        """
        Вычисление метрики
        """
        # Подсчёт сообщений по дням
        messages_by_day = defaultdict(int)

        for message in chat.messages:
            if message.date:
                # Приводим к дате (без времени)
                msg_date = self._to_date(message.date)
                messages_by_day[msg_date] += 1

        if not messages_by_day:
            # Нет сообщений с датой
            return MetricResult(
                metric_id=self.id,
                metric_title=self.title,
                data={"dates": [], "counts": []},
                metadata={}
            )

        # Сортируем даты
        sorted_dates = sorted(messages_by_day.keys())

        # Вычисляем накопительную сумму
        cumulative_count = 0
        dates = []
        counts = []

        for msg_date in sorted_dates:
            cumulative_count += messages_by_day[msg_date]
            dates.append(msg_date.isoformat())
            counts.append(cumulative_count)

        return MetricResult(
            metric_id=self.id,
            metric_title=self.title,
            data={
                "dates": dates,
                "counts": counts
            },
            metadata={
                "total_messages": cumulative_count,
                "first_date": dates[0] if dates else None,
                "last_date": dates[-1] if dates else None,
                "days_count": len(dates)
            }
        )

    @staticmethod
    def _to_date(dt: datetime) -> date:
        """
        Преобразование datetime в date.
        """
        return dt.date()
