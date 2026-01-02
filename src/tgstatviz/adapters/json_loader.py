"""
Загрузчик экспорта Telegram-чата в формате JSON

Назначение модуля:
- Чтение JSON-экспорта
- Преобразование данных в доменные модели Chat и Message

Модуль не считает метрики и не выполняет визуализацию
"""

import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from tgstatviz.domain.models import (
    Author,
    Chat,
    ChatType,
    MediaType,
    Message,
    MessageType,
    TextEntity,
    TextEntityType,
)


class JSONExportFormatError(ValueError):
    """
    Ошибка формата экспорта Telegram
    """


class JSONExportLoader:
    """
    Загрузчик экспорта

    Основной сценарий:
    - loader = JSONExportLoader.from_export_dir(Path("..."))
    - chats = loader.load_chats()
    """

    def __init__(self, export_dir: Path):
        """
        export_dir - каталог экспорта, содержащий result.json и вложения
        """
        self._export_dir = export_dir
        self._cached_root: Optional[Mapping[str, Any]] = None
        self._cached_chats: Optional[Sequence[Chat]] = None

    @classmethod
    def from_export_dir(cls, export_dir: Path) -> "JSONExportLoader":
        """
        Создание загрузчика по каталогу экспорта

        export_dir - каталог экспорта, содержащий result.json и вложения
        """
        export_dir = Path(export_dir)
        result_json_path = export_dir / 'result.json'

        if not export_dir.exists():
            raise FileNotFoundError(f"Каталог экспорта не найден: {export_dir}")
        if not result_json_path.exists():
            raise FileNotFoundError(f"Файл JSON не найден: {result_json_path}")

        return cls(export_dir=export_dir)

    @property
    def export_dir(self) -> Path:
        """
        Каталог экспорта (корень)
        """
        return self._export_dir

    @property
    def result_json_path(self) -> Path:
        """
        Путь к result.json
        """
        return self._export_dir / 'result.json'

    def load_chats(self) -> Sequence[Chat]:
        """
        Загрузка всех чатов из result.json
        """
        if self._cached_chats is not None:
            return self._cached_chats

        data = self._load_root()
        chats = self._parse_chats_from_root(data)

        self._cached_chats = chats
        return chats

    def _load_root(self) -> Mapping[str, Any]:
        if self._cached_root is None:
            self._cached_root = self._read_json(self.result_json_path)
        return self._cached_root

    def _parse_chats_from_root(self, data: Mapping[str, Any]) -> Sequence[Chat]:
        # Вариант 1 - "полный экспорт": корень содержит chats.list
        chats_block = data.get("chats")
        if isinstance(chats_block, dict) and isinstance(chats_block.get("list"), list):
            chats_list = chats_block["list"]
            return tuple(self._parse_chat(obj) for obj in chats_list)

        # Вариант 2 - "экспорт одного чата": некоторые инструменты могут
        # класть сообщения сразу в корень или под другим ключом.
        if isinstance(data.get("messages"), list):
            # Пытаемся собрать "чат" из того, что есть
            pseudo_chat: dict[str, Any] = {
                "id": data.get("id", 0),
                "name": data.get("name", data.get("title", "Неизвестный чат")),
                "type": data.get("type", "unknown"),
                "messages": data.get("messages", []),
            }
            return (self._parse_chat(pseudo_chat),)

        raise JSONExportFormatError(
            "Не удалось распознать структуру JSON. Ожидалось наличие chats.list или messages."
        )

    def load_chat_by_name(self, name: str) -> Optional[Chat]:
        """
        Поиск чата по имени
        """
        for chat in self.load_chats():
            if chat.name == name:
                return chat
        return None

    def load_chat_by_id(self, chat_id: int) -> Optional[Chat]:
        """
        Поиск чата по id
        """
        for chat in self.load_chats():
            if chat.id == chat_id:
                return chat
        return None

    @staticmethod
    def _read_json(path: Path) -> Mapping[str, Any]:
        """
        Десериализация JSON-файла
        """
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)

        if not isinstance(obj, dict):
            raise JSONExportFormatError(f"Ожидался JSON-объект (dict) в корне файла: {path}")

        return obj

    def _parse_chat(self, raw_chat: Mapping[str, Any]) -> Chat:
        """
        Преобразование сырого объекта чата Telegram в доменную модель Chat
        """
        chat_id = self._to_int(raw_chat.get("id"), default=0)
        chat_name = self._to_str(raw_chat.get("name")) or self._to_str(raw_chat.get("title")) or "Неизвестный чат"
        chat_type = self._parse_chat_type(self._to_str(raw_chat.get("type")))

        raw_messages = raw_chat.get("messages")
        if raw_messages is None:
            raw_messages = raw_chat.get("history")
        if not isinstance(raw_messages, list):
            raw_messages = []

        messages: list[Message] = []
        for idx, m in enumerate(raw_messages):
            if not isinstance(m, dict):
                continue
            try:
                msg = self._parse_message(m)
                messages.append(msg)
            except ValueError as e:
                msg_id = m.get("id", idx)
                warnings.warn(
                    f"Пропущено сообщение id={msg_id} в чате '{chat_name}' (id={chat_id}): {e}",
                    UserWarning,
                    stacklevel=2
                )

        return Chat(
            id=chat_id,
            name=chat_name,
            type=chat_type,
            messages=tuple(messages),
            raw=dict(raw_chat),
        )

    def _parse_message(self, raw_msg: Mapping[str, Any]) -> Message:
        """
        Преобразование сырого объекта сообщения Telegram в доменную модель Message
        """
        msg_id = self._to_int(raw_msg.get("id"), default=0)
        msg_type = self._parse_message_type(self._to_str(raw_msg.get("type")))

        # date обычно строка ISO, иногда с Z
        date = self._parse_datetime(self._to_str(raw_msg.get("date")))
        if date is None:
            raise ValueError(f"Не удалось распарсить дату сообщения: {raw_msg.get('date')}")

        author = self._parse_author(raw_msg)
        text, entities = self._parse_text_and_entities(raw_msg.get("text"))

        reply_to_id = self._to_int_optional(
            raw_msg.get("reply_to_message_id", raw_msg.get("reply_to_id"))
        )

        edited_at = self._parse_datetime(self._to_str(raw_msg.get("edited")))
        forwarded_from = self._to_str(raw_msg.get("forwarded_from"))

        media_type, media_path = self._parse_media(raw_msg)

        return Message(
            id=msg_id,
            date=date,
            author=author,
            type=msg_type,
            text=text,
            text_entities=entities,
            reply_to_id=reply_to_id,
            edited_at=edited_at,
            forwarded_from=forwarded_from,
            media_type=media_type,
            media_path=media_path,
            raw=dict(raw_msg),
        )

    def _parse_author(self, raw_msg: Mapping[str, Any]) -> Optional[Author]:
        """
        Разбор автора сообщения
        """
        from_name = self._to_str(raw_msg.get("from"))
        from_id = self._to_str(raw_msg.get("from_id"))

        if not from_name and not from_id:
            return None

        # Если id вдруг нет, то делаем псевдо-id из имени
        safe_id = from_id or f"name:{from_name}"
        safe_name = from_name or from_id or "Неизвестный автор"

        return Author(id=safe_id, name=safe_name)

    def _parse_text_and_entities(self, raw_text: Any) -> tuple[Optional[str], Sequence[TextEntity]]:
        """
        Нормализация текста
        """
        if raw_text is None:
            return None, ()

        # Простой вариант
        if isinstance(raw_text, str):
            return raw_text, ()

        # Составной вариант
        if isinstance(raw_text, list):
            parts: list[str] = []
            entities: list[TextEntity] = []

            for item in raw_text:
                if isinstance(item, str):
                    parts.append(item)
                    continue

                if isinstance(item, dict):
                    # Ожидаемые поля: type, text, href
                    item_text = self._to_str(item.get("text")) or ""
                    parts.append(item_text)

                    raw_type = self._to_str(item.get("type"))
                    if raw_type:
                        entities.append(
                            TextEntity(
                                type=TextEntityType.from_raw(raw_type),
                                text=self._to_str(item.get("text")),
                                href=self._to_str(item.get("href")),
                                raw=dict(item),
                            )
                        )
                    continue

                # На случай неожиданных типов
                parts.append(str(item))

            normalized = "".join(parts)
            normalized = normalized if normalized != "" else None
            return normalized, tuple(entities)

        # На случай неожиданных типов
        return str(raw_text), ()

    def _parse_media(self, raw_msg: Mapping[str, Any]) -> tuple[Optional[MediaType], Optional[str]]:
        """
        Парсинг базовой информации о вложениях
        """
        raw_media_type = self._to_str(raw_msg.get("media_type"))
        media_type = self._parse_media_type(raw_media_type)

        # Фото и файл лежат в экспорте отдельно
        photo = self._to_str(raw_msg.get("photo"))
        file_ = self._to_str(raw_msg.get("file"))

        if photo:
            return MediaType.PHOTO, photo
        if file_:
            # Если тип неизвестен, считаем "файлом"
            return media_type or MediaType.DOCUMENT, file_

        # На всякий случай пробежимся еще так
        for key in ("path", "media", "document", "sticker", "video_file", "audio_file"):
            value = self._to_str(raw_msg.get(key))
            if value:
                return media_type, value

        return media_type, None

    @staticmethod
    def _parse_chat_type(raw_type: Optional[str]) -> ChatType:
        """
        Безопасное преобразование тпа чата в ChatType
        """
        if not raw_type:
            return ChatType.UNKNOWN
        try:
            return ChatType(raw_type)
        except ValueError:
            return ChatType.UNKNOWN

    @staticmethod
    def _parse_message_type(raw_type: Optional[str]) -> MessageType:
        """
        Безопасное преобразование типа сообщения в MessageType
        """
        if not raw_type:
            return MessageType.UNKNOWN
        try:
            return MessageType(raw_type)
        except ValueError:
            return MessageType.UNKNOWN

    @staticmethod
    def _parse_media_type(raw_type: Optional[str]) -> Optional[MediaType]:
        """
        Безопасное преобразование media_type в MediaType
        """
        if not raw_type:
            return None
        try:
            return MediaType(raw_type)
        except ValueError:
            return MediaType.UNKNOWN

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """
        Разбор даты из строки.
        """
        if not value:
            return None

        v = value.strip()
        if v.endswith("Z"):
            v = v[:-1] + "+00:00"

        # datetime.fromisoformat не принимает некоторые варианты
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            pass

        # Чаще всего встречается "YYYY-mm-dd HH:MM:SS"
        for fmt in ("%Y-%m-%d %H:%M:%S",):
            try:
                return datetime.strptime(v, fmt)
            except ValueError:
                continue

        # Значит без даты
        return None

    @staticmethod
    def _to_int(value: Any, *, default: int) -> int:
        """
        Приведение к int со значением пол умолчанию
        """
        try:
            if value is None:
                return default
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _to_int_optional(value: Any) -> Optional[int]:
        """
        Попытка приведения к int
        """
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_str(value: Any) -> Optional[str]:
        """
        Приведение к строке
        """
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return str(value)
