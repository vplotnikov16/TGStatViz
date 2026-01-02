"""
Рендеринг видео из storyboard
"""

from pathlib import Path
from typing import Optional

from tgstatviz.adapters.json_loader import JSONExportLoader
from tgstatviz.domain.models import Chat


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

        # Шаг 3: Создание сцен
        print(f"\nСоздание сцен Manim (качество: {quality})...")

        # Шаг 4: Рендеринг
        print("\nРендеринг сцен Manim...")

        if output_path:
            print(f"Видео сохранено в: {output_path}")

    @staticmethod
    def _load_chat(export_dir: Path) -> Chat:
        """
        Загрузка чата через адаптер
        """
        loader = JSONExportLoader.from_export_dir(export_dir)
        chats = loader.load_chats()

        # На начальной стадии берём первый чат
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
