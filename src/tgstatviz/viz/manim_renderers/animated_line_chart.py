"""
Рендерер: анимированный линейный график (базовый)
"""
from typing import Type

from manim import (
    Scene, Axes, Create, FadeIn, Text, Line,
    UP, DOWN, LEFT, RIGHT, DEGREES,
    rate_functions
)

from tgstatviz.domain.metrics.base import MetricResult
from tgstatviz.viz.manim_renderers.base import Renderer
from tgstatviz.viz.manim_renderers.registry import register_renderer


@register_renderer
class AnimatedLineChartRenderer(Renderer):
    """
    Базовый рендерер анимированного линейного графика для временных рядов

    Ожидаемый формат данных:
        - dates: list[str] - даты в формате dd.mm.YYYY
        - counts: list[int|float] - значения для каждой даты (могут быть сглажены)

    Опциональные метаданные:
        - max_original_value: int|float - максимальное значение для построения оси Y

    Параметры рендерера:
        - line_color: str - цвет линии графика (по умолчанию "TEAL")
        - line_width: float - толщина линии (по умолчанию 3)
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

        # Параметры графика
        line_color = params.get("line_color", "TEAL")
        line_width = params.get("line_width", 3)

        # Получаем максимальное значение для оси Y
        max_original_value = result.metadata.get("max_original_value")

        if not dates or not counts:
            raise ValueError(
                f"Метрика {result.metric_id} вернула пустые данные для графика"
            )

        # Проверка на пропуск сцены
        if duration == 0 and wait_time == 0:
            # Возвращаем пустую сцену, которую пропустим
            class EmptyScene(Scene):
                """
                Пустая сцена
                """
                def construct(self):
                    pass

            return EmptyScene

        # Определяем количество подписей на оси X (максимум 10)
        max_x_labels = min(10, len(dates))
        label_indices = [int(i * (len(dates) - 1) / (max_x_labels - 1))
                         for i in range(max_x_labels)] if max_x_labels > 1 else [0]

        # Для оси Y используем максимум из оригинальных данных или из текущих
        if max_original_value is not None:
            y_max = max_original_value * 1.1
        else:
            y_max = max(counts) * 1.1

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

                # Подпись оси Y - сверху в конце оси Y
                y_label = Text("Сообщения", font_size=28)
                y_label.next_to(axes.y_axis.get_end(), UP, buff=0.3)

                # Вручную добавляем засечки и подписи для оси X
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
                    if y_val == 0:  # Пропускаем ноль (он на пересечении осей)
                        continue
                    y_pos = axes.c2p(0, y_val)
                    tick = Line(y_pos, y_pos + LEFT * 0.1, stroke_width=2)
                    y_ticks.append(tick)

                    # Подпись
                    label = Text(str(int(y_val)), font_size=20)
                    label.next_to(tick.get_end(), LEFT, buff=0.1)
                    y_tick_labels.append(label)

                # График
                graph = axes.plot_line_graph(
                    x_values=list(range(len(dates))),
                    y_values=counts,
                    line_color=line_color,
                    add_vertex_dots=False,
                    stroke_width=line_width
                )

                # Расчёт времени анимаций
                if duration == 0:
                    # Без анимации - всё появляется сразу
                    title_time = 0
                    axes_time = 0
                    graph_time = 0
                else:
                    # С анимацией
                    title_time = 0.5
                    axes_time = 1.0
                    graph_time = max(0.1, duration - title_time - axes_time)

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

                # Финальная пауза
                if wait_time > 0:
                    self.wait(wait_time)

        return AnimatedLineScene
