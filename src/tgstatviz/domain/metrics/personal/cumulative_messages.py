"""
Метрика: накопительное количество сообщений по дням
"""
from tgstatviz.domain.metrics.registry import register_metric
from tgstatviz.domain.metrics.personal.base_time_series import BaseTimeSeriesMetric


@register_metric
class CumulativeMessagesMetric(BaseTimeSeriesMetric):
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

    def _transform_counts(
            self,
            counts: list[int],
            messages_by_day: dict
    ) -> list[float]:
        """
        Преобразование в накопительную сумму
        """
        cumulative = []
        total = 0
        for count in counts:
            total += count
            cumulative.append(total)
        return cumulative

    def _build_metadata(
            self,
            dates: list[str],
            original_counts: list[float],
            smoothed_counts: list[float],
            smooth_window: int
    ) -> dict:
        """
        Метаданные для накопительной метрики
        """
        return {
            "total_messages": int(original_counts[-1]) if original_counts else 0,
            "first_date": dates[0] if dates else None,
            "last_date": dates[-1] if dates else None,
            "days_count": len(dates),
            "smooth_window": smooth_window
        }
