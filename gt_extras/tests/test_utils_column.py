import pytest
import pandas as pd
import numpy as np
import warnings
from great_tables import GT
from gt_extras._utils_column import (
    _validate_and_get_single_column,
    _scale_numeric_column,
)


@pytest.mark.parametrize(
    "col_arg,expected_name,expected_vals",
    [
        ("col1", "col1", [1, 2, 3]),
        (["col1"], "col1", [1, 2, 3]),
    ],
)
def test_validate_column_basic(col_arg, expected_name, expected_vals):
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    gt = GT(df)

    col_name, col_vals = _validate_and_get_single_column(gt, col_arg)

    assert col_name == expected_name
    assert col_vals == expected_vals


def test_validate_column_with_mixed_data_types():
    df = pd.DataFrame({"mixed": [1, "text", 3.5, None]})
    gt = GT(df)

    col_name, col_vals = _validate_and_get_single_column(gt, "mixed")

    assert col_name == "mixed"
    assert col_vals == [1, "text", 3.5, None]


def test_validate_column_not_found():
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    gt = GT(df)

    with pytest.raises(KeyError, match="Column 'nonexistent' not found"):
        _validate_and_get_single_column(gt, "nonexistent")


def test_validate_multiple_columns_error():
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    gt = GT(df)

    with pytest.raises(
        ValueError, match="Expected a single column, but got multiple columns"
    ):
        _validate_and_get_single_column(gt, ["col1", "col2"])


def test_validate_column_empty_list():
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    gt = GT(df)

    with pytest.raises(KeyError, match="Column '\\[\\]' not found"):
        _validate_and_get_single_column(gt, [])


def test_scaling_basic():
    col_vals = [0, 1, 2, 3, 4, 5]
    df = pd.DataFrame({"col": col_vals})

    result = _scale_numeric_column(df, "col", col_vals)

    assert all(isinstance(x, (int, float)) for x in result)
    assert result == [0, 0.2, 0.4, 0.6, 0.8, 1.0]


def test_scaling_with_custom_domain():
    col_vals = [0, 1, 2, 3, 4]
    df = pd.DataFrame({"col": col_vals})
    domain = [0, 10]

    result = _scale_numeric_column(df, "col", col_vals, domain)

    assert all(isinstance(x, (int, float)) for x in result)
    assert result == [0, 0.1, 0.2, 0.3, 0.4]


def test_scaling_with_na_values():
    col_vals = [1, np.nan, 3, None, 5]
    df = pd.DataFrame({"col": col_vals})

    result = _scale_numeric_column(df, "col", col_vals)

    assert len(result) == 5
    assert result[1] == 0
    assert result[3] == 0

    assert result[0] > 0 and result[0] <= 1
    assert result[2] > 0 and result[2] <= 1
    assert result[4] > 0 and result[4] <= 1


def test_scaling_all_na_values():
    col_vals = [np.nan, None, np.nan]
    df = pd.DataFrame({"col": col_vals})

    with pytest.raises(TypeError, match="Invalid column type provided \\(col\\)"):
        _scale_numeric_column(df, "col", col_vals)


def test_scaling_non_numeric_column():
    col_vals = ["a", "b", "c"]
    df = pd.DataFrame({"col": col_vals})

    with pytest.raises(TypeError, match="Invalid column type provided \\(col\\)"):
        _scale_numeric_column(df, "col", col_vals)


def test_scaling_mixed_numeric_non_numeric():
    col_vals = [1, "text", 3]
    df = pd.DataFrame({"col": col_vals})

    with pytest.raises(TypeError, match="Invalid column type provided \\(col\\)"):
        _scale_numeric_column(df, "col", col_vals)


def test_scaling_values_outside_domain_below():
    col_vals = [-5, 1, 2, 3]
    df = pd.DataFrame({"col": col_vals})
    domain = [0, 10]

    with pytest.warns(
        UserWarning,
        match="less than the domain minimum",
    ):
        result = _scale_numeric_column(df, "col", col_vals, domain)

    assert result[0] == 0


def test_scaling_values_outside_domain_above():
    col_vals = [1, 2, 3, 15]
    df = pd.DataFrame({"col": col_vals})
    domain = [0, 3]

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = _scale_numeric_column(df, "col", col_vals, domain)

        assert len(w) >= 1
        assert "greater than the domain maximum" in str(w[0].message)

    assert result[2] == 1
    assert result[3] == 1


def test_scaling_zero_values():
    col_vals = [0, 1, 2, 3]
    df = pd.DataFrame({"col": col_vals})

    result = _scale_numeric_column(df, "col", col_vals)

    assert result == [0, 1 / 3, 2 / 3, 1.0]


def test_scaling_negative_values():
    col_vals = [-1, 0, 1, 2]
    df = pd.DataFrame({"col": col_vals})

    with pytest.warns(
        UserWarning,
        match="Value -1 in column 'col' is less than the domain minimum 0. Setting to 0.",
    ):
        result = _scale_numeric_column(df, "col", col_vals)

    assert result == [0, 0, 0.5, 1]


def test_scaling_default_domain_min_zero_true():
    col_vals = [2, 4, 6, 8]
    df = pd.DataFrame({"col": col_vals})

    result = _scale_numeric_column(df, "col", col_vals, default_domain_min_zero=True)

    expected = [0.25, 0.5, 0.75, 1.0]
    assert result == expected


def test_scaling_default_domain_min_zero_false():
    col_vals = [2, 4, 6, 8]
    df = pd.DataFrame({"col": col_vals})

    result = _scale_numeric_column(df, "col", col_vals, default_domain_min_zero=False)

    expected = [0.0, 2 / 6, 4 / 6, 6 / 6]
    assert result == expected
