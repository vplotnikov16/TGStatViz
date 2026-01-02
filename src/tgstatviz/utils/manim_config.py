"""
Конфигурация Manim для поддержки кириллицы и настройка качества
"""
import platform
from manim import config as manim_config, TexTemplate, Tex, MathTex


def configure_latex_for_cyrillic() -> None:
    """
    Настройка LaTeX в Manim для поддержки кириллицы

    Для поддержки Unicode/кириллицы переключаемся на XeLaTeX и расширяем babel
    до варианта с russian
    """
    try:
        tex_template = TexTemplate()
        tex_template.tex_compiler = "xelatex"
        tex_template.output_format = ".pdf"

        # Подменяем babel в уже существующем preamble (избавляемся от option clash)
        if hasattr(tex_template, "preamble") and isinstance(tex_template.preamble, str):
            tex_template.preamble = tex_template.preamble.replace(
                r"\usepackage[english]{babel}",
                r"\usepackage[english,russian]{babel}"
            )

        # Добавляем поддержку системных шрифтов (XeLaTeX) и шрифт с кириллицей
        tex_template.add_to_preamble(r"\usepackage{fontspec}")

        # Выбираем шрифт в зависимости от платформы
        font = _get_system_font()
        tex_template.add_to_preamble(rf"\setmainfont{{{font}}}")

        # Глобально для Tex/MathTex
        Tex.set_default(tex_template=tex_template)
        MathTex.set_default(tex_template=tex_template)

        # И для всего проекта
        manim_config.tex_template = tex_template
        manim_config.tex_compiler = "xelatex"

        print(f"LaTeX настроен: XeLaTeX с шрифтом {font}")

    # pylint: disable=broad-exception-caught
    except Exception as e:
        print(f"Предупреждение: не удалось настроить LaTeX для кириллицы: {e}")


def _get_system_font() -> str:
    """
    Получить подходящий системный шрифт с поддержкой кириллицы
    """
    system = platform.system()

    if system == "Windows":
        return "Arial"
    if system == "Darwin":
        return "Helvetica Neue"
    return "DejaVu Sans"


def configure_quality(quality: str) -> None:
    """
    Настроить качество рендеринга Manim
    """
    quality_map = {
        "low": "low_quality",
        "medium": "medium_quality",
        "high": "high_quality",
    }

    manim_quality = quality_map.get(quality, "low_quality")
    manim_config.quality = manim_quality

    print(f"Качество Manim: {manim_quality}")


def initialize_manim(quality: str = "low", enable_cyrillic: bool = True) -> None:
    """
    Полная инициализация конфигурации Manim
    """
    configure_quality(quality)

    if enable_cyrillic:
        configure_latex_for_cyrillic()
