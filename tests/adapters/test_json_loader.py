"""
Тесты для загрузчика JSON-экспорта Telegram
"""

import json
from pathlib import Path

import pytest

from tgstatviz.adapters.json_loader import JSONExportFormatError, JSONExportLoader
from tgstatviz.domain.models import (
    ChatType,
    MediaType,
    MessageType,
    TextEntityType,
)


@pytest.fixture
def temp_export_dir(tmp_path: Path) -> Path:
    """
    Временный каталог экспорта для тестов
    """
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    return export_dir


@pytest.fixture
def valid_single_chat_export(temp_export_dir: Path) -> Path:
    """
    Валидный экспорт с одним чатом и несколькими сообщениями
    """
    data = {
        "chats": {
            "list": [
                {
                    "id": 123456789,
                    "name": "Тестовый чат",
                    "type": "personal_chat",
                    "messages": [
                        {
                            "id": 1,
                            "type": "message",
                            "date": "2024-01-15T10:30:00",
                            "from": "Иван",
                            "from_id": "user123",
                            "text": "Привет!",
                        },
                        {
                            "id": 2,
                            "type": "message",
                            "date": "2024-01-15T10:31:00",
                            "from": "Мария",
                            "from_id": "user456",
                            "text": [
                                "Привет, ",
                                {"type": "bold", "text": "Иван"},
                                "!",
                            ],
                            "reply_to_message_id": 1,
                        },
                    ],
                }
            ]
        }
    }

    result_path = temp_export_dir / "result.json"
    result_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return temp_export_dir


@pytest.fixture
def export_with_media(temp_export_dir: Path) -> Path:
    """
    Экспорт с медиа-вложениями
    """
    data = {
        "chats": {
            "list": [
                {
                    "id": 999,
                    "name": "Медиа чат",
                    "type": "private_group",
                    "messages": [
                        {
                            "id": 10,
                            "type": "message",
                            "date": "2024-02-01T12:00:00",
                            "from": "Петр",
                            "from_id": "user789",
                            "text": "Фото дня",
                            "photo": "photos/photo_001.jpg",
                        },
                        {
                            "id": 11,
                            "type": "message",
                            "date": "2024-02-01T12:05:00",
                            "from": "Анна",
                            "from_id": "user321",
                            "media_type": "sticker",
                            "file": "stickers/sticker_002.webp",
                        },
                    ],
                }
            ]
        }
    }

    result_path = temp_export_dir / "result.json"
    result_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return temp_export_dir


@pytest.fixture
def export_with_service_messages(temp_export_dir: Path) -> Path:
    """
    Экспорт со служебными сообщениями
    """
    data = {
        "chats": {
            "list": [
                {
                    "id": 777,
                    "name": "Групповой чат",
                    "type": "private_supergroup",
                    "messages": [
                        {
                            "id": 100,
                            "type": "service",
                            "date": "2024-03-01T09:00:00",
                            "text": "Петр создал группу",
                        },
                        {
                            "id": 101,
                            "type": "message",
                            "date": "2024-03-01T09:05:00",
                            "from": "Петр",
                            "from_id": "user789",
                            "text": "Всем привет!",
                        },
                    ],
                }
            ]
        }
    }

    result_path = temp_export_dir / "result.json"
    result_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return temp_export_dir


@pytest.fixture
def export_single_chat_root(temp_export_dir: Path) -> Path:
    """
    Экспорт одного чата (messages в корне)
    """
    data = {
        "id": 555,
        "name": "Прямой экспорт",
        "type": "bot_chat",
        "messages": [
            {
                "id": 1,
                "type": "message",
                "date": "2024-04-01T14:00:00",
                "from": "Бот",
                "from_id": "bot001",
                "text": "Команда получена",
            }
        ],
    }

    result_path = temp_export_dir / "result.json"
    result_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return temp_export_dir


