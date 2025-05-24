from rich.console import Console
from app.cli.cli import app
from app.utils.errors import DataFileNotFound, LLMConfigError


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
