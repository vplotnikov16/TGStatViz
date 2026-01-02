"""
TODO: докстринг модуля
"""
from typing import Any

from pydantic import BaseModel, Field


class Transition(BaseModel):
    """
    TODO: докстринг класса
    """
    name: str = "fade"
    duration: float = 0.5


class Slide(BaseModel):
    """
    TODO: докстринг класса
    """
    metric: str = Field(..., description="ID метрики")
    renderer: str = Field(..., description="ID рендерера")
    duration: float = Field(5.0, ge=0.1)
    params: dict[str, Any] = Field(default_factory=dict)


class Defaults(BaseModel):
    """
    TODO: докстринг класса
    """
    style: str = "dark"
    transition: Transition = Field(default_factory=Transition)


class ProjectConfig(BaseModel):
    """
    TODO: докстринг класса
    """
    title: str
    description: str = ""
    defaults: Defaults = Field(default_factory=Defaults)
    slides: list[Slide]
