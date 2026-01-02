"""
Рендерер: анимированный линейный график (базовый)
"""
from typing import Type, Optional

from manim import (
    Scene, Axes, Create, FadeIn, Text, Line, VGroup,
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
            return self._create_empty_scene()

        # Определяем количество подписей на оси X (максимум 10)
        label_indices = self._calculate_label_indices(dates)

        # Для оси Y используем максимум из оригинальных данных или из текущих
        y_max = self._calculate_y_max(counts, max_original_value)

        # Создаём сцену через защищённый метод (для переопределения в наследниках)
        return self._create_scene(
            dates=dates,
            counts=counts,
            metric_title=metric_title,
            duration=duration,
            wait_time=wait_time,
            label_indices=label_indices,
            y_max=y_max,
            line_color=line_color,
            line_width=line_width
        )

    # Защищённые методы для переопределения в наследниках

    @staticmethod
    def _create_empty_scene() -> Type[Scene]:
        """
        Создать пустую сцену (для пропуска)
        """

        class EmptyScene(Scene):
            """Пустая сцена"""

            def construct(self):
                """Ничего не делаем"""

        return EmptyScene

    @staticmethod
    def _calculate_label_indices(dates: list[str]) -> list[int]:
        """
        Вычислить индексы подписей на оси X (максимум 10)
        """
        max_x_labels = min(10, len(dates))
        return [int(i * (len(dates) - 1) / (max_x_labels - 1))
                for i in range(max_x_labels)] if max_x_labels > 1 else [0]

    @staticmethod
    def _calculate_y_max(counts: list[float], max_original_value: Optional[float]) -> float:
        """
        Вычислить максимум для оси Y
        """
        if max_original_value is not None:
            return max_original_value * 1.1
        return max(counts) * 1.1

    @staticmethod
    def _calculate_animation_times(duration: float, has_additional_elements: bool = False) -> dict:
        """
        Рассчитать время анимаций

        Args:
            duration: общая длительность
            has_additional_elements: есть ли дополнительные элементы (максимум, проекции)

        Returns:
            Словарь с временами: title_time, axes_time, graph_time, additional_time
        """
        if duration == 0:
            return {
                "title_time": 0,
                "axes_time": 0,
                "graph_time": 0,
                "additional_time": 0
            }

        title_time = 0.5
        axes_time = 1.0
        additional_time = 1.0 if has_additional_elements else 0
        graph_time = max(0.1, duration - title_time - axes_time - additional_time)

        return {
            "title_time": title_time,
            "axes_time": axes_time,
            "graph_time": graph_time,
            "additional_time": additional_time
        }

    def _create_scene(
            self,
            dates: list[str],
            counts: list[float],
            metric_title: str,
            duration: float,
            wait_time: float,
            label_indices: list[int],
            y_max: float,
            line_color: str,
            line_width: float
    ) -> Type[Scene]:
        """
        Создать класс сцены (может быть переопределён в наследниках)
        """
        # Расчёт времени
        times = self._calculate_animation_times(duration, has_additional_elements=False)

        class AnimatedLineScene(Scene):
            """
            Сцена с анимированным линейным графиком
            """

            def construct(scene_self):  # pylint: disable=no-self-argument
                """
                Построение и анимация графика
                """
                # Создаём элементы через вспомогательные методы
                title = Text(metric_title, font_size=36).to_edge(UP, buff=0.5)
                axes = self._create_axes(dates, y_max)
                x_label, y_label = self._create_axis_labels(axes)
                x_ticks, x_tick_labels = self._create_x_ticks(axes, dates, label_indices)
                y_ticks, y_tick_labels = self._create_y_ticks(axes)

                # График
                graph = axes.plot_line_graph(
                    x_values=list(range(len(dates))),
                    y_values=counts,
                    line_color=line_color,
                    add_vertex_dots=False,
                    stroke_width=line_width
                )

                # Анимация
                self._animate_title(scene_self, title, times["title_time"])
                self._animate_axes(
                    scene_self, axes, x_label, y_label,
                    x_ticks, x_tick_labels, y_ticks, y_tick_labels,
                    times["axes_time"]
                )
                self._animate_graph(scene_self, graph, times["graph_time"])

                # Финальная пауза
                if wait_time > 0:
                    scene_self.wait(wait_time)

        return AnimatedLineScene

    # Вспомогательные методы для создания элементов

    @staticmethod
    def _create_axes(dates: list[str], y_max: float) -> Axes:
        """
        Создание осей координат
        """
        return Axes(
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

    @staticmethod
    def _create_axis_labels(axes: Axes) -> tuple[Text, Text]:
        """
        Создание подписей к осям
        """
        x_label = Text("Дата", font_size=28)
        x_label.next_to(axes.x_axis.get_end(), RIGHT, buff=0.3)

        y_label = Text("Сообщения", font_size=28)
        y_label.next_to(axes.y_axis.get_end(), UP, buff=0.3)

        return x_label, y_label

    @staticmethod
    def _create_x_ticks(
            axes: Axes,
            dates: list[str],
            label_indices: list[int]
    ) -> tuple[list[Line], list[Text]]:
        """
        Создать засечек и названия для оси X
        """
        x_ticks = []
        x_tick_labels = []

        for idx in label_indices:
            x_pos = axes.c2p(idx, 0)
            tick = Line(x_pos, x_pos + DOWN * 0.1, stroke_width=2)
            x_ticks.append(tick)

            label = Text(dates[idx], font_size=18).rotate(30 * DEGREES)
            label.next_to(tick.get_end(), DOWN, buff=0.1)
            x_tick_labels.append(label)

        return x_ticks, x_tick_labels

    @staticmethod
    def _create_y_ticks(axes: Axes) -> tuple[list[Line], list[Text]]:
        """
        Создание засечек и названия для оси Y"""
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

        return y_ticks, y_tick_labels

    # Методы анимации

    @staticmethod
    def _animate_title(scene: Scene, title: Text, title_time: float):
        """
        Анимация заголовка
        """
        if title_time > 0:
            scene.play(FadeIn(title), run_time=title_time)
        else:
            scene.add(title)

    @staticmethod
    def _animate_axes(
            scene: Scene,
            axes: Axes,
            x_label: Text,
            y_label: Text,
            x_ticks: list[Line],
            x_tick_labels: list[Text],
            y_ticks: list[Line],
            y_tick_labels: list[Text],
            axes_time: float
    ):
        """
        Анимация осей и подписей
        """
        if axes_time > 0:
            scene.play(
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
            scene.add(axes, x_label, y_label, *x_ticks, *x_tick_labels, *y_ticks, *y_tick_labels)

    @staticmethod
    def _animate_graph(scene: Scene, graph: VGroup, graph_time: float):
        """
        Анимация графика
        """
        if graph_time > 0:
            scene.play(
                Create(graph),
                run_time=graph_time,
                rate_func=rate_functions.ease_in_quad
            )
        else:
            scene.add(graph)
