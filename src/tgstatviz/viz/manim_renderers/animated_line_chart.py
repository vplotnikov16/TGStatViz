"""
Рендерер: анимированный линейный график
"""
from typing import Type

from manim import (
    Scene, Axes, Create, FadeIn, Text,
    UP, DOWN, LEFT
)

from tgstatviz.domain.metrics.base import MetricResult
from tgstatviz.viz.manim_renderers.base import Renderer
from tgstatviz.viz.manim_renderers.registry import register_renderer


@register_renderer
class AnimatedLineChartRenderer(Renderer):
    """
    Рендерер анимированного линейного графика для временных рядов

    Ожидаемый формат данных:
        - dates: list[str] - даты в ISO формате
        - counts: list[int|float] - значения для каждой даты
    """

    @property
    def id(self) -> str:
        return "animated_line_chart"

    def render(self, result: MetricResult, duration: float, **params) -> Type[Scene]:
        """
        Создание Manim-сцену с анимированным линейным графиком
        """
        dates = result.data.get("dates", [])
        counts = result.data.get("counts", [])
        metric_title = result.metric_title

        if not dates or not counts:
            raise ValueError(
                f"Метрика {result.metric_id} вернула пустые данные для графика"
            )

        class AnimatedLineScene(Scene):
            """
            Сцена с анимированным линейным графиком
            """

            def construct(self):
                """
                Построение и анимация графика
                """
                # Заголовок
                title = Text(metric_title, font_size=36).to_edge(UP, buff=0.5)

                # Оси
                axes = Axes(
                    x_range=[0, len(dates) - 1, max(1, (len(dates) - 1) // 10)],
                    y_range=[0, max(counts) * 1.1, max(counts) // 5 or 1],
                    x_length=10,
                    y_length=5,
                    axis_config={"include_numbers": True, "font_size": 24},
                    tips=False,
                ).to_edge(DOWN, buff=1)

                # Подписи осей
                x_label = Text("Дни", font_size=28).next_to(axes, DOWN)
                y_label = Text("Сообщений", font_size=28).next_to(axes, LEFT).rotate(90)

                graph = axes.plot_line_graph(
                    x_values=list(range(len(dates))),
                    y_values=counts,
                    line_color="#00FF00",
                    add_vertex_dots=False,
                    stroke_width=3
                )

                # Анимация
                self.play(FadeIn(title), run_time=0.5)
                self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1)
                self.play(Create(graph), run_time=duration - 2, rate_func=lambda t: t)
                self.wait(0.5)

        return AnimatedLineScene
