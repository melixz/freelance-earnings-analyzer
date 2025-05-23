import os

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from ..utils.errors import LLMConfigError

load_dotenv()


class LLMConfig:
    """Конфигурация для языковых моделей (LLM)"""

    def __init__(self):
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY")
        self.model_name: str = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
        self.temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))
        self.max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))

    def validate_config(self) -> bool:
        """Проверяет корректность конфигурации"""
        if not self.openai_api_key:
            raise LLMConfigError(
                "OPENAI_API_KEY не найден в переменных окружения. "
                "Пожалуйста, создайте .env файл и добавьте ваш ключ API"
            )
        return True

    def create_llm(self) -> ChatOpenAI:
        """Создает экземпляр ChatOpenAI"""
        self.validate_config()

        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.openai_api_key,
        )


def get_llm() -> ChatOpenAI:
    """Получает настроенный экземпляр LLM"""
    config = LLMConfig()
    return config.create_llm()
