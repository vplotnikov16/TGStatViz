"""
Рендеринг видео из storyboard
"""

from pathlib import Path
from typing import Optional

from manim import config as manim_config, tempconfig

from tgstatviz.adapters.json_loader import JSONExportLoader
from tgstatviz.domain.models import Chat
from tgstatviz.storyboard.loader import load_storyboard
from tgstatviz.viz.scene_compiler import SceneCompiler


class RenderService:
    """
    Рендеринг видео из storyboard
    """

    def render_video(
            self,
            export_dir: Path,
            storyboard_path: Path,
            output_path: Optional[Path] = None,
            quality: str = "low",
    ) -> None:
        """
        Выполнение рендеринга

        Args:
            export_dir: путь к каталогу экспорта Telegram
            storyboard_path: путь к YAML-конфигу storyboard
            output_path: путь к выходному видео (опционально)
            quality: качество рендера (low/medium/high)
        """

        # Шаг 1: Загрузка чата
        print(f"Загрузка чата из {export_dir}...")
        chat = self._load_chat(export_dir)
        self._print_chat_info(chat)

        # Шаг 2: Загрузка storyboard
        print(f"\nЗагрузка storyboard из {storyboard_path}...")
        config = load_storyboard(storyboard_path)
        print(f"Загружен storyboard: {config.title}")
        print(f"Описание: {config.description}")
        print(f"Слайдов: {len(config.slides)}")

        # Шаг 3: Создание сцен
        print(f"\nСоздание сцен Manim (качество: {quality})...")
        self._configure_manim_quality(quality)

        compiler = SceneCompiler()
        scenes = compiler.compile(config, chat)

        if not scenes:
            print("Ошибка: не удалось создать ни одной сцены")
            return

        print(f"Создано сцен: {len(scenes)}")

        # Шаг 4: Рендеринг
        print("\nРендеринг сцен Manim...")
        rendered_videos = self._render_scenes(scenes, output_path)

        if not rendered_videos:
            print("\nОшибка: ни одна сцена не была успешно отрендерена")
            return

        # Шаг 5: Финализация
        if output_path:
            if len(rendered_videos) == 1:
                # Одна сцена - просто переименовываем
                self._finalize_single_video(rendered_videos[0], output_path)
            else:
                # Несколько сцен - нужна склейка (TODO: Шаг 6)
                print(f"\n[TODO] Склейка {len(rendered_videos)} сцен в {output_path}")
                print(f"Временные файлы сцен: {rendered_videos[0].parent}")
        else:
            print("\nРендеринг завершён (выходной путь не указан)")

    @staticmethod
    def _render_scenes(scenes: list, output_path: Optional[Path]) -> list[Path]:
        """
        Рендеринг списка сцен.
        """
        # Временная директория для отдельных сцен
        if output_path:
            per_scene_dir = output_path.parent / ".tgstatviz_scenes"
            per_scene_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Если output_path не указан, используем стандартную директорию Manim
            per_scene_dir = None

        rendered_videos = []

        for i, (scene_class, _) in enumerate(scenes, start=1):
            print(f"  Рендеринг сцены {i}/{len(scenes)} ({scene_class.__name__})...")

            try:
                if per_scene_dir:
                    # Устанавливаем путь для этой сцены
                    scene_output = per_scene_dir / f"scene_{i:03d}.mp4"

                    # Используем tempconfig для изоляции настроек сцены
                    with tempconfig({"output_file": str(scene_output)}):
                        scene = scene_class()
                        scene.render()

                    if scene_output.exists():
                        rendered_videos.append(scene_output)
                else:
                    # Рендерим в стандартное место Manim
                    scene = scene_class()
                    scene.render()

            # pylint: disable=broad-exception-caught
            except Exception as e:
                print(f"\tПредупреждение: не удалось отрендерить сцену {i}: {e}")
                continue

        return rendered_videos

    @staticmethod
    def _finalize_single_video(source: Path, destination: Path) -> None:
        """
        Переместить единственное видео в финальную директорию.
        """
        if destination.exists():
            destination.unlink()

        destination.parent.mkdir(parents=True, exist_ok=True)
        source.replace(destination)

        print(f"\nВидео сохранено: {destination}")

    @staticmethod
    def _load_chat(export_dir: Path) -> Chat:
        """
        Загрузка чата через адаптер
        """
        loader = JSONExportLoader.from_export_dir(export_dir)
        chats = loader.load_chats()

        # На начальной стадии берём первый чат
        if not chats:
            raise ValueError("В экспорте не найдено ни одного чата")

        return chats[0]

    @staticmethod
    def _print_chat_info(chat: Chat) -> None:
        """
        Вывод информации о загруженном чате
        """
        print(f"Чат: {chat.name}")
        print(f"Тип: {chat.type.value}")
        print(f"ID: {chat.id}")
        print(f"Сообщений: {len(chat.messages)}")

        authors = {msg.author.id for msg in chat.messages if msg.author}
        print(f"Авторов: {len(authors)}")

    @staticmethod
    def _configure_manim_quality(quality: str) -> None:
        """
        Настройка качества рендеринга Manim
        """
        quality_map = {
            "low": "low_quality",
            "medium": "medium_quality",
            "high": "high_quality",
        }

        manim_quality = quality_map.get(quality, "low_quality")
        manim_config.quality = manim_quality

        print(f"Качество Manim: {manim_quality}")
