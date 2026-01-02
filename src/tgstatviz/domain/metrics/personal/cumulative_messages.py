"""
TODO: докстринг модуля
"""
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
        # ... вычисление
        return MetricResult(
            metric_id=self.id,
            metric_title=self.title,
            data={"dates": [...], "counts": [...]},
            metadata={"smooth_window": params.get("smooth_window", 1)}
        )
