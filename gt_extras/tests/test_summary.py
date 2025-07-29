from datetime import datetime, timezone

import numpy as np
import pandas as pd
import polars as pl
import pytest
from great_tables import GT

from gt_extras.summary import gt_plt_summary
from gt_extras.tests.conftest import assert_rendered_body


def test_gt_plt_summary_snap(snapshot):
    for DataFrame in [pd.DataFrame, pl.DataFrame]:
        df = DataFrame(
            {
                "numeric": [1.5, 2.2, 3.3, None, 5.1],
                "string": ["A", "B", "A", "C", None],
                "boolean": [True, False, True, False, False],
                "datetime": [
                    datetime(2024, 1, 1, tzinfo=timezone.utc),
                    datetime(2024, 1, 2, tzinfo=timezone.utc),
                    datetime(2024, 1, 3, tzinfo=timezone.utc),
                    None,
                    datetime(2024, 1, 5, tzinfo=timezone.utc),
                ],
            }
        )
        res = gt_plt_summary(df)
        assert_rendered_body(snapshot(name="pd_and_pl"), gt=res)


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_basic(DataFrame):
    df = DataFrame(
        {
            "numeric": [1, 2, 3, 4, 5],
            "string": ["A", "B", "C", "D", "E"],
            "boolean": [True, False, True, False, True],
        }
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert isinstance(result, GT)
    assert "Summary Table" in html
    assert "5 rows x 3 cols" in html
    assert html.count("<svg") == 6

    assert "numeric" in html
    assert "string" in html
    assert "boolean" in html

    assert "opacity: 0;" in html
    assert ":hover" in html
    assert "transition:" in html

    assert ">Type</th>" in html
    assert ">Column</th>" in html
    assert ">Plot Overview</th>" in html
    assert ">Missing</th>" in html
    assert ">Mean</th>" in html
    assert ">Median</th>" in html
    assert ">SD</th>" in html

    assert "[1 to 3]" in html
    assert "[3 to 5]" in html

    assert html.count(">1 row</text>") == 5
    assert html.count(">2 rows</text>") == 2
    assert html.count(">3 rows</text>") == 2

    assert html.count('fill="#4e79a7"') == 5
    assert html.count('fill="#a65773"') == 2
    assert html.count('fill="#f18e2c"') == 2

    assert html.count(">0.0%</td>") == 3
    assert html.count(">3.00</td>") == 2
    assert html.count(">1.58</td>") == 1
    assert html.count(">0.60</td>") == 1


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_custom_title(DataFrame):
    df = DataFrame({"col": [1, 2, 3]})

    result = gt_plt_summary(df, title="Custom Title")
    html = result.as_raw_html()

    assert (
        '<td colspan="7" class="gt_heading gt_title gt_font_normal">Custom Title</td>'
        in html
    )
    assert (
        '<td colspan="7" class="gt_heading gt_subtitle gt_font_normal gt_bottom_border">3 rows x 1 cols</td>'
        in html
    )


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_numeric_column(DataFrame):
    df = DataFrame({"numeric": [1.1, 2.2, 3.3, 4.4, 5.5]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "<title>signal</title>" in html
    assert '<td class="gt_row gt_right">3.30</td>' in html
    assert "<svg" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_string_column(DataFrame):
    df = DataFrame({"string": ["A", "B", "A", "C", "A"]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "<title>List</title>" in html
    assert "<svg" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_boolean_column(DataFrame):
    df = DataFrame({"boolean": [True, False, True, True, False]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "<title>Check</title>" in html
    assert "0.60" in html
    assert "<svg" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_datetime_column(DataFrame):
    df = DataFrame(
        {
            "datetime": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 1, 2, tzinfo=timezone.utc),
                datetime(2024, 1, 3, tzinfo=timezone.utc),
                datetime(2024, 1, 4, tzinfo=timezone.utc),
                datetime(2024, 1, 5, tzinfo=timezone.utc),
            ]
        }
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "<svg" in html
    assert "<title>Clock</title>" in html
    assert "2024-01-01</text>" in html
    assert "2024-01-05</text>" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_with_missing_values(DataFrame):
    df = DataFrame(
        {
            "numeric": [1, 2, None, 4, 5],
            "string": ["A", None, "C", "D", "E"],
            "boolean": [True, False, None, False, True],
        }
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert html.count("20.0%") == 3


def test_gt_plt_summary_with_nan_values():
    df = pd.DataFrame(
        {
            "numeric": [1.0, 2.0, np.nan, 4.0, 5.0],
            "mixed": [1, np.nan, None, 4, 5],
        }
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "20.0%" in html
    assert "40.0%" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_empty_dataframe(DataFrame):
    df = DataFrame()

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "0 rows x 0 cols" in html
    assert "<svg" not in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_empty_columns(DataFrame):
    df = DataFrame({"col1": [], "col2": []})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "0 rows x 2 cols" in html
    assert html.count("100.0%") == 2


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_single_row(DataFrame):
    df = DataFrame(
        {
            "numeric": [42],
            "string": ["test"],
            "boolean": [True],
        }
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "1 rows x 3 cols" in html
    assert html.count("42.00") == 2

    assert html.count(">1 row</text>") == 3
    assert html.count(">0 rows</text>") == 2

    assert '>"True"</text>' in html
    assert '>"False"</text>' not in html


def test_gt_plt_summary_all_missing_column():
    # Pandas version
    df_pd = pd.DataFrame(
        {
            "all_none": [None, None, None],
            "all_nan": [np.nan, np.nan, np.nan],
            "mixed": [np.nan, None, float("nan")],
        }
    )

    result = gt_plt_summary(df_pd)
    html = result.as_raw_html()

    assert "3 rows x 3 cols" in html
    assert html.count("100.0%") == 3

    # Polars version
    df_pl = pl.DataFrame(
        {
            "all_none": [None, None, None],
            "mixed": [None, None, None],
        }
    )

    result = gt_plt_summary(df_pl)
    html = result.as_raw_html()

    assert "3 rows x 2 cols" in html
    assert html.count("100.0%") == 2


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_single_value_numeric(DataFrame):
    df = DataFrame({"numeric": [5, 5, 5, 5, 5]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "[3.5 to 4.5]" in html
    assert "[4.5 to 5.5]" in html
    assert "[5.5 to 6.5]" in html

    assert html.count(">0 rows</text>") == 2
    assert html.count(">5 rows</text>") == 1


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_boolean_all_true(DataFrame):
    df = DataFrame({"boolean": [True, True, True]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "1.00" in html
    assert 'fill-opacity="1.0"' in html
    assert ">0.0%</td>" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_boolean_all_false(DataFrame):
    df = DataFrame({"boolean": [False, False, False]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "0.00" in html
    assert 'fill-opacity="0.2"' in html
    assert ">0.0%</td>" in html


def test_gt_plt_summary_boolean_all_empty():
    df = pl.DataFrame({"boolean": [None, None, None]}, schema={"boolean": bool})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "<div></div>" in html


def test_gt_plt_summary_datetime_single_date():
    df = pl.DataFrame(
        {"datetime": [datetime(2024, 1, 1, tzinfo=timezone.utc)]},
        schema={"datetime": datetime},
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "[2023-12-30 to 2023-12-31]" in html
    assert "[2023-12-31 to 2024-01-01]" in html
    assert "[2024-01-01 to 2024-01-02]" in html

    assert html.count(">0 rows</text>") == 2
    assert html.count(">1 row</text>") == 1


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_datetime_two_dates(DataFrame):
    df = DataFrame(
        {
            "datetime": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 1, 2, tzinfo=timezone.utc),
            ]
        }
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert html.count(">1 row</text>") == 2

    assert "[2024-01-01 to 2024-01-01]" in html
    assert "[2024-01-01 to 2024-01-02]" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_datetime_repeated_date(DataFrame):
    df = DataFrame(
        {
            "datetime": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 1, 1, tzinfo=timezone.utc),
            ]
        }
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "[2023-12-30 to 2023-12-31]" in html
    assert "[2023-12-31 to 2024-01-01]" in html
    assert "[2024-01-01 to 2024-01-02]" in html

    assert html.count(">0 rows</text>") == 2
    assert html.count(">3 rows</text>") == 1


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_numeric_two_values(DataFrame):
    df = DataFrame({"numeric": [1, 2]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert html.count(">1 row</text>") == 2

    assert "[1 to 1.5]" in html
    assert "[1.5 to 2]" in html


def test_gt_plt_summary_unknown_dtype():
    df = pd.DataFrame({"other": [object(), object(), object()]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert "<title>Question</title>" in html
    assert "other" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_negative_numbers(DataFrame):
    df = DataFrame({"negative": [-5, -3, -1, 1, 3]})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert html.count("−1.00") == 2
    assert html.count("3.16") == 1

    assert "[-5 to -1]" in html
    assert "[-1 to 3]" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_categorical_many_categories(DataFrame):
    categories = [f"Cat_{i}" for i in range(20)]
    df = DataFrame({"many_cats": categories})

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    assert html.count('x="21.8"') == 4
    assert html.count('x="155.8"') == 4

    for i in range(20):
        assert f'>"Cat_{i}"</text>' in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_plt_summary_column_order_preserved(DataFrame):
    df = DataFrame(
        {
            "z_column": [1, 2, 3],
            "a_column": ["A", "B", "C"],
            "m_column": [True, False, True],
        }
    )

    result = gt_plt_summary(df)
    html = result.as_raw_html()

    z_pos = html.find("z_column")
    a_pos = html.find("a_column")
    m_pos = html.find("m_column")

    assert z_pos < a_pos < m_pos


# TODO: time
# def test_gt_plt_summary_datetime_with_time():
#     df = pd.DataFrame(
#         {
#             "datetime_with_time": [
#                 datetime(2024, 1, 1, 10, 30, 0, tzinfo = timezone.utc),
#                 datetime(2024, 1, 1, 14, 45, 30, tzinfo = timezone.utc),
#                 datetime(2024, 1, 2, 9, 15, 45, tzinfo = timezone.utc),
#             ]
#         }
#     )

#     result = gt_plt_summary(df)
#     html = result.as_raw_html()

#     assert "2024-01-01" in html
