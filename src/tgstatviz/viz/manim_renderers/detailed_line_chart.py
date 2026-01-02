"""
Рендерер: анимированный линейный график с деталями (наследует базовый)
"""
from typing import Type

from manim import (
    Scene, Dot, Text, DashedLine, VGroup, Create, FadeIn,
    UP
)

from tgstatviz.domain.metrics.base import MetricResult
from tgstatviz.viz.manim_renderers.animated_line_chart import AnimatedLineChartRenderer
from tgstatviz.viz.manim_renderers.registry import register_renderer


@register_renderer
class DetailedLineChartRenderer(AnimatedLineChartRenderer):
    """
    Рендерер линейного графика с детальной визуализацией (наследует AnimatedLineChartRenderer)

    Добавляет к базовому рендереру:
    - Две кривые (оригинальная полупрозрачная + сглаженная яркая) если smooth_window > 0
    - Выделение максимума с проекциями к осям
    - Настройку прозрачности элементов

    Требует метаданных:
        - original_counts: list[int|float] - оригинальные данные
        - smooth_window: int - окно сглаживания
        - max_index, max_date, max_count - для выделения максимума

    Параметры рендерера:
        - highlight_max: bool - выделить максимум (по умолчанию False)
        - show_projections: bool - показать проекции (по умолчанию False)
        - highlight_color: str - цвет точки максимума (по умолчанию "RED")
        - original_opacity: float - прозрачность оригинальной кривой (по умолчанию 0.3)
        - smoothed_color: str - цвет сглаженной кривой (по умолчанию "TEAL")
        - original_color: str - цвет оригинальной кривой (по умолчанию = smoothed_color)
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
        Создание детальной сцены с двумя кривыми и выделением максимума
        """
        dates = result.data.get("dates", [])
        # Сглаженные
        counts = result.data.get("counts", [])
        metric_title = result.metric_title

        # Параметры визуализации
        highlight_max = params.get("highlight_max", False)
        show_projections = params.get("show_projections", False)
        highlight_color = params.get("highlight_color", "RED")
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

        if highlight_max and (max_index is None or max_count is None):
            raise ValueError(
                f"Метрика {result.metric_id} не предоставила данные о максимуме. "
                "Отключите highlight_max."
            )

        # Проверка на пропуск сцены
        if duration == 0 and wait_time == 0:
            return self._create_empty_scene()

        # Используем методы базового класса
        label_indices = self._calculate_label_indices(dates)
        y_max = self._calculate_y_max(original_counts, max_original_value)
        times = self._calculate_animation_times(duration, has_additional_elements=highlight_max)

        # Создаём расширенную сцену
        return self._create_detailed_scene(
            dates=dates,
            original_counts=original_counts,
            smoothed_counts=counts,
            metric_title=metric_title,
            wait_time=wait_time,
            label_indices=label_indices,
            y_max=y_max,
            times=times,
            smooth_window=smooth_window,
            smoothed_color=smoothed_color,
            original_color=original_color,
            original_opacity=original_opacity,
            highlight_max=highlight_max,
            show_projections=show_projections,
            highlight_color=highlight_color,
            projection_dash_length=projection_dash_length,
            max_index=max_index,
            max_date=max_date,
            max_count=max_count
        )

    def _create_detailed_scene(
            self,
            dates: list[str],
            original_counts: list[float],
            smoothed_counts: list[float],
            metric_title: str,
            wait_time: float,
            label_indices: list[int],
            y_max: float,
            times: dict,
            smooth_window: int,
            smoothed_color: str,
            original_color: str,
            original_opacity: float,
            highlight_max: bool,
            show_projections: bool,
            highlight_color: str,
            projection_dash_length: float,
            max_index: int,
            max_date: str,
            max_count: float
    ) -> Type[Scene]:
        """
        Создать класс детальной сцены с двумя кривыми
        """

        class DetailedLineScene(Scene):
            """
            Сцена с детальной визуализацией
            """

            def construct(scene_self):  # pylint: disable=no-self-argument
                """
                Построение и анимация детального графика
                """
                # Используем методы базового класса для создания элементов
                title = Text(metric_title, font_size=36).to_edge(UP, buff=0.5)
                axes = self._create_axes(dates, y_max)
                x_label, y_label = self._create_axis_labels(axes)
                x_ticks, x_tick_labels = self._create_x_ticks(axes, dates, label_indices)
                y_ticks, y_tick_labels = self._create_y_ticks(axes)

                # ЛОГИКА ДВУХ КРИВЫХ
                if smooth_window > 0:
                    # Оригинальная (полупрозрачная)
                    original_graph = axes.plot_line_graph(
                        x_values=list(range(len(dates))),
                        y_values=original_counts,
                        line_color=original_color,
                        add_vertex_dots=False,
                        stroke_width=2,
                        stroke_opacity=original_opacity
                    )

                    # Сглаженная (яркая)
                    smoothed_graph = axes.plot_line_graph(
                        x_values=list(range(len(dates))),
                        y_values=smoothed_counts,
                        line_color=smoothed_color,
                        add_vertex_dots=False,
                        stroke_width=3
                    )
                else:
                    # Одна кривая без сглаживания
                    original_graph = None
                    smoothed_graph = axes.plot_line_graph(
                        x_values=list(range(len(dates))),
                        y_values=original_counts,
                        line_color=smoothed_color,
                        add_vertex_dots=False,
                        stroke_width=3
                    )

                # Анимация базовых элементов (используем методы базового класса)
                self._animate_title(scene_self, title, times["title_time"])
                self._animate_axes(
                    scene_self, axes, x_label, y_label,
                    x_ticks, x_tick_labels, y_ticks, y_tick_labels,
                    times["axes_time"]
                )

                # Анимация графиков
                if times["graph_time"] > 0:
                    if original_graph:
                        scene_self.play(
                            Create(original_graph),
                            Create(smoothed_graph),
                            run_time=times["graph_time"]
                        )
                    else:
                        self._animate_graph(scene_self, smoothed_graph, times["graph_time"])
                else:
                    if original_graph:
                        scene_self.add(original_graph)
                    scene_self.add(smoothed_graph)

                # Выделение максимума
                if highlight_max and max_index is not None and max_count is not None:
                    elements_opacity = original_opacity if smooth_window > 0 else 1.0

                    max_point = axes.c2p(max_index, max_count)
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
                        x_projection = DashedLine(
                            max_point,
                            axes.c2p(max_index, 0),
                            color=highlight_color,
                            dash_length=projection_dash_length,
                            stroke_width=2,
                            stroke_opacity=elements_opacity
                        )
                        projections.add(x_projection)

                        y_projection = DashedLine(
                            max_point,
                            axes.c2p(0, max_count),
                            color=highlight_color,
                            dash_length=projection_dash_length,
                            stroke_width=2,
                            stroke_opacity=elements_opacity
                        )
                        projections.add(y_projection)

                    if times["additional_time"] > 0:
                        animations = [FadeIn(max_dot)]
                        if max_label:
                            animations.append(FadeIn(max_label))
                        if show_projections and len(projections) > 0:
                            animations.append(Create(projections))
                        scene_self.play(*animations, run_time=times["additional_time"])
                    else:
                        scene_self.add(max_dot)
                        if max_label:
                            scene_self.add(max_label)
                        if show_projections and len(projections) > 0:
                            scene_self.add(projections)

                # Финальная пауза
                if wait_time > 0:
                    scene_self.wait(wait_time)

        return DetailedLineScene
