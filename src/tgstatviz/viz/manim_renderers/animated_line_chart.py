"""
Рендерер: анимированный линейный график
"""
from typing import Type

from manim import (
    Scene, Axes, Create, FadeIn, Text, Line, Dot,
    UP, DOWN, LEFT, RIGHT, TEAL, DEGREES,
    rate_functions, DashedLine, VGroup
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

    Опциональные метаданные для выделения максимума:
        - max_index: int - индекс точки максимума (в оригинальных данных)
        - max_date: str - дата максимума
        - max_count: int|float - значение максимума (из оригинальных данных до сглаживания)

    Параметры рендерера (через params в storyboard):
        - highlight_max: bool - выделить точку максимума (по умолчанию False)
        - highlight_color: str - цвет точки максимума (по умолчанию "RED")
        - show_projections: bool - показать проекции к осям (по умолчанию False)
        - projection_color: str - цвет проекций (по умолчанию цвет точки)
        - projection_dash_length: float - длина штриха проекции (по умолчанию 0.1)
    """

    @property
    def id(self) -> str:
        return "animated_line_chart"

    def render(
            self,
            result: MetricResult,
            duration: float,
            wait_time: float = 1.0,
            **params
    ) -> Type[Scene]:
        """
        Создание Manim-сцены с анимированным линейным графиком

        Args:
            result: результат метрики с данными и метаданными
            duration: длительность анимации в секундах
            wait_time: время финальной паузы в секундах
            **params: параметры рендерера

        Returns:
            Класс Manim-сцены
        """
        dates = result.data.get("dates", [])
        counts = result.data.get("counts", [])
        metric_title = result.metric_title

        # Параметры выделения максимума
        highlight_max = params.get("highlight_max", False)
        highlight_color = params.get("highlight_color", "RED")
        show_projections = params.get("show_projections", False)
        projection_color = params.get("projection_color", None) or highlight_color
        projection_dash_length = params.get("projection_dash_length", 0.1)

        # Получаем метаданные о максимуме
        max_index = result.metadata.get("max_index")
        max_date = result.metadata.get("max_date")
        max_count = result.metadata.get("max_count")  # Оригинальное значение!

        if not dates or not counts:
            raise ValueError(
                f"Метрика {result.metric_id} вернула пустые данные для графика"
            )

        # Проверяем, что если запрошено выделение максимума, то есть данные о нём
        if highlight_max and (max_index is None or max_count is None):
            raise ValueError(
                f"Метрика {result.metric_id} не предоставила данные о максимуме (max_index, max_count). "
                "Либо отключите highlight_max, либо убедитесь, что метрика возвращает эти данные в metadata."
            )

        # Проверка на пропуск сцены
        if duration == 0 and wait_time == 0:
            # Возвращаем пустую сцену, которую пропустим
            class EmptyScene(Scene):
                """
                Пустая сцена
                """
                def construct(self):
                    """
                    Ничего не делаем
                    """

            return EmptyScene

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
                        "include_numbers": False,
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

                # Расчёт времени анимаций
                if duration == 0:
                    # Без анимации - всё появляется сразу
                    title_time = 0
                    axes_time = 0
                    graph_time = 0
                    highlight_time = 0
                else:
                    # С анимацией
                    title_time = 0.5
                    axes_time = 1.0
                    highlight_time = 1.0 if highlight_max else 0
                    graph_time = max(0.1, duration - title_time - axes_time - highlight_time)

                # Анимация заголовка
                if title_time > 0:
                    self.play(FadeIn(title), run_time=title_time)
                else:
                    self.add(title)

                # Анимация осей и подписей
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

                # Анимация графика
                if graph_time > 0:
                    self.play(
                        Create(graph),
                        run_time=graph_time,
                        rate_func=rate_functions.ease_in_quad
                    )
                else:
                    self.add(graph)

                # Выделение максимума, если включено
                if highlight_max and max_index is not None and max_count is not None:
                    # ИСПРАВЛЕНИЕ БАГА: используем max_count из метаданных (оригинальное значение)
                    # вместо counts[max_index] (которое может быть сглажено)
                    max_point = axes.c2p(max_index, max_count)

                    # Точка максимума
                    max_dot = Dot(max_point, color=highlight_color, radius=0.1)

                    # Подпись к точке
                    max_label = None
                    if max_date:
                        label_text = f"{max_date}\n{int(max_count)} сообщ."
                        max_label = Text(label_text, font_size=20, color=highlight_color)
                        # Размещаем подпись над точкой
                        max_label.next_to(max_dot, UP, buff=0.2)

                    # Проекции к осям (пунктирные линии), если включено
                    projections = VGroup()
                    if show_projections:
                        # Вертикальная проекция от точки к оси X
                        x_proj_start = max_point
                        x_proj_end = axes.c2p(max_index, 0)
                        x_projection = DashedLine(
                            x_proj_start, x_proj_end,
                            color=projection_color,
                            dash_length=projection_dash_length,
                            stroke_width=2
                        )
                        projections.add(x_projection)

                        # Горизонтальная проекция от точки к оси Y
                        y_proj_start = max_point
                        y_proj_end = axes.c2p(0, max_count)
                        y_projection = DashedLine(
                            y_proj_start, y_proj_end,
                            color=projection_color,
                            dash_length=projection_dash_length,
                            stroke_width=2
                        )
                        projections.add(y_projection)

                    # Анимация появления максимума и проекций
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
