"""
Загрузка storyboard из YAML-файла
"""
from pathlib import Path

import yaml
from pydantic import ValidationError

from tgstatviz.storyboard.schema import ProjectConfig


class StoryboardLoadError(Exception):
    """Ошибка загрузки storyboard"""


def load_storyboard(path: Path) -> ProjectConfig:
    """
    Загрузка и валидация storyboard из YAML-файла
    """
    if not path.exists():
        raise StoryboardLoadError(f"Файл storyboard не найден: {path}")

    if not path.is_file():
        raise StoryboardLoadError(f"Путь не является файлом: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise StoryboardLoadError(f"Ошибка парсинга YAML: {e}") from e
    except OSError as e:
        raise StoryboardLoadError(f"Ошибка чтения файла: {e}") from e

    if data is None:
        raise StoryboardLoadError("YAML-файл пустой")

    if not isinstance(data, dict):
        raise StoryboardLoadError(
            f"YAML должен содержать объект (dict), получен: {type(data).__name__}"
        )

    try:
        config = ProjectConfig.model_validate(data)
    except ValidationError as e:
        raise StoryboardLoadError(f"Ошибка валидации схемы storyboard:\n{e}") from e

    return config
