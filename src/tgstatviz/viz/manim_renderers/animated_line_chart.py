"""
TODO: докстринг модуля
"""
from typing import Type

from manim import Scene

from tgstatviz.domain.metrics.base import MetricResult
from tgstatviz.viz.manim_renderers.base import Renderer
from tgstatviz.viz.manim_renderers.registry import register_renderer


@register_renderer
class AnimatedLineChartRenderer(Renderer):
    """
    TODO: докстринг класса
    """

    @property
    def id(self) -> str:
        """
        TODO: докстринг метода
        """
        return "animated_line_chart"

    def render(self, result: MetricResult, duration: float, **params) -> Type[Scene]:
        dates = result.data["dates"]
        counts = result.data["counts"]
        title = result.metric_title

        class AnimatedLineScene(Scene):
            """
            TODO: докстринг класса
            """
            def construct(self):
                """
                TODO: докстринг метода
                """
                from manim import Axes, Text, Create, Write, UP, BLUE

                # Заголовок
                title_text = Text(title, font_size=36).to_edge(UP)
                self.play(Write(title_text))

                # Оси
                axes = Axes(
                    x_range=[0, len(dates), max(1, len(dates) // 10)],
                    y_range=[0, max(counts) * 1.1, max(counts) // 5],
                    x_length=10,
                    y_length=6,
                )
                self.play(Create(axes))

                line = axes.plot_line_graph(
                    x_values=list(range(len(dates))),
                    y_values=counts,
                    line_color=BLUE,
                    add_vertex_dots=False
                )
                self.play(Create(line), run_time=duration)
                self.wait(1)

        return AnimatedLineScene
