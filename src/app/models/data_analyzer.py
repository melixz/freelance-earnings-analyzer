import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
from app.document_loaders.csv_loader import FreelancerCSVLoader


class FreelancerDataAnalyzer:
    """Анализатор данных о фрилансерах"""

    def __init__(
        self,
        data_path: str = "data/freelancer_earnings_bd.csv",
        loader_cls=FreelancerCSVLoader,
    ):
        """
        Инициализация анализатора

        Args:
            data_path: Путь к CSV файлу с данными
            loader_cls: Класс загрузчика данных (для тестирования)
        """
        self.data_path = Path(data_path)
        self.df: Optional[pd.DataFrame] = None
        self.loader_cls = loader_cls
        self._load_data()

    def _load_data(self) -> None:
        """Загружает данные из CSV файла через загрузчик"""
        loader = self.loader_cls(str(self.data_path))
        self.df = loader.load()
        print(f"Загружено {len(self.df)} записей о фрилансерах")

    def get_data_info(self) -> Dict[str, Any]:
        """Возвращает общую информацию о данных"""
        if self.df is None:
            return {}

        return {
            "total_records": len(self.df),
            "columns": list(self.df.columns),
            "data_types": dict(self.df.dtypes),
            "missing_values": dict(self.df.isnull().sum()),
            "sample_data": self.df.head().to_dict("records"),
        }

    def get_payment_method_analysis(self) -> Dict[str, Any]:
        """Анализ доходов по способам оплаты"""
        if self.df is None:
            return {}

        payment_stats = (
            self.df.groupby("Payment_Method")
            .agg(
                {
                    "Earnings_USD": ["mean", "median", "count", "sum"],
                    "Hourly_Rate": ["mean", "median"],
                }
            )
            .round(2)
        )

        results = {}
        for payment_method in payment_stats.index:
            results[payment_method] = {
                "avg_earnings": payment_stats.loc[
                    payment_method, ("Earnings_USD", "mean")
                ],
                "median_earnings": payment_stats.loc[
                    payment_method, ("Earnings_USD", "median")
                ],
                "total_freelancers": payment_stats.loc[
                    payment_method, ("Earnings_USD", "count")
                ],
                "total_earnings": payment_stats.loc[
                    payment_method, ("Earnings_USD", "sum")
                ],
                "avg_hourly_rate": payment_stats.loc[
                    payment_method, ("Hourly_Rate", "mean")
                ],
                "median_hourly_rate": payment_stats.loc[
                    payment_method, ("Hourly_Rate", "median")
                ],
            }

        return results

    def get_region_analysis(self) -> Dict[str, Any]:
        """Анализ доходов по регионам"""
        if self.df is None:
            return {}

        region_stats = (
            self.df.groupby("Client_Region")
            .agg(
                {
                    "Earnings_USD": ["mean", "median", "count", "sum"],
                    "Hourly_Rate": ["mean", "median"],
                    "Job_Success_Rate": "mean",
                    "Client_Rating": "mean",
                }
            )
            .round(2)
        )

        results = {}
        for region in region_stats.index:
            results[region] = {
                "avg_earnings": region_stats.loc[region, ("Earnings_USD", "mean")],
                "median_earnings": region_stats.loc[region, ("Earnings_USD", "median")],
                "total_freelancers": region_stats.loc[
                    region, ("Earnings_USD", "count")
                ],
                "total_earnings": region_stats.loc[region, ("Earnings_USD", "sum")],
                "avg_hourly_rate": region_stats.loc[region, ("Hourly_Rate", "mean")],
                "avg_success_rate": region_stats.loc[
                    region, ("Job_Success_Rate", "mean")
                ],
                "avg_client_rating": region_stats.loc[
                    region, ("Client_Rating", "mean")
                ],
            }

        return results

    def get_expert_analysis(self) -> Dict[str, Any]:
        """Анализ экспертов с менее чем 100 проектами"""
        if self.df is None:
            return {}

        experts = self.df[self.df["Experience_Level"] == "Expert"]
        experts_under_100 = experts[experts["Job_Completed"] < 100]

        return {
            "total_experts": len(experts),
            "experts_under_100_projects": len(experts_under_100),
            "percentage": round((len(experts_under_100) / len(experts)) * 100, 2),
            "avg_earnings_under_100": experts_under_100["Earnings_USD"].mean(),
            "avg_earnings_all_experts": experts["Earnings_USD"].mean(),
        }

    def get_crypto_vs_other_analysis(self) -> Dict[str, Any]:
        """Сравнение доходов криптоплатежей с другими способами"""
        if self.df is None:
            return {}

        crypto_users = self.df[self.df["Payment_Method"] == "Crypto"]
        other_users = self.df[self.df["Payment_Method"] != "Crypto"]

        return {
            "crypto_stats": {
                "count": len(crypto_users),
                "avg_earnings": crypto_users["Earnings_USD"].mean(),
                "median_earnings": crypto_users["Earnings_USD"].median(),
                "avg_hourly_rate": crypto_users["Hourly_Rate"].mean(),
            },
            "other_stats": {
                "count": len(other_users),
                "avg_earnings": other_users["Earnings_USD"].mean(),
                "median_earnings": other_users["Earnings_USD"].median(),
                "avg_hourly_rate": other_users["Hourly_Rate"].mean(),
            },
            "difference": {
                "earnings_difference": crypto_users["Earnings_USD"].mean()
                - other_users["Earnings_USD"].mean(),
                "hourly_rate_difference": crypto_users["Hourly_Rate"].mean()
                - other_users["Hourly_Rate"].mean(),
                "percentage_difference": round(
                    (
                        (
                            crypto_users["Earnings_USD"].mean()
                            - other_users["Earnings_USD"].mean()
                        )
                        / other_users["Earnings_USD"].mean()
                    )
                    * 100,
                    2,
                ),
            },
        }

    def execute_custom_query(self, query: str) -> Any:
        """Выполняет пользовательский запрос к данным"""
        if self.df is None:
            return None

        try:
            allowed_methods = [
                "groupby",
                "mean",
                "median",
                "sum",
                "count",
                "max",
                "min",
                "head",
                "tail",
                "describe",
                "value_counts",
                "unique",
                "sort_values",
                "filter",
                "query",
            ]

            for method in allowed_methods:
                if method in query:
                    break
            else:
                return "Запрос содержит недопустимые операции"

            return eval(f"self.df.{query}")

        except Exception as e:
            return f"Ошибка выполнения запроса: {str(e)}"
