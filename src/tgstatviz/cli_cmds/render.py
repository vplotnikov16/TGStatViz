"""
Команда рендеринга storyboard
"""
from argparse import ArgumentParser, Namespace
from pathlib import Path

from tgstatviz.cli_cmds.base import BaseCommand
from tgstatviz.services.render_service import RenderService


class RenderCommand(BaseCommand):
    """
    Команда рендеринга из storyboard
    """

    @staticmethod
    def get_name() -> str:
        return 'render'

    @staticmethod
    def get_help() -> str:
        return 'Отрендерить storyboard в видео'

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        parser.add_argument(
            'export_dir',
            help='Путь к каталогу экспорта, в котором лежит result.json',
        )
        parser.add_argument(
            'storyboard',
            help='Путь к YAML-конфигу storyboard',
        )
        parser.add_argument(
            '-o', '--output',
            help='Путь к результирующему видеофайлу'
        )
        parser.add_argument(
            '-q', '--quality',
            choices=['low', 'medium', 'high'],
            default='low',
            help='Качество видео (low, medium, high)',
        )

    @classmethod
    def execute(cls, args: Namespace):
        """
        Выполнение команды рендеринга
        """
        service = RenderService()

        export_dir = Path(args.export_dir)
        if not export_dir.exists():
            raise FileNotFoundError(f"Каталог экспорта не найден: {export_dir}")

        storyboard_path = Path(args.storyboard)
        if not storyboard_path.exists():
            raise FileNotFoundError(f"Файл раскадровки не найден: {storyboard_path}")

        service.render_video(
            export_dir=export_dir,
            storyboard_path=storyboard_path,
            output_path=Path(args.output) if args.output else None,
            quality=args.quality,
        )
