"""
Компилятор storyboard в список Manim-сцен
"""
from typing import Type

from manim import Scene

from tgstatviz.domain.metrics.registry import get_metric
from tgstatviz.domain.models import Chat
from tgstatviz.storyboard.schema import ProjectConfig, Slide
from tgstatviz.viz.manim_renderers.registry import get_renderer


class SceneCompiler:
    """
    Компилятор storyboard в список Manim-сцен
    """

    def compile(self, config: ProjectConfig, chat: Chat) -> list[tuple[Type[Scene], float]]:
        """
        Скомпилировать storyboard в список (Scene class, total_duration)
        """
        scenes = []

        for i, slide in enumerate(config.slides, start=1):
            try:
                scene_class = self._compile_slide(slide, chat)

                # Общая длительность = duration + wait_time
                total_duration = slide.duration + slide.wait_time

                # Пропускаем сцену, если общая длительность = 0
                if total_duration == 0:
                    print(f"Пропущен слайд {i} ({slide.metric}): duration=0 и wait_time=0")
                    continue

                scenes.append((scene_class, total_duration))
            # pylint: disable=broad-exception-caught
            except Exception as e:
                print(f"Предупреждение: пропущен слайд {i} ({slide.metric}): {e}")
                continue

        return scenes

    @staticmethod
    def _compile_slide(slide: Slide, chat: Chat) -> Type[Scene]:
        """
        Скомпилировать один слайд
        """
        # 1. Получаем метрику
        metric_type = get_metric(slide.metric)
        metric = metric_type()

        # 2. Вычисляем метрику
        result = metric.compute(chat, **slide.params)

        # 3. Получаем рендерер
        renderer_type = get_renderer(slide.renderer)
        renderer = renderer_type()

        # 4. Создаем сцену (передаём wait_time отдельно)
        scene_class = renderer.render(
            result,
            duration=slide.duration,
            wait_time=slide.wait_time,
            **slide.params
        )

        return scene_class
