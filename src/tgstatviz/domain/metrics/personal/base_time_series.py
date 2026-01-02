"""
Базовый класс для метрик временных рядов по дням
"""
from abc import abstractmethod

from tgstatviz.domain.metrics.base import Metric, MetricResult
from tgstatviz.domain.metrics.helpers import group_messages_by_day, smooth_data
from tgstatviz.domain.models import Chat


class BaseTimeSeriesMetric(Metric):
    """
    Базовый класс для метрик, работающих с временными рядами по дням.

    Инкапсулирует общую логику:
    - Группировка сообщений по дням
    - Сглаживание данных
    - Формирование базовых метаданных
    """

    def compute(self, chat: Chat, **params) -> MetricResult:
        """
        Вычисление метрики временного ряда
        """
        smooth_window = params.get("smooth_window", 1)

        # Подсчёт сообщений по дням через helper
        messages_by_day = group_messages_by_day(chat.messages)

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

        # Дочерний класс преобразует данные (накопительно, скользящее окно и т.п.)
        counts = self._transform_counts(counts, messages_by_day)

        # Применяем сглаживание, если smooth_window > 1
        original_counts = counts.copy()
        if smooth_window > 1:
            counts = smooth_data(counts, window=smooth_window)

        # Дочерний класс формирует специфичные метаданные
        metadata = self._build_metadata(
            dates, original_counts, counts, smooth_window
        )

        return MetricResult(
            metric_id=self.id,
            metric_title=self.title,
            data={
                "dates": dates,
                "counts": counts
            },
            metadata=metadata
        )

    @abstractmethod
    def _transform_counts(
            self,
            counts: list[int],
            messages_by_day: dict
    ) -> list[float]:
        """
        Преобразование подсчитанных данных (реализуется в дочернем классе)
        """

    @abstractmethod
    def _build_metadata(
            self,
            dates: list[str],
            original_counts: list[float],
            smoothed_counts: list[float],
            smooth_window: int
    ) -> dict:
        """
        Построение метаданных (реализуется в дочернем классе)
        """