class TestJSONExportLoaderInitialization:
    """
    Тесты инициализации загрузчика
    """

    def test_from_export_dir_success(self, valid_single_chat_export: Path):
        """
        Успешное создание загрузчика из валидного каталога
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        assert loader.export_dir == valid_single_chat_export
        assert loader.result_json_path == valid_single_chat_export / "result.json"

    def test_from_export_dir_missing_directory(self, tmp_path: Path):
        """
        Ошибка при отсутствии каталога экспорта
        """
        missing_dir = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError, match="Каталог экспорта не найден"):
            JSONExportLoader.from_export_dir(missing_dir)

    def test_from_export_dir_missing_result_json(self, temp_export_dir: Path):
        """
        Ошибка при отсутствии result.json
        """
        with pytest.raises(FileNotFoundError, match="Файл JSON не найден"):
            JSONExportLoader.from_export_dir(temp_export_dir)


class TestLoadChats:
    """
    Тесты загрузки чатов
    """

    def test_load_single_chat_from_chats_list(self, valid_single_chat_export: Path):
        """
        Загрузка одного чата из chats.list
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chats = loader.load_chats()

        assert len(chats) == 1
        chat = chats[0]

        assert chat.id == 123456789
        assert chat.name == "Тестовый чат"
        assert chat.type == ChatType.PERSONAL
        assert len(chat.messages) == 2

    def test_load_chat_from_root_messages(self, export_single_chat_root: Path):
        """
        Загрузка чата когда messages в корне
        """
        loader = JSONExportLoader.from_export_dir(export_single_chat_root)
        chats = loader.load_chats()

        assert len(chats) == 1
        chat = chats[0]

        assert chat.id == 555
        assert chat.name == "Прямой экспорт"
        assert chat.type == ChatType.BOT_CHAT
        assert len(chat.messages) == 1

    def test_load_chats_caching(self, valid_single_chat_export: Path):
        """
        Проверка кэширования результата load_chats
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chats1 = loader.load_chats()
        chats2 = loader.load_chats()

        assert chats1 is chats2

    def test_load_chat_by_name(self, valid_single_chat_export: Path):
        """
        Поиск чата по имени
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chat = loader.load_chat_by_name("Тестовый чат")

        assert chat is not None
        assert chat.name == "Тестовый чат"

    def test_load_chat_by_name_not_found(self, valid_single_chat_export: Path):
        """
        Поиск несуществующего чата по имени
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chat = loader.load_chat_by_name("Несуществующий")

        assert chat is None

    def test_load_chat_by_id(self, valid_single_chat_export: Path):
        """
        Поиск чата по ID
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chat = loader.load_chat_by_id(123456789)

        assert chat is not None
        assert chat.id == 123456789

    def test_load_chat_by_id_not_found(self, valid_single_chat_export: Path):
        """
        Поиск несуществующего чата по ID
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chat = loader.load_chat_by_id(999999)

        assert chat is None


class TestMessageParsing:
    """
    Тесты парсинга сообщений
    """

    def test_parse_simple_message(self, valid_single_chat_export: Path):
        """
        Парсинг простого текстового сообщения
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chats = loader.load_chats()
        message = chats[0].messages[0]

        assert message.id == 1
        assert message.type == MessageType.REGULAR
        assert message.text == "Привет!"
        assert message.author is not None
        assert message.author.name == "Иван"
        assert message.author.id == "user123"

    def test_parse_message_with_formatted_text(self, valid_single_chat_export: Path):
        """
        Парсинг сообщения с форматированным текстом
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chats = loader.load_chats()
        message = chats[0].messages[1]

        assert message.text == "Привет, Иван!"
        assert len(message.text_entities) == 1

        entity = message.text_entities[0]
        assert entity.type == TextEntityType.BOLD
        assert entity.text == "Иван"

    def test_parse_reply_message(self, valid_single_chat_export: Path):
        """
        Парсинг сообщения-ответа
        """
        loader = JSONExportLoader.from_export_dir(valid_single_chat_export)
        chats = loader.load_chats()
        message = chats[0].messages[1]

        assert message.is_reply
        assert message.reply_to_id == 1

    def test_parse_service_message(self, export_with_service_messages: Path):
        """
        Парсинг служебного сообщения
        """
        loader = JSONExportLoader.from_export_dir(export_with_service_messages)
        chats = loader.load_chats()
        message = chats[0].messages[0]

        assert message.type == MessageType.SERVICE
        assert message.text == "Петр создал группу"
        assert message.author is None

    def test_parse_message_with_photo(self, export_with_media: Path):
        """
        Парсинг сообщения с фото
        """
        loader = JSONExportLoader.from_export_dir(export_with_media)
        chats = loader.load_chats()
        message = chats[0].messages[0]

        assert message.has_media
        assert message.media_type == MediaType.PHOTO
        assert message.media_path == "photos/photo_001.jpg"

    def test_parse_message_with_sticker(self, export_with_media: Path):
        """
        Парсинг сообщения со стикером
        """
        loader = JSONExportLoader.from_export_dir(export_with_media)
        chats = loader.load_chats()
        message = chats[0].messages[1]

        assert message.has_media
        assert message.media_type == MediaType.STICKER
        assert message.media_path == "stickers/sticker_002.webp"


class TestEdgeCases:
    """
    Тесты граничных случаев и нестандартных данных
    """

    def test_message_without_author(self, temp_export_dir: Path):
        """
        Сообщение без автора
        """
        data = {
            "chats": {
                "list": [
                    {
                        "id": 1,
                        "name": "Чат",
                        "type": "personal_chat",
                        "messages": [
                            {
                                "id": 1,
                                "type": "service",
                                "date": "2024-01-01T00:00:00",
                                "text": "Системное сообщение",
                            }
                        ],
                    }
                ]
            }
        }

        result_path = temp_export_dir / "result.json"
        result_path.write_text(json.dumps(data), encoding="utf-8")

        loader = JSONExportLoader.from_export_dir(temp_export_dir)
        chats = loader.load_chats()
        message = chats[0].messages[0]

        assert not message.has_author
        assert message.author is None

    def test_message_with_empty_text(self, temp_export_dir: Path):
        """
        Сообщение с пустым текстом
        """
        data = {
            "chats": {
                "list": [
                    {
                        "id": 1,
                        "name": "Чат",
                        "type": "personal_chat",
                        "messages": [
                            {
                                "id": 1,
                                "type": "message",
                                "date": "2024-01-01T00:00:00",
                                "from": "User",
                                "from_id": "u1",
                                "text": "",
                            }
                        ],
                    }
                ]
            }
        }

        result_path = temp_export_dir / "result.json"
        result_path.write_text(json.dumps(data), encoding="utf-8")

        loader = JSONExportLoader.from_export_dir(temp_export_dir)
        chats = loader.load_chats()
        message = chats[0].messages[0]

        assert not message.has_text
        assert message.text == ""

    def test_unknown_chat_type(self, temp_export_dir: Path):
        """
        Неизвестный тип чата
        """
        data = {
            "chats": {
                "list": [
                    {
                        "id": 1,
                        "name": "Странный чат",
                        "type": "future_type_v2",
                        "messages": [],
                    }
                ]
            }
        }

        result_path = temp_export_dir / "result.json"
        result_path.write_text(json.dumps(data), encoding="utf-8")

        loader = JSONExportLoader.from_export_dir(temp_export_dir)
        chats = loader.load_chats()

        assert chats[0].type == ChatType.UNKNOWN

    def test_unknown_text_entity_type(self, temp_export_dir: Path):
        """
        Неизвестный тип форматирования текста
        """
        data = {
            "chats": {
                "list": [
                    {
                        "id": 1,
                        "name": "Чат",
                        "type": "personal_chat",
                        "messages": [
                            {
                                "id": 1,
                                "type": "message",
                                "date": "2024-01-01T00:00:00",
                                "from": "User",
                                "from_id": "u1",
                                "text": [
                                    {"type": "super_new_feature", "text": "Текст"}
                                ],
                            }
                        ],
                    }
                ]
            }
        }

        result_path = temp_export_dir / "result.json"
        result_path.write_text(json.dumps(data), encoding="utf-8")

        loader = JSONExportLoader.from_export_dir(temp_export_dir)
        chats = loader.load_chats()
        message = chats[0].messages[0]

        assert len(message.text_entities) == 1
        assert message.text_entities[0].type == TextEntityType.UNKNOWN

    def test_invalid_message_date_skips_message(self, temp_export_dir: Path):
        """
        Сообщение с невалидной датой пропускается с предупреждением
        """
        data = {
            "chats": {
                "list": [
                    {
                        "id": 1,
                        "name": "Чат",
                        "type": "personal_chat",
                        "messages": [
                            {
                                "id": 1,
                                "type": "message",
                                "date": "invalid-date",
                                "from": "User",
                                "from_id": "u1",
                                "text": "Привет",
                            },
                            {
                                "id": 2,
                                "type": "message",
                                "date": "2024-01-01T00:00:00",
                                "from": "User",
                                "from_id": "u1",
                                "text": "Мир",
                            },
                        ],
                    }
                ]
            }
        }

        result_path = temp_export_dir / "result.json"
        result_path.write_text(json.dumps(data), encoding="utf-8")

        loader = JSONExportLoader.from_export_dir(temp_export_dir)

        with pytest.warns(UserWarning, match="Пропущено сообщение"):
            chats = loader.load_chats()

        # Только второе сообщение должно загрузиться
        assert len(chats[0].messages) == 1
        assert chats[0].messages[0].id == 2


class TestErrorHandling:
    """
    Тесты обработки ошибок
    """

    def test_invalid_json_structure(self, temp_export_dir: Path):
        """
        Невалидная структура JSON
        """
        data = {"some_random_key": "value"}

        result_path = temp_export_dir / "result.json"
        result_path.write_text(json.dumps(data), encoding="utf-8")

        loader = JSONExportLoader.from_export_dir(temp_export_dir)

        with pytest.raises(
                JSONExportFormatError, match="Не удалось распознать структуру JSON"
        ):
            loader.load_chats()

    def test_json_array_in_root(self, temp_export_dir: Path):
        """
        JSON-массив в корне вместо объекта
        """
        data = [{"id": 1, "name": "test"}]

        result_path = temp_export_dir / "result.json"
        result_path.write_text(json.dumps(data), encoding="utf-8")

        loader = JSONExportLoader.from_export_dir(temp_export_dir)

        with pytest.raises(
                JSONExportFormatError, match="Ожидался JSON-объект \\(dict\\) в корне файла"
        ):
            loader.load_chats()
