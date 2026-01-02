"""
CLI-команды приложения
"""

from .render import RenderCommand
from .metrics import MetricsCommand
from .renderers import RenderersCommand

command_types = [
    RenderCommand,
    MetricsCommand,
    RenderersCommand,
]

mapping = {
    command.get_name(): command.execute for command in command_types
}
