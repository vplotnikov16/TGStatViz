"""
Утилиты для склейки видеофайлов через ffmpeg
"""
import subprocess
from pathlib import Path
from shutil import which


class FFmpegNotFoundError(Exception):
    """
    FFmpeg не найден в системе
    """


class VideoConcatError(Exception):
    """
    Ошибка склейки видео
    """


def _write_concat_list(list_path: Path, video_paths: list[Path]) -> None:
    """
    Формирование списка видеофайлов для конкатенации ffmpeg
    """
    list_path.parent.mkdir(parents=True, exist_ok=True)

    with list_path.open("w", encoding="utf-8") as f:
        for video_path in video_paths:
            # ffmpeg concat демультиплексор ожидает: file '<путь>'
            # Используем POSIX-стиль слэшей для лучшей совместимости на Windows
            f.write(f"file '{video_path.resolve().as_posix()}'\n")


def concat_videos(video_paths: list[Path], output_path: Path) -> None:
    """
    Объединение нескольких видео в один файл через ffmpeg concat демультиплексор

    Сначала пробуется копирование потоков (быстро, без потери качества),
    а при ошибке автоматически переключается на переэнкодирование
    """
    if not video_paths:
        raise ValueError("Список видео для склейки пуст")

    # Проверяем наличие ffmpeg
    ffmpeg = which("ffmpeg")
    if not ffmpeg:
        raise FFmpegNotFoundError("ffmpeg не найден")

    # Создаём временный файл со списком видео
    tmp_dir = output_path.parent / ".tgstatviz_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    concat_list = tmp_dir / "concat_list.txt"

    _write_concat_list(concat_list, video_paths)

    print(f"  Склейка {len(video_paths)} видео...")

    # Попытка 1: копирование потоков (быстро, без потери качества)
    success = _try_copy_streams(ffmpeg, concat_list, output_path)

    if success:
        print("\tСклейка завершена (копирование потоков)")
        return

    # Попытка 2: переэнкодирование (медленнее, но надёжнее)
    print("\tКопирование потоков не удалось, переэнкодирование...")
    success = _try_reencode(ffmpeg, concat_list, output_path)

    if success:
        print("\tСклейка завершена (переэнкодирование)")
        return

    raise VideoConcatError("Не удалось склеить видео ни одним из методов")


def _try_copy_streams(ffmpeg: str, concat_list: Path, output_path: Path) -> bool:
    """
    Попытка склеить видео копированием потоков (без переэнкодирования)
    """
    cmd = [
        ffmpeg,
        # Перезаписать выходной файл
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        # Копирование без переэнкодирования
        "-c", "copy",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=False,
            text=True
        )
        return result.returncode == 0
    # pylint: disable=broad-exception-caught
    except Exception:
        return False


def _try_reencode(ffmpeg: str, concat_list: Path, output_path: Path) -> bool:
    """
    Попытка склеить видео с переэнкодированием
    """
    cmd = [
        ffmpeg,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        # H.264 кодек
        "-c:v", "libx264",
        # Формат пикселей (совместимость)
        "-pix_fmt", "yuv420p",
        # Компромисс скорости/качества
        "-preset", "medium",
        # Качество (18 = визуально без потерь)
        "-crf", "18",
        # Без аудио
        "-an",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=False,
            text=True
        )

        if result.returncode != 0:
            print(f"\tffmpeg stderr: {result.stderr[:200]}")

        return result.returncode == 0
    # pylint: disable=broad-exception-caught
    except Exception as e:
        print(f"\tОшибка запуска ffmpeg: {e}")
        return False
