"""
TODO: докстринг класса
"""

from .render import RenderCommand

command_types = [RenderCommand]

mapping = {
    RenderCommand.get_name(): RenderCommand.execute
}
