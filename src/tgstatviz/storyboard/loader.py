"""
Загрузка storyboard из YAML-файла
"""
from pathlib import Path

import yaml
from pydantic import ValidationError

from tgstatviz.storyboard.schema import ProjectConfig, LegacyProjectConfig


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
        # Пробуем новый формат (с project-обёрткой)
        if "project" in data:
            project_data = data["project"]
            project_data["defaults"] = data.get("defaults", {})
            project_data["slides"] = data.get("slides", [])
            config = ProjectConfig.model_validate(project_data)
        else:
            # Старый формат (без project-обёртки)
            config_legacy = LegacyProjectConfig.model_validate(data)
            # Преобразуем в новый формат
            config = ProjectConfig(
                title=config_legacy.title,
                description=config_legacy.description,
                defaults=config_legacy.defaults,
                slides=config_legacy.slides
            )
    except ValidationError as e:
        raise StoryboardLoadError(f"Ошибка валидации схемы storyboard:\n{e}") from e

    return config
