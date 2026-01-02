"""
Пакет Manim-рендереров
"""

# Импортируем все рендереры для автоматической регистрации через декораторы
from tgstatviz.viz.manim_renderers.animated_line_chart import (
    AnimatedLineChartRenderer
)

__all__ = [
    "AnimatedLineChartRenderer",
]
