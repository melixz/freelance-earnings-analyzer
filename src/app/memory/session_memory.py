from typing import List, Dict


class SessionMemory:
    """Память для хранения истории вопросов и ответов пользователя"""

    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add(self, question: str, answer: str) -> None:
        self.history.append({"question": question, "answer": answer})

    def get_history(self, n: int = 5) -> List[Dict[str, str]]:
        """Возвращает последние n пар вопрос-ответ"""
        return self.history[-n:]
