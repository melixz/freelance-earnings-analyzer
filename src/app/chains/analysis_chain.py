from typing import Dict, Any, Optional
import json
import numpy as np
import pandas as pd

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..models.data_analyzer import FreelancerDataAnalyzer
from ..config.llm_config import get_llm
from ..prompts.earnings_prompts import CLASSIFICATION_PROMPT, INTERPRETATION_PROMPT
from ..prompts.predefined_questions import PREDEFINED_QUESTIONS
from ..memory.session_memory import SessionMemory


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, pd.Int64Dtype):
            return int(obj)
        if obj is pd.NA:
            return None
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


class FreelancerAnalysisChain:
    """Цепочка анализа вопросов о данных фрилансеров"""

    def __init__(
        self,
        data_analyzer: Optional[FreelancerDataAnalyzer] = None,
        memory: Optional[SessionMemory] = None,
    ):
        """
        Инициализация цепочки анализа

        Args:
            data_analyzer: Анализатор данных
            memory: Память для хранения истории
        """
        self.data_analyzer = data_analyzer or FreelancerDataAnalyzer()
        self.memory = memory or SessionMemory()
        self.llm = get_llm()
        self._setup_chain()

    def _setup_chain(self):
        """Настройка цепочки обработки"""

        self.classification_prompt = ChatPromptTemplate.from_template(
            CLASSIFICATION_PROMPT
        )

        self.interpretation_prompt = ChatPromptTemplate.from_template(
            INTERPRETATION_PROMPT
        )

        self.classification_chain = (
            self.classification_prompt | self.llm | StrOutputParser()
        )
        self.interpretation_chain = (
            self.interpretation_prompt | self.llm | StrOutputParser()
        )

    def _get_analysis_data(self, analysis_type: str, question: str) -> Dict[str, Any]:
        """
        Получает данные анализа на основе типа

        Args:
            analysis_type: Тип анализа
            question: Исходный вопрос

        Returns:
            Результаты анализа
        """
        try:
            if analysis_type == "payment_method":
                return self.data_analyzer.get_payment_method_analysis()
            elif analysis_type == "region":
                return self.data_analyzer.get_region_analysis()
            elif analysis_type == "expert":
                return self.data_analyzer.get_expert_analysis()
            elif analysis_type == "crypto_comparison":
                return self.data_analyzer.get_crypto_vs_other_analysis()
            elif analysis_type == "general_info":
                return self.data_analyzer.get_data_info()
            else:
                return {
                    "message": "Для данного типа вопроса требуется дополнительный анализ",
                    "general_stats": self.data_analyzer.get_data_info(),
                }
        except Exception as e:
            return {"error": f"Ошибка при анализе данных: {str(e)}"}

    def analyze_question(self, question: str) -> str:
        """
        Анализирует вопрос пользователя и возвращает ответ

        Args:
            question: Вопрос пользователя

        Returns:
            Ответ на основе анализа данных
        """
        try:
            analysis_type = self.classification_chain.invoke(
                {"question": question}
            ).strip()

            analysis_results = self._get_analysis_data(analysis_type, question)

            history = self.memory.get_history()
            context = (
                "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
                if history
                else ""
            )

            formatted_results = json.dumps(
                analysis_results, ensure_ascii=False, indent=2, cls=NpEncoder
            )

            prompt_vars = {
                "question": question,
                "analysis_results": formatted_results,
            }
            if context:
                prompt_vars["context"] = context

            response = self.interpretation_chain.invoke(prompt_vars)

            self.memory.add(question, response)

            return response

        except Exception as e:
            return f"Произошла ошибка при обработке вопроса: {str(e)}"

    def get_predefined_analyses(self) -> Dict[str, str]:
        """Возвращает предопределенные анализы для демонстрации"""
        return PREDEFINED_QUESTIONS
