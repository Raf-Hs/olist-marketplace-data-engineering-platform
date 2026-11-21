import pytest

from src.config.paths import silver_dir
from src.quality.checks import run_basic_checks


@pytest.mark.requires_data
def test_basic_quality_checks_pass():
    if not (silver_dir() / "customers" / "customers.parquet").exists():
        pytest.skip("silver data not available")
    results = run_basic_checks()
    failed = [r for r in results if not r.passed]
    assert not failed, [r.name for r in failed]
