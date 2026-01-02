"""
Пакет Manim-рендереров
"""

# Импортируем все рендереры для автоматической регистрации через декораторы
from tgstatviz.viz.manim_renderers.animated_line_chart import (
    AnimatedLineChartRenderer
)

from tgstatviz.viz.manim_renderers.detailed_line_chart import (
    DetailedLineChartRenderer
)

__all__ = [
    "AnimatedLineChartRenderer",
    "DetailedLineChartRenderer",
]
