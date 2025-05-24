import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown

from ..chains.analysis_chain import FreelancerAnalysisChain
from ..models.data_analyzer import FreelancerDataAnalyzer
from ..config.llm_config import LLMConfig
from ..utils.errors import DataFileNotFound, LLMConfigError

app = typer.Typer(
    help=(
        "Анализатор данных о доходах фрилансеров.\n"
        "\n"
        "Примеры использования:\n"
        "  run analyze -q 'Какой регион приносит наибольший доход?'\n"
        "  run analyze -i\n"
        "  run info\n"
        "  run validate\n"
        "  run demo\n"
        "\n"
        "Используйте --help для получения справки по каждой команде."
    )
)
console = Console()


@app.command(
    help=(
        "Анализ данных фрилансеров.\n"
        "\n"
        "Используйте --question/-q для анализа одного вопроса или --interactive/-i для интерактивного режима.\n"
        "\n"
        "Примеры:\n"
        "  run analyze -q 'Какие способы оплаты наиболее выгодны для фрилансеров?'\n"
        "  run analyze -i"
    )
)
def analyze(
    question: Optional[str] = typer.Option(
        None,
        "--question",
        "-q",
        help="Вопрос для анализа (например: 'Какие способы оплаты наиболее выгодны для фрилансеров?')",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Интерактивный режим (пошаговый диалог с системой)",
    ),
):
    """Анализ данных фрилансеров по вашему вопросу или в интерактивном режиме."""

    try:
        console.print("Инициализация анализатора...", style="yellow")
        analyzer = FreelancerDataAnalyzer()
        chain = FreelancerAnalysisChain(analyzer)
        console.print("Анализатор готов к работе!", style="green")

        if interactive or not question:
            run_interactive_mode(chain)
        else:
            run_single_question(chain, question)

    except FileNotFoundError as e:
        console.print(f"Ошибка: {e}", style="red")
        console.print(
            "Убедитесь, что файл данных находится в правильной директории.",
            style="yellow",
        )
    except Exception as e:
        console.print(f"Произошла ошибка: {e}", style="red")


def run_single_question(chain: FreelancerAnalysisChain, question: str):
    """Обработка одного вопроса пользователя"""

    console.print(Panel(f"Вопрос: {question}", title="Анализ", style="blue"))

    with console.status("[yellow]Обработка вопроса..."):
        response = chain.analyze_question(question)

    console.print(Panel(Markdown(response), title="Результат анализа", style="green"))


@app.command(help="Проверить корректность конфигурации LLM и наличие файла с данными.")
def validate():
    """Проверка конфигурации и наличия данных для анализа."""
    try:
        config = LLMConfig()
        config.validate_config()
        analyzer = FreelancerDataAnalyzer()
        analyzer.get_data_info()
        console.print("[green]Конфигурация и данные в порядке![/green]")
    except (DataFileNotFound, LLMConfigError) as e:
        console.print(f"[red]Ошибка:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Непредвиденная ошибка:[/red] {e}")


def run_interactive_mode(chain: FreelancerAnalysisChain):
    """Интерактивный режим работы с анализатором"""
    console.print(
        Panel(
            "Добро пожаловать в интерактивный анализатор данных фрилансеров!\n"
            "Вы можете задавать вопросы о данных или использовать предустановленные запросы.\n"
            "Для выхода введите 'quit' или 'exit'. Для справки — '/help', для информации о данных — '/info'.",
            title="Интерактивный режим",
            style="blue",
        )
    )
    show_predefined_analyses(chain)
    while True:
        console.print()
        question = Prompt.ask("Ваш вопрос", default="")
        if question.lower() in ["quit", "exit", "выход"]:
            console.print("До свидания!", style="green")
            break
        if question.strip() == "/help":
            console.print(
                "[yellow]Доступные команды: /help, /info, quit, exit, ключ предустановленного запроса[/yellow]"
            )
            continue
        if question.strip() == "/info":
            analyzer = chain.data_analyzer
            data_info = analyzer.get_data_info()
            console.print(
                Panel(
                    f"Всего записей: {data_info.get('total_records', '?')}\nКолонок: {len(data_info.get('columns', []))}",
                    title="Информация о данных",
                    style="green",
                )
            )
            continue
        if not question.strip():
            continue
        predefined = chain.get_predefined_analyses()
        if question in predefined:
            question = predefined[question]
            console.print(f"Выбран предустановленный запрос: {question}", style="cyan")
        console.print(Panel(f"Вопрос: {question}", title="Анализ", style="blue"))
        with console.status("[yellow]Обработка вопроса..."):
            response = chain.analyze_question(question)
        console.print(
            Panel(Markdown(response), title="Результат анализа", style="green")
        )


def show_predefined_analyses(chain: FreelancerAnalysisChain):
    """Показывает предустановленные запросы для быстрого анализа"""

    predefined = chain.get_predefined_analyses()

    table = Table(title="Предустановленные запросы")
    table.add_column("Ключ", style="cyan", no_wrap=True)
    table.add_column("Описание", style="magenta")

    for key, description in predefined.items():
        table.add_row(key, description)

    console.print(table)
    console.print(
        "Вы можете использовать ключ из первого столбца для быстрого запуска анализа",
        style="yellow",
    )


@app.command(help="Показать подробную информацию о структуре и содержимом данных.")
def info():
    """Показать информацию о данных: количество записей, колонки, типы, пропуски."""

    try:
        console.print("Загрузка данных...", style="yellow")
        analyzer = FreelancerDataAnalyzer()
        data_info = analyzer.get_data_info()

        console.print(
            Panel(
                f"Общая статистика:\n"
                f"• Всего записей: {data_info['total_records']}\n"
                f"• Колонок в данных: {len(data_info['columns'])}",
                title="Информация о данных",
                style="green",
            )
        )

        table = Table(title="Структура данных")
        table.add_column("Колонка", style="cyan")
        table.add_column("Тип данных", style="yellow")
        table.add_column("Пропущенные значения", style="red")

        for col in data_info["columns"]:
            dtype = str(data_info["data_types"][col])
            missing = data_info["missing_values"][col]
            table.add_row(col, dtype, str(missing))

        console.print(table)

    except Exception as e:
        console.print(f"Ошибка при загрузке данных: {e}", style="red")


@app.command(help="Демонстрация возможностей анализатора на примерах типовых вопросов.")
def demo():
    """Демонстрация работы анализатора на заранее подготовленных вопросах."""

    try:
        console.print("Запуск демонстрации...", style="blue")

        analyzer = FreelancerDataAnalyzer()
        chain = FreelancerAnalysisChain(analyzer)

        demo_questions = [
            "Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте?",
            "Какой процент экспертов выполнил менее 100 проектов?",
            "Какой регион приносит наибольший доход фрилансерам?",
        ]

        for i, question in enumerate(demo_questions, 1):
            console.print(f"\nДемо {i}/3: {question}", style="cyan")

            with console.status("[yellow]Анализ..."):
                response = chain.analyze_question(question)

            console.print(
                Panel(Markdown(response), title=f"Результат {i}", style="green")
            )

            if i < len(demo_questions):
                input("Нажмите Enter для продолжения...")

        console.print("\nДемонстрация завершена!", style="green")

    except Exception as e:
        console.print(f"Ошибка при демонстрации: {e}", style="red")


if __name__ == "__main__":
    app()
