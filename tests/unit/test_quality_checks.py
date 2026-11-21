import pandas as pd

from src.quality.checks import (
    check_not_null,
    check_range,
    check_referential_integrity,
    check_unique,
)


def test_check_not_null_pass():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    r = check_not_null(df, ["a", "b"])
    assert r.passed


def test_check_not_null_fail():
    df = pd.DataFrame({"a": [1, None]})
    r = check_not_null(df, ["a"])
    assert not r.passed
    assert r.metrics["null_counts"]["a"] == 1


def test_check_unique_pass():
    df = pd.DataFrame({"a": [1, 2]})
    r = check_unique(df, ["a"])
    assert r.passed


def test_check_unique_fail():
    df = pd.DataFrame({"a": [1, 1]})
    r = check_unique(df, ["a"])
    assert not r.passed
    assert r.metrics["duplicate_count"] == 1


def test_check_range():
    df = pd.DataFrame({"price": [1.0, 2.0, -1.0]})
    r = check_range(df, "price", min_val=0)
    assert not r.passed
    assert r.metrics["out_of_range"] == 1


def test_check_referential_integrity():
    child = pd.DataFrame({"fk": [1, 2, 3]})
    parent = pd.DataFrame({"pk": [1, 2]})
    r = check_referential_integrity(child, parent, "fk", "pk")
    assert not r.passed
    assert r.metrics["orphan_count"] == 1
    assert 3 in r.metrics["sample_orphans"]
