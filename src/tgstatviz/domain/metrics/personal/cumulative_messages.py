"""
TODO: докстринг модуля
"""
from collections import defaultdict

from tgstatviz.domain.metrics.base import Metric, MetricResult
from tgstatviz.domain.metrics.registry import register_metric
from tgstatviz.domain.models import Chat


@register_metric
class CumulativeMessagesMetric(Metric):
    """
    TODO: докстринг класса
    """

    @property
    def id(self) -> str:
        return "personal.cumulative_messages"

    @property
    def title(self) -> str:
        return "Накопительное количество сообщений"

    def compute(self, chat: Chat, **params) -> MetricResult:

        # Собираем сообщения по датам
        dates_counts = defaultdict(int)
        for msg in chat.messages:
            date = msg.date.date()
            dates_counts[date] += 1

        # Сортируем и накапливаем
        sorted_dates = sorted(dates_counts.keys())
        cumulative = 0
        dates_list, counts_list = [], []

        for date in sorted_dates:
            cumulative += dates_counts[date]
            dates_list.append(date.isoformat())
            counts_list.append(cumulative)

        # Сглаживаем
        smooth_window = params.get("smooth_window", 1)
        if smooth_window > 1:
            counts_list = self._smooth(counts_list, smooth_window)

        return MetricResult(
            metric_id=self.id,
            metric_title=self.title,
            data={"dates": dates_list, "counts": counts_list},
            metadata={"smooth_window": smooth_window}
        )

    @staticmethod
    def _smooth(values: list[int], window: int) -> list[float]:
        """
        Скользящее среднее
        """
        smoothed = []
        for i in range(len(values)):
            start = max(0, i - window + 1)
            window_vals = values[start:i + 1]
            smoothed.append(sum(window_vals) / len(window_vals))
        return smoothed
