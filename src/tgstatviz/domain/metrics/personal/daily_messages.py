"""
Метрика: количество сообщений по дням
"""
from tgstatviz.domain.metrics.registry import register_metric
from tgstatviz.domain.metrics.personal.base_time_series import BaseTimeSeriesMetric


@register_metric
class DailyMessagesMetric(BaseTimeSeriesMetric):
    """
    Вычисление количества сообщений в каждый день.

    Для каждого дня подсчитывает, сколько сообщений было написано
    именно в этот день (не накопительно).
    """

    @property
    def id(self) -> str:
        return "personal.daily_messages"

    @property
    def title(self) -> str:
        return "Количество сообщений по дням"

    def _transform_counts(
            self,
            counts: list[int],
            messages_by_day: dict
    ) -> list[float]:
        """
        Для дневной метрики преобразование не требуется - возвращаем как есть
        """
        return [float(c) for c in counts]

    def _build_metadata(
            self,
            dates: list[str],
            original_counts: list[float],
            smoothed_counts: list[float],
            smooth_window: int
    ) -> dict:
        """
        Метаданные для дневной метрики (включая информацию о максимуме)
        """
        # Находим день с максимумом (до сглаживания)
        max_index = original_counts.index(max(original_counts)) if original_counts else None
        max_count = original_counts[max_index] if max_index is not None else None
        max_date = dates[max_index] if max_index is not None else None

        return {
            "total_messages": int(sum(original_counts)),
            "first_date": dates[0] if dates else None,
            "last_date": dates[-1] if dates else None,
            "days_count": len(dates),
            "smooth_window": smooth_window,
            # Информация о максимуме
            "max_index": max_index,
            "max_date": max_date,
            "max_count": int(max_count) if max_count is not None else None,
            "avg_messages_per_day": sum(original_counts) / len(original_counts) if original_counts else 0
        }
