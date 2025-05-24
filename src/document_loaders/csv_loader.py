import pandas as pd
from pathlib import Path
from src.utils.errors import DataFileNotFound


class FreelancerCSVLoader:
    """Загрузчик данных о фрилансерах из CSV"""

    def __init__(self, path: str):
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            raise DataFileNotFound(f"Файл не найден: {self.path}")
        return pd.read_csv(self.path)
