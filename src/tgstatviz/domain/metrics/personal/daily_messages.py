"""
Метрика: количество сообщений по дням
"""
from collections import defaultdict
from datetime import datetime, date

from tgstatviz.domain.metrics.base import Metric, MetricResult
from tgstatviz.domain.metrics.registry import register_metric
from tgstatviz.domain.models import Chat


@register_metric
class DailyMessagesMetric(Metric):
    """
    Вычисление количества сообщений за каждый день
    """

    @property
    def id(self) -> str:
        return "personal.daily_messages"

    @property
    def title(self) -> str:
        return "Количество сообщений по дням"

    def compute(self, chat: Chat, **params) -> MetricResult:
        """
        Вычисление метрики
        """
        smooth = params.get("smooth", 1)

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

        # Формируем списки дат и количеств
        dates = []
        counts = []

        for msg_date in sorted_dates:
            dates.append(msg_date.strftime("%d.%m.%Y"))
            counts.append(messages_by_day[msg_date])

        # Находим день с максимумом ДО сглаживания
        max_index = counts.index(max(counts)) if counts else None
        max_count = counts[max_index] if max_index is not None else None
        max_date = dates[max_index] if max_index is not None else None

        # Применяем сглаживание, если smooth > 1
        original_counts = counts.copy()
        if smooth > 1:
            counts = self._smooth_data(counts, window=smooth)

        return MetricResult(
            metric_id=self.id,
            metric_title=self.title,
            data={
                "dates": dates,
                "counts": counts
            },
            metadata={
                "total_messages": sum(original_counts),
                "first_date": dates[0] if dates else None,
                "last_date": dates[-1] if dates else None,
                "days_count": len(dates),
                "smooth_window": smooth,
                # Информация о максимуме
                "max_index": max_index,
                "max_date": max_date,
                "max_count": max_count,
                "avg_messages_per_day": sum(original_counts) / len(original_counts) if original_counts else 0
            }
        )

    @staticmethod
    def _to_date(dt: datetime) -> date:
        """
        Преобразование datetime в date
        """
        return dt.date()

    @staticmethod
    def _smooth_data(data: list[float], window: int) -> list[float]:
        """
        Сглаживание данных методом скользящего среднего
        """
        if window <= 1 or len(data) < window:
            return data

        smoothed = []
        for i in range(len(data)):
            start = max(0, i - window // 2)
            end = min(len(data), i + window // 2 + 1)
            smoothed.append(sum(data[start:end]) / (end - start))

        return smoothed
