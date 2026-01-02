"""
Рендерер: анимированный линейный график с деталями
"""
from typing import Type

from manim import (
    Scene, Axes, Create, FadeIn, Text, Line, Dot,
    UP, DOWN, LEFT, RIGHT, TEAL, RED, DEGREES,
    rate_functions, DashedLine, VGroup
)

from tgstatviz.domain.metrics.base import MetricResult
from tgstatviz.viz.manim_renderers.base import Renderer
from tgstatviz.viz.manim_renderers.registry import register_renderer


@register_renderer
class DetailedLineChartRenderer(Renderer):
    """
    Рендерер анимированного линейного графика с детальной визуализацией

    Особенности:
    - Если smooth_window > 0: рисует две кривые (оригинальная полупрозрачная + сглаженная яркая)
    - Если smooth_window == 0: рисует одну кривую в обычном цвете
    - Поддерживает выделение максимума с проекциями к осям
    - Прозрачность оригинальной кривой, точки и проекций настраивается

    Ожидаемый формат данных:
        - dates: list[str] - даты в формате dd.mm.YYYY
        - counts: list[int|float] - сглаженные значения (если smooth_window > 0)

    Обязательные метаданные:
        - original_counts: list[int|float] - оригинальные данные
        - max_original_value: int|float - максимальное значение для оси Y
        - smooth_window: int - окно сглаживания

    Опциональные метаданные для выделения максимума:
        - max_index: int - индекс точки максимума
        - max_date: str - дата максимума
        - max_count: int|float - значение максимума

    Параметры рендерера (через params в storyboard):
        - highlight_max: bool - выделить точку максимума (по умолчанию False)
        - highlight_color: str - цвет точки максимума (по умолчанию "RED")
        - show_projections: bool - показать проекции к осям (по умолчанию False)
        - original_opacity: float - прозрачность оригинальной кривой (по умолчанию 0.3)
        - smoothed_color: str - цвет сглаженной кривой (по умолчанию "TEAL")
        - original_color: str - цвет оригинальной кривой (по умолчанию совпадает со сглаженной)
        - projection_dash_length: float - длина штриха проекции (по умолчанию 0.1)
    """

    @property
    def id(self) -> str:
        return "detailed_line_chart"

    def render(
            self,
            result: MetricResult,
            duration: float,
            wait_time: float = 1.0,
            **params
    ) -> Type[Scene]:
        """
        Создание Manim-сцены с детальным линейным графиком
        """
        dates = result.data.get("dates", [])
        # Сглаженные данные
        counts = result.data.get("counts", [])
        metric_title = result.metric_title

        # Параметры визуализации
        highlight_max = params.get("highlight_max", False)
        highlight_color = params.get("highlight_color", "RED")
        show_projections = params.get("show_projections", False)
        original_opacity = params.get("original_opacity", 0.3)
        smoothed_color = params.get("smoothed_color", "TEAL")
        original_color = params.get("original_color", smoothed_color)
        projection_dash_length = params.get("projection_dash_length", 0.1)

        # Получаем метаданные
        original_counts = result.metadata.get("original_counts")
        max_original_value = result.metadata.get("max_original_value")
        smooth_window = result.metadata.get("smooth_window", 0)

        max_index = result.metadata.get("max_index")
        max_date = result.metadata.get("max_date")
        max_count = result.metadata.get("max_count")

        if not dates or not counts:
            raise ValueError(
                f"Метрика {result.metric_id} вернула пустые данные для графика"
            )

        if not original_counts:
            raise ValueError(
                f"Метрика {result.metric_id} не предоставила original_counts. "
                f"Используйте базовый рендерер 'animated_line_chart'."
            )

        # Проверяем данные о максимуме
        if highlight_max and (max_index is None or max_count is None):
            raise ValueError(
                f"Метрика {result.metric_id} не предоставила данные о максимуме. "
                "Отключите highlight_max или убедитесь, что метрика возвращает max_index и max_count."
            )

        # Проверка на пропуск сцены
        if duration == 0 and wait_time == 0:
            class EmptyScene(Scene):
                def construct(self):
                    pass

            return EmptyScene

        # Определяем количество подписей на оси X (максимум 10)
        max_x_labels = min(10, len(dates))
        label_indices = [int(i * (len(dates) - 1) / (max_x_labels - 1))
                         for i in range(max_x_labels)] if max_x_labels > 1 else [0]

        # Для оси Y используем максимум из оригинальных данных
        y_max = max_original_value * 1.1 if max_original_value else max(original_counts) * 1.1

        class AnimatedLineScene(Scene):
            """
            Сцена с детальным линейным графиком
            """

            def construct(self):
                """
                Построение и анимация графика
                """
                # Заголовок
                title = Text(metric_title, font_size=36).to_edge(UP, buff=0.5)

                # Оси
                axes = Axes(
                    x_range=[0, len(dates) - 1, 1],
                    y_range=[0, y_max, y_max // 5 or 1],
                    x_length=10,
                    y_length=5,
                    axis_config={
                        "include_numbers": False,
                        "include_ticks": False,
                        "font_size": 20
                    },
                    tips=False,
                ).to_edge(DOWN, buff=1.2)

                # Подписи осей
                x_label = Text("Дата", font_size=28)
                x_label.next_to(axes.x_axis.get_end(), RIGHT, buff=0.3)

                y_label = Text("Сообщения", font_size=28)
                y_label.next_to(axes.y_axis.get_end(), UP, buff=0.3)

                # Засечки и подписи для оси X
                x_ticks = []
                x_tick_labels = []
                for idx in label_indices:
                    x_pos = axes.c2p(idx, 0)
                    tick = Line(x_pos, x_pos + DOWN * 0.1, stroke_width=2)
                    x_ticks.append(tick)

                    label = Text(dates[idx], font_size=18).rotate(30 * DEGREES)
                    label.next_to(tick.get_end(), DOWN, buff=0.1)
                    x_tick_labels.append(label)

                # Засечки и подписи для оси Y
                y_tick_values = axes.y_axis.get_tick_range()
                y_ticks = []
                y_tick_labels = []
                for y_val in y_tick_values:
                    if y_val == 0:
                        continue
                    y_pos = axes.c2p(0, y_val)
                    tick = Line(y_pos, y_pos + LEFT * 0.1, stroke_width=2)
                    y_ticks.append(tick)

                    label = Text(str(int(y_val)), font_size=20)
                    label.next_to(tick.get_end(), LEFT, buff=0.1)
                    y_tick_labels.append(label)

                # ЛОГИКА ДВУХ КРИВЫХ
                if smooth_window > 0:
                    # Две кривые: оригинальная (полупрозрачная) + сглаженная (яркая)

                    # Оригинальная кривая (полупрозрачная)
                    original_graph = axes.plot_line_graph(
                        x_values=list(range(len(dates))),
                        y_values=original_counts,
                        line_color=original_color,
                        add_vertex_dots=False,
                        stroke_width=2,
                        stroke_opacity=original_opacity
                    )

                    # Сглаженная кривая (яркая)
                    smoothed_graph = axes.plot_line_graph(
                        x_values=list(range(len(dates))),
                        y_values=counts,
                        line_color=smoothed_color,
                        add_vertex_dots=False,
                        stroke_width=3
                    )
                else:
                    # Одна кривая в обычном цвете (без сглаживания)
                    original_graph = None
                    smoothed_graph = axes.plot_line_graph(
                        x_values=list(range(len(dates))),
                        y_values=original_counts,
                        line_color=smoothed_color,
                        add_vertex_dots=False,
                        stroke_width=3
                    )

                # Расчёт времени анимаций
                if duration == 0:
                    title_time = 0
                    axes_time = 0
                    graph_time = 0
                    highlight_time = 0
                else:
                    title_time = 0.5
                    axes_time = 1.0
                    highlight_time = 1.0 if highlight_max else 0
                    graph_time = max(0.1, duration - title_time - axes_time - highlight_time)

                # Анимация заголовка
                if title_time > 0:
                    self.play(FadeIn(title), run_time=title_time)
                else:
                    self.add(title)

                # Анимация осей
                if axes_time > 0:
                    self.play(
                        Create(axes),
                        FadeIn(x_label),
                        FadeIn(y_label),
                        *[FadeIn(tick) for tick in x_ticks],
                        *[FadeIn(label) for label in x_tick_labels],
                        *[FadeIn(tick) for tick in y_ticks],
                        *[FadeIn(label) for label in y_tick_labels],
                        run_time=axes_time
                    )
                else:
                    self.add(axes, x_label, y_label, *x_ticks, *x_tick_labels, *y_ticks, *y_tick_labels)

                # Анимация графиков
                if graph_time > 0:
                    if original_graph:
                        # Две кривые одновременно
                        self.play(
                            Create(original_graph),
                            Create(smoothed_graph),
                            run_time=graph_time,
                            rate_func=rate_functions.ease_in_quad
                        )
                    else:
                        # Одна кривая
                        self.play(
                            Create(smoothed_graph),
                            run_time=graph_time,
                            rate_func=rate_functions.ease_in_quad
                        )
                else:
                    if original_graph:
                        self.add(original_graph)
                    self.add(smoothed_graph)

                # Выделение максимума
                if highlight_max and max_index is not None and max_count is not None:
                    # Координаты точки максимума (оригинальное значение)
                    max_point = axes.c2p(max_index, max_count)

                    # Прозрачность точки и проекций = прозрачность оригинальной кривой
                    elements_opacity = original_opacity if smooth_window > 0 else 1.0

                    # Точка максимума
                    max_dot = Dot(
                        max_point,
                        color=highlight_color,
                        radius=0.12,
                        fill_opacity=elements_opacity,
                        stroke_opacity=elements_opacity
                    )

                    # Подпись к точке
                    max_label = None
                    if max_date:
                        label_text = f"{max_date}\n{int(max_count)} сообщ."
                        max_label = Text(
                            label_text,
                            font_size=20,
                            color=highlight_color,
                            fill_opacity=elements_opacity
                        )
                        max_label.next_to(max_dot, UP, buff=0.2)

                    # Проекции к осям
                    projections = VGroup()
                    if show_projections:
                        # Вертикальная проекция
                        x_projection = DashedLine(
                            max_point,
                            axes.c2p(max_index, 0),
                            color=highlight_color,
                            dash_length=projection_dash_length,
                            stroke_width=2,
                            stroke_opacity=elements_opacity
                        )
                        projections.add(x_projection)

                        # Горизонтальная проекция
                        y_projection = DashedLine(
                            max_point,
                            axes.c2p(0, max_count),
                            color=highlight_color,
                            dash_length=projection_dash_length,
                            stroke_width=2,
                            stroke_opacity=elements_opacity
                        )
                        projections.add(y_projection)

                    # Анимация появления максимума
                    if highlight_time > 0:
                        animations = [FadeIn(max_dot)]
                        if max_label:
                            animations.append(FadeIn(max_label))
                        if show_projections and len(projections) > 0:
                            animations.append(Create(projections))
                        self.play(*animations, run_time=highlight_time)
                    else:
                        self.add(max_dot)
                        if max_label:
                            self.add(max_label)
                        if show_projections and len(projections) > 0:
                            self.add(projections)

                # Финальная пауза
                if wait_time > 0:
                    self.wait(wait_time)

        return AnimatedLineScene
