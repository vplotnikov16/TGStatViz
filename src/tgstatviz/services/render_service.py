"""
Рендеринг видео из storyboard
"""

from pathlib import Path
from typing import Optional

from manim import tempconfig

from tgstatviz.adapters.json_loader import JSONExportLoader
from tgstatviz.domain.models import Chat
from tgstatviz.storyboard.loader import load_storyboard
from tgstatviz.viz.scene_compiler import SceneCompiler
from tgstatviz.utils.manim_config import initialize_manim
from tgstatviz.utils.video_concat import concat_videos, FFmpegNotFoundError, VideoConcatError


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
        # Инициализация Manim (качество + кириллица)
        print(f"Настройка Manim (качество: {quality})...")
        initialize_manim(quality=quality, enable_cyrillic=True)

        # Шаг 1: Загрузка чата
        print(f"\nЗагрузка чата из {export_dir}...")
        chat = self._load_chat(export_dir)
        self._print_chat_info(chat)

        # Шаг 2: Загрузка storyboard
        print(f"\nЗагрузка storyboard из {storyboard_path}...")
        config = load_storyboard(storyboard_path)
        print(f"Загружен storyboard: {config.title}")
        print(f"Описание: {config.description}")
        print(f"Слайдов: {len(config.slides)}")

        # Шаг 3: Компиляция сцен
        print("\nКомпиляция сцен...")
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
                # Несколько сцен - склеиваем через ffmpeg
                self._finalize_multiple_videos(rendered_videos, output_path)
        else:
            print("\nРендеринг завершён (выходной путь не указан)")

    @staticmethod
    def _render_scenes(scenes: list, output_path: Optional[Path]) -> list[Path]:
        """
        Рендеринг списка сцен
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
    def _finalize_multiple_videos(video_paths: list[Path], output_path: Path) -> None:
        """
        Склеить несколько видео в один файл.

        Args:
            video_paths: Список путей к отрендеренным сценам
            output_path: Путь к итоговому видеофайлу
        """
        print(f"\nСклейка {len(video_paths)} сцен в единое видео...")

        try:
            concat_videos(video_paths, output_path)
            print(f"\nВидео сохранено: {output_path}")

        except FFmpegNotFoundError as e:
            print(f"\nОшибка: {e}")
            print(f"Отдельные сцены сохранены в: {video_paths[0].parent}")

        except VideoConcatError as e:
            print(f"\nОшибка склейки: {e}")
            print(f"Отдельные сцены сохранены в: {video_paths[0].parent}")

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
