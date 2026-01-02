"""
Модели для анализа экспортов Telegram.

Модуль содержит неизменяемые сущности чата и сообщений.
Модели не выполняют расчёт метрик и не содержат логики визуализации.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Optional, Sequence

# Строковой идентификатор сущности из экспорта или вычисленного домена
EntityId = str


class ChatType(str, Enum):
    """
    Тип диалога в экспорте Telegram
    """

    # Избранное
    SAVED_MESSAGES = "saved_messages"
    # Ответы авторов каналов на собственные комментарии
    REPLIES = "replies"
    # Личный чат один на один
    PERSONAL = "personal_chat"
    # Чат с ботом
    BOT_CHAT = "bot_chat"

    # Приватная группа
    PRIVATE_GROUP = "private_group"
    # Приватная супергруппа
    PRIVATE_SUPERGROUP = "private_supergroup"
    # Публичная супергруппа
    PUBLIC_SUPERGROUP = "public_supergroup"

    # Приватный канал
    PRIVATE_CHANNEL = "private_channel"
    # Публичный канал
    PUBLIC_CHANNEL = "public_channel"

    # Неизвестный тип
    UNKNOWN = "unknown"


class MessageType(str, Enum):
    """
    Тип сообщения в экспорте Telegram
    """

    # Сообщение пользователя
    REGULAR = "message"
    # Служебное сообщение
    SERVICE = "service"
    # Неизвестный тип
    UNKNOWN = "unknown"


class MediaType(str, Enum):
    """
    Тип медиа вложения сообщения
    """

    # Фотография
    PHOTO = "photo"
    # Документ/файл
    DOCUMENT = "document"

    # Стикер
    STICKER = "sticker"
    # Кружок
    VIDEO_MESSAGE = "video_message"
    # Голосовое сообщение
    VOICE_MESSAGE = "voice_message"
    # gif или что-то вроде того
    ANIMATION = "animation"
    # Видео
    VIDEO = "video_file"
    # аудиофайл
    AUDIO_FILE = "audio_file"

    # Неизвестный тип
    UNKNOWN = "unknown"


class TextEntityType(str, Enum):
    """
    Тип сущности форматированного текста/ссылки
    """

    # Полужирный
    BOLD = "bold"
    # Курсив
    ITALIC = "italic"
    # Подчеркнутый
    UNDERLINE = "underline"
    # Зачеркнутый
    STRIKETHROUGH = "strikethrough"
    # Спойлер (скрытый)
    SPOILER = "spoiler"
    # Код
    CODE = "code"
    # Блок кода с языком
    PRE = "pre"

    # Ссылка, где текст отдельно от href
    TEXT_LINK = "text_link"
    # Ссылка в тексте
    URL = "url"
    # Упоминание через @
    MENTION = "mention"
    HASHTAG = "hashtag"
    # Финансовый тикер
    CASHTAG = "cashtag"
    BOT_COMMAND = "bot_command"
    EMAIL = "email"
    PHONE = "phone"

    CUSTOM_EMOJI = "custom_emoji"

    # Неизвестный тип
    UNKNOWN = "unknown"

    @classmethod
    def from_raw(cls, value: str) -> "TextEntityType":
        """
        Безопасное создание из сырого значения экспорта.
        Возвращает UNKNOWN для нераспознанных типов.
        """
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


@dataclass(frozen=True, slots=True)
class Author:
    """
    Автор сообщения
    """

    # ID автора в рамках экспорта
    id: EntityId
    # Отображаемое имя автора на момент экспорта
    name: str


@dataclass(frozen=True, slots=True)
class TextEntity:
    """
    Сущность форматированного текста
    """

    # Тип сущности
    type: TextEntityType
    # Текст сущности, если он вынесен отдельно
    text: Optional[str] = None
    # Ссылка (если сущность является ссылкой)
    href: Optional[str] = None
    # Сырой JSON
    raw: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Message:
    """
    Сообщение чата
    """

    # ID сообщения в рамках конкретного чата
    id: int
    # Время отправки сообщения
    date: datetime
    # Автор сообщения (может отсутствовать для некоторых service-сообщений)
    author: Optional[Author] = None

    # Тип сообщения
    type: MessageType = MessageType.REGULAR

    # Нормализованный текст сообщения, если есть
    text: Optional[str] = None
    # Разметка текста, ссылки и форматирование
    text_entities: Sequence[TextEntity] = field(default_factory=tuple)

    # Идентификатор сообщения, на которое дан ответ
    reply_to_id: Optional[int] = None
    # Время последнего редактирования, если было
    edited_at: Optional[datetime] = None

    # Источник пересылки в человекочитаемом виде
    forwarded_from: Optional[str] = None

    # Тип вложения, если вложение есть
    media_type: Optional[MediaType] = None
    # Путь к вложению относительно каталога экспорта
    media_path: Optional[str] = None

    # Сырой JSON
    raw: Mapping[str, Any] = field(default_factory=dict)

    @property
    def has_text(self) -> bool:
        """
        Признак наличия текстового содержимого
        """
        return bool(self.text)

    @property
    def has_author(self) -> bool:
        """
        Признак наличия автора
        """
        return self.author is not None

    @property
    def is_reply(self) -> bool:
        """
        Признак ответа на другое сообщение
        """
        return self.reply_to_id is not None

    @property
    def is_edited(self) -> bool:
        """
        Признак редактирования сообщения
        """
        return self.edited_at is not None

    @property
    def is_forwarded(self) -> bool:
        """
        Признак пересланного сообщения
        """
        return self.forwarded_from is not None

    @property
    def has_media(self) -> bool:
        """
        Признак наличия медиа вложения
        """
        if self.media_type is not None:
            return True
        if self.media_path:
            return True

        # На всякий случай
        for key in ("photo", "file", "document", "sticker", "media_type"):
            if self.raw.get(key):
                return True

        return False


@dataclass(frozen=True, slots=True)
class Chat:
    """
    Чат с сообщениями
    """

    # ID чата в рамках экспорта
    id: int
    # Название чата на момент экспорта
    name: str
    # Тип чата
    type: ChatType

    # Сообщения чата в порядке, который задан экспортом
    messages: Sequence[Message] = field(default_factory=tuple)

    # Сырой JSON
    raw: Mapping[str, Any] = field(default_factory=dict)

    @property
    def is_personal(self) -> bool:
        """
        Признак личного диалога
        """
        return self.type == ChatType.PERSONAL

    @property
    def is_group(self) -> bool:
        """
        Признак группового чата
        """
        return self.type in {
            ChatType.PRIVATE_GROUP,
            ChatType.PRIVATE_SUPERGROUP,
            ChatType.PUBLIC_SUPERGROUP,
        }

    @property
    def is_channel(self) -> bool:
        """
        Признак канала
        """
        return self.type in {
            ChatType.PRIVATE_CHANNEL,
            ChatType.PUBLIC_CHANNEL,
        }
