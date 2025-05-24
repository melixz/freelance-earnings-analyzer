"""
Главный файл анализатора данных фрилансеров
"""

from rich.console import Console
from src.cli.cli import app
from src.utils.errors import DataFileNotFound, LLMConfigError


def main():
    console = Console()
    try:
        app()
    except DataFileNotFound as e:
        console.print(f"[red]Ошибка данных:[/red] {e}")
    except LLMConfigError as e:
        console.print(f"[red]Ошибка конфигурации LLM:[/red] {e}")
    except Exception as e:
        console.print(f"[bold red]Непредвиденная ошибка:[/bold red] {e}", style="red")


if __name__ == "__main__":
    main()
