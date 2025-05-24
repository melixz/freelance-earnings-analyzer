import pytest
import pandas as pd
import tempfile
from pathlib import Path
from src.app.document_loaders.csv_loader import FreelancerCSVLoader
from app.utils.errors import DataFileNotFound


def test_csv_loader_success():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        loader = FreelancerCSVLoader(tmp.name)
        loaded = loader.load()
        assert loaded.shape == (2, 2)
    Path(tmp.name).unlink()


def test_csv_loader_file_not_found():
    loader = FreelancerCSVLoader("not_exists.csv")
    with pytest.raises(DataFileNotFound):
        loader.load()
