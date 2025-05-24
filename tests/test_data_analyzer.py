import pytest
import pandas as pd
from src.app.models.data_analyzer import FreelancerDataAnalyzer
from app.utils.errors import DataFileNotFound

MOCK_DATA = pd.DataFrame(
    {
        "Payment_Method": ["Crypto", "Bank", "Crypto", "PayPal"],
        "Earnings_USD": [1000, 800, 1200, 700],
        "Hourly_Rate": [50, 40, 60, 35],
        "Client_Region": ["EU", "US", "EU", "Asia"],
        "Experience_Level": ["Expert", "Expert", "Intermediate", "Expert"],
        "Job_Completed": [120, 80, 50, 30],
        "Job_Success_Rate": [98, 95, 90, 85],
        "Client_Rating": [4.9, 4.8, 4.7, 4.6],
    }
)


class MockLoader:
    def __init__(self, *args, **kwargs):
        pass

    def load(self):
        return MOCK_DATA.copy()


def test_data_info():
    analyzer = FreelancerDataAnalyzer(loader_cls=MockLoader)
    info = analyzer.get_data_info()
    assert info["total_records"] == 4
    assert "Payment_Method" in info["columns"]


def test_payment_method_analysis():
    analyzer = FreelancerDataAnalyzer(loader_cls=MockLoader)
    stats = analyzer.get_payment_method_analysis()
    assert "Crypto" in stats
    assert stats["Crypto"]["avg_earnings"] == 1100


def test_region_analysis():
    analyzer = FreelancerDataAnalyzer(loader_cls=MockLoader)
    stats = analyzer.get_region_analysis()
    assert "EU" in stats
    assert stats["EU"]["total_freelancers"] == 2


def test_expert_analysis():
    analyzer = FreelancerDataAnalyzer(loader_cls=MockLoader)
    result = analyzer.get_expert_analysis()
    assert result["total_experts"] == 3
    assert result["experts_under_100_projects"] == 2


def test_crypto_vs_other_analysis():
    analyzer = FreelancerDataAnalyzer(loader_cls=MockLoader)
    result = analyzer.get_crypto_vs_other_analysis()
    assert "crypto_stats" in result
    assert result["crypto_stats"]["count"] == 2


def test_file_not_found():
    with pytest.raises(DataFileNotFound):
        FreelancerDataAnalyzer(data_path="not_exists.csv")
