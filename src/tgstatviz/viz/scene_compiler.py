"""
TODO: докстринг модуля
"""
from typing import Type
from manim import Scene

from tgstatviz.domain.models import Chat
from tgstatviz.domain.metrics.registry import get_metric
from tgstatviz.viz.manim_renderers.registry import get_renderer
from tgstatviz.storyboard.schema import ProjectConfig, Slide


class SceneCompiler:
    """
    Компилятор storyboard в список Manim-сцен
    """

    def compile(self, config: ProjectConfig, chat: Chat) -> list[tuple[Type[Scene], float]]:
        """
        Компилирование storyboard в список (Scene class, duration)
        """
        scenes = []

        for i, slide in enumerate(config.slides, start=1):
            try:
                scene_class = self._compile_slide(slide, chat)
                scenes.append((scene_class, slide.duration))
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

        # 4. Создаем сцену
        scene_class = renderer.render(result, slide.duration, **slide.params)

        return scene_class
