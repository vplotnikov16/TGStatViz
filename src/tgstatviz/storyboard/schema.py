"""
Pydantic-схемы для конфигурации storyboard
"""
from typing import Any

from pydantic import BaseModel, Field


class Transition(BaseModel):
    """
    Параметры перехода между слайдами
    """
    name: str = "fade"
    duration: float = 0.5


class Slide(BaseModel):
    """
    Описание одного слайда раскадровки
    """
    metric: str = Field(..., description="ID метрики")
    renderer: str = Field(..., description="ID рендерера")
    duration: float = Field(5.0, ge=0.0, description="Длительность анимации слайда в секундах")
    wait_time: float = Field(1.0, ge=0.0, description="Время финальной паузы в секундах (не входит в duration)")
    params: dict[str, Any] = Field(default_factory=dict, description="Параметры метрики и рендерера")


class Defaults(BaseModel):
    """
    Значения по умолчанию для раскадровки
    """
    style: str = "dark"
    transition: Transition = Field(default_factory=Transition)


class ProjectConfig(BaseModel):
    """
    Корневая конфигурация проекта раскадровки
    """
    title: str = Field(..., description="Название проекта")
    description: str = Field("", description="Описание раскадровки")
    defaults: Defaults = Field(default_factory=Defaults)
    slides: list[Slide] = Field(..., description="Список слайдов")


# Для обратной совместимости со старым форматом (без project-обёртки)
class LegacyProjectConfig(BaseModel):
    """
    Старый формат конфигурации (без project-обёртки)
    """
    title: str = Field("Untitled", description="Название проекта")
    description: str = Field("", description="Описание раскадровки")
    defaults: Defaults = Field(default_factory=Defaults)
    slides: list[Slide] = Field(..., description="Список слайдов")
