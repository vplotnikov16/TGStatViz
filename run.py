"""
Вспомогательный скрипт для удобного запуска рендеринга TGStatViz

Позволяет настроить пути к ffmpeg/MikTeX, экспорту, конфигу и запустить
команду render без ручного набора всех аргументов в консоли.

"""

import os
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class QualityEnum(str, Enum):
    """
    Качество рендера видео
    """
    # 480p
    LOW = "low"
    # 720p
    MEDIUM = "medium"
    # 1080p
    HIGH = "high"


# Путь к папке ffmpeg (для склейки видео)
FFMPEG_BIN_DIR: Optional[Path] = Path(r"C:\dev\tools\ffmpeg\bin")
# Путь к папке MikTeX (для LaTeX/кириллицы в Manim)
MIKTEX_BIN_DIR: Optional[Path] = Path(r"C:\dev\tools\miktex\texmfs\install\miktex\bin\x64")
# Базовая директория проекта
BASE_DIR: Path = Path(__file__).resolve().parent
# Путь к каталогу экспорта Telegram (должен содержать result.json)
PATH_TO_EXPORT_DIR: Path = BASE_DIR / "exports" / "ChatExport_2025-12-31"
# Путь к YAML-конфигу раскадровки
PATH_TO_STORYBOARD_YAML: Path = BASE_DIR / "configs" / "example.yaml"
# Куда сохранить итоговое видео
OUTPUT_FILE: Optional[Path] = BASE_DIR / "output" / "video.mp4"

# Качество рендера (low/medium/high)
QUALITY: QualityEnum = QualityEnum.LOW


@dataclass(frozen=True)
class RenderCommand:
    """
    Конфигурация команды render
    """
    export_dir: Path
    storyboard_yaml: Path
    quality: QualityEnum
    output_file: Optional[Path]


def build_command(cfg: RenderCommand) -> list[str]:
    """
    Формирование команды для subprocess

    Args:
        cfg: конфигурация рендера

    Returns:
        Список аргументов для subprocess.run()
    """
    cmd = [sys.executable, "-m", "tgstatviz", "render"]

    # Позиционные аргументы
    cmd += [str(cfg.export_dir), str(cfg.storyboard_yaml)]

    # Качество
    cmd += ["-q", cfg.quality.value]

    # Выходной файл (опционально)
    if cfg.output_file is not None:
        cmd += ["-o", str(cfg.output_file)]

    return cmd


def setup_environment() -> None:
    """
    Настройка PATH
    """
    path_additions: list[str] = []

    if FFMPEG_BIN_DIR is not None and FFMPEG_BIN_DIR.exists():
        path_additions.append(str(FFMPEG_BIN_DIR))
        print(f"ffmpeg: {FFMPEG_BIN_DIR}")

    if MIKTEX_BIN_DIR is not None and MIKTEX_BIN_DIR.exists():
        path_additions.append(str(MIKTEX_BIN_DIR))
        print(f"MikTeX: {MIKTEX_BIN_DIR}")

    if path_additions:
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = os.pathsep.join(path_additions) + os.pathsep + current_path


def main() -> None:
    """
    Главная функция запуска
    """
    # Настройка окружения (PATH для ffmpeg/MikTeX)
    setup_environment()
    # Формирование конфигурации
    cfg = RenderCommand(
        export_dir=PATH_TO_EXPORT_DIR,
        storyboard_yaml=PATH_TO_STORYBOARD_YAML,
        quality=QUALITY,
        output_file=OUTPUT_FILE,
    )
    # Формирование команды
    cmd = build_command(cfg)
    # Запуск
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
