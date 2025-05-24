class DataFileNotFound(FileNotFoundError):
    """Ошибка: файл данных не найден"""

    pass


class LLMConfigError(ValueError):
    """Ошибка: некорректная конфигурация LLM или отсутствует API-ключ"""

    pass
