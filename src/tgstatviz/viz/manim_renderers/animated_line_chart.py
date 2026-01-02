"""
Рендерер: анимированный линейный график
"""
from typing import Type

from manim import (
    Scene, Axes, Create, FadeIn, Text, Line,
    UP, DOWN, LEFT, TEAL, DEGREES,
    rate_functions, RIGHT
)

from tgstatviz.domain.metrics.base import MetricResult
from tgstatviz.viz.manim_renderers.base import Renderer
from tgstatviz.viz.manim_renderers.registry import register_renderer


@register_renderer
class AnimatedLineChartRenderer(Renderer):
    """
    Рендерер анимированного линейного графика для временных рядов

    Ожидаемый формат данных:
        - dates: list[str] - даты в формате dd.mm.YYYY
        - counts: list[int|float] - значения для каждой даты
    """

    @property
    def id(self) -> str:
        return "animated_line_chart"

    def render(self, result: MetricResult, duration: float, **params) -> Type[Scene]:
        """
        Создание Manim-сцены с анимированным линейным графиком
        """
        dates = result.data.get("dates", [])
        counts = result.data.get("counts", [])
        metric_title = result.metric_title

        if not dates or not counts:
            raise ValueError(
                f"Метрика {result.metric_id} вернула пустые данные для графика"
            )

        # Определяем количество подписей на оси X (максимум 10)
        max_x_labels = min(10, len(dates))
        label_indices = [int(i * (len(dates) - 1) / (max_x_labels - 1))
                         for i in range(max_x_labels)] if max_x_labels > 1 else [0]

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

                # Оси БЕЗ автоматических засечек и подписей
                axes = Axes(
                    x_range=[0, len(dates) - 1, 1],
                    y_range=[0, max(counts) * 1.1, max(counts) // 5 or 1],
                    x_length=10,
                    y_length=5,
                    axis_config={
                        # Отключаем автоподписи
                        "include_numbers": False,
                        # Отключаем автозасечки
                        "include_ticks": False,
                        "font_size": 20
                    },
                    tips=False,
                ).to_edge(DOWN, buff=1.2)

                # Подпись оси X - справа в конце оси X
                x_label = Text("Дата", font_size=28)
                x_label.next_to(axes.x_axis.get_end(), RIGHT, buff=0.3)

                # Подпись оси Y - сверху в конце оси Y
                y_label = Text("Сообщения", font_size=28)
                y_label.next_to(axes.y_axis.get_end(), UP, buff=0.3)

                # Вручную добавляем засечки и подписи для оси X
                x_ticks = []
                x_tick_labels = []
                for idx in label_indices:
                    x_pos = axes.c2p(idx, 0)

                    # Засечка (короткая вертикальная линия вниз от оси)
                    tick_start = x_pos
                    tick_end = x_pos + DOWN * 0.1
                    tick = Line(tick_start, tick_end, stroke_width=2)
                    x_ticks.append(tick)

                    # Подпись под углом +30° (по часовой стрелке)
                    label = Text(dates[idx], font_size=18).rotate(30 * DEGREES)
                    label.next_to(tick_end, DOWN, buff=0.1)
                    x_tick_labels.append(label)

                # Вручную добавляем засечки и подписи для оси Y
                y_tick_values = axes.y_axis.get_tick_range()
                y_ticks = []
                y_tick_labels = []
                for y_val in y_tick_values:
                    if y_val == 0:  # Пропускаем ноль (он на пересечении осей)
                        continue
                    y_pos = axes.c2p(0, y_val)

                    # Засечка (короткая горизонтальная линия влево от оси)
                    tick_start = y_pos
                    tick_end = y_pos + LEFT * 0.1
                    tick = Line(tick_start, tick_end, stroke_width=2)
                    y_ticks.append(tick)

                    # Подпись
                    label = Text(str(int(y_val)), font_size=20)
                    label.next_to(tick_end, LEFT, buff=0.1)
                    y_tick_labels.append(label)

                # График с бирюзовым цветом
                graph = axes.plot_line_graph(
                    x_values=list(range(len(dates))),
                    y_values=counts,
                    line_color=TEAL,
                    add_vertex_dots=False,
                    stroke_width=3
                )

                # Анимация
                self.play(FadeIn(title), run_time=0.5)
                self.play(
                    Create(axes),
                    FadeIn(x_label),
                    FadeIn(y_label),
                    *[FadeIn(tick) for tick in x_ticks],
                    *[FadeIn(label) for label in x_tick_labels],
                    *[FadeIn(tick) for tick in y_ticks],
                    *[FadeIn(label) for label in y_tick_labels],
                    run_time=1
                )
                self.play(
                    Create(graph),
                    run_time=duration - 2,
                    # Экспоненциальное ускорение
                    rate_func=rate_functions.ease_in_quad
                )
                self.wait(0.5)

        return AnimatedLineScene
