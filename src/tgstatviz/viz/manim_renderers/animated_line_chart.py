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
        """
        TODO: докстринг метода
        """

        class AnimatedLineScene(Scene):
            """
            TODO: докстринг класса
            """

            def construct(self):
                """
                TODO: докстринг метода
                """
                # ... создание графика из result.data

        AnimatedLineScene.duration = duration
        return AnimatedLineScene
