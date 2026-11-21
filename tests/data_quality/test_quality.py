from src.quality.checks import run_basic_checks


def test_basic_quality_checks_pass():
    results = run_basic_checks()
    failed = [r for r in results if not r.passed]
    assert not failed, [r.name for r in failed]
