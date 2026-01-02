"""
TODO: докстринг модуля
"""
from typing import Type

from tgstatviz.viz.manim_renderers.base import Renderer

_RENDERERS: dict[str, Type[Renderer]] = {}


def register_renderer(renderer_cls: Type[Renderer]) -> Type[Renderer]:
    """
    Декоратор для автоматической регистрации рендерера
    """
    instance = renderer_cls()
    _RENDERERS[instance.id] = renderer_cls
    return renderer_cls


def get_renderer(renderer_id: str) -> Type[Renderer]:
    """
    Геттер класса рендерера по ID
    """
    if renderer_id not in _RENDERERS:
        raise ValueError(f"Рендерер '{renderer_id}' не зарегистрирован")
    return _RENDERERS[renderer_id]


def list_renderers() -> list[str]:
    """
    Список всех зарегистрированных рендереров
    """
    return list(_RENDERERS.keys())
