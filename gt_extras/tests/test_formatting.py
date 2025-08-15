import numpy as np
import pandas as pd
import polars as pl
import pytest
from great_tables import GT, google_font, loc, style

from gt_extras.formatting import (
    GTCombinedLayout,
    fmt_pct_extra,
    gt_duplicate_column,
    gt_two_column_layout,
)
from gt_extras.tests.conftest import assert_rendered_body


def test_fmt_pct_extra_snap(snapshot, mini_gt):
    res = fmt_pct_extra(mini_gt, columns="num", scale=1, decimals=0)
    assert_rendered_body(snapshot, gt=res)


def test_fmt_pct_extra_basic(mini_gt):
    html = fmt_pct_extra(mini_gt, columns="num", scale=1).as_raw_html()

    assert "<span style='color:grey;'><1%</span>" in html
    assert "2.2%" in html
    assert "33.3%" in html


def test_fmt_pct_extra_threshold_low(mini_gt):
    html = fmt_pct_extra(mini_gt, columns="num", scale=100, threshold=10).as_raw_html()

    assert "11.1%" in html
    assert "222.2%" in html
    assert "3333.0%" in html


def test_fmt_pct_extra_threshold_high(mini_gt):
    html = fmt_pct_extra(
        mini_gt, columns="num", scale=100, threshold=4000
    ).as_raw_html()

    assert html.count("<span style='color:grey;'><4000%</span>") == 3


def test_fmt_pct_extra_custom_color(mini_gt):
    html = fmt_pct_extra(
        mini_gt, columns="num", color="red", threshold=50
    ).as_raw_html()

    assert html.count("<span style='color:red;'><50%</span>") == 1


def test_fmt_pct_extra_decimals(mini_gt):
    html_0 = fmt_pct_extra(mini_gt, columns="num", decimals=0).as_raw_html()
    assert "11%" in html_0  # 0.1111 * 100 = 11.11% rounded
    assert "222%" in html_0


def test_fmt_pct_extra_negative_values():
    df = pd.DataFrame({"num": [-0.005, -0.25, 0.15]})
    gt_test = GT(df)

    html = fmt_pct_extra(gt=gt_test, columns="num", threshold=1.0).as_raw_html()

    assert "<span style='color:grey;'><1%</span>" in html
    assert "-25.0%" in html
    assert "15.0%" in html


def test_fmt_pct_extra_zero_values():
    df = pd.DataFrame({"num": [0.0, 0.005, 0.02]})
    gt_test = GT(df)
    html = fmt_pct_extra(gt=gt_test, columns="num").as_raw_html()

    assert html.count("<span style='color:grey;'><1%</span>") == 2
    assert "2.0%" in html


def test_fmt_pct_extra_edge_case_threshold():
    df = pd.DataFrame({"num": [0.01, 0.0099, 0.0101]})
    gt_test = GT(df)

    html = fmt_pct_extra(
        gt=gt_test, columns="num", scale=100, threshold=1.0, decimals=2
    ).as_raw_html()

    assert "1.00%" in html
    assert "<span style='color:grey;'><1%</span>" in html
    assert "1.01%" in html


def test_fmt_pct_extra_with_none_values():
    df = pd.DataFrame({"num": [0.005, None, 0.25, np.nan]})
    gt_test = GT(df)

    result = fmt_pct_extra(gt=gt_test, columns="num")
    html = result.as_raw_html()

    assert isinstance(result, GT)
    assert "25%" in html


def test_gt_duplicate_column_snap(snapshot, mini_gt):
    res = gt_duplicate_column(mini_gt, column="num")
    assert_rendered_body(snapshot, gt=res)


def test_gt_duplicate_column_basic(mini_gt):
    res = gt_duplicate_column(mini_gt, column="num", append_text="_copy")
    html = res.as_raw_html()

    assert "num_copy" in res._tbl_data.columns
    assert "num_copy" in html
    assert all(res._tbl_data["num"] == res._tbl_data["num_copy"])


def test_gt_duplicate_column_custom_name(mini_gt):
    res = gt_duplicate_column(mini_gt, column="num", dupe_name="duplicated_num")
    html = res.as_raw_html()

    assert "duplicated_num" in res._tbl_data.columns
    assert "duplicated_num" in html
    assert all(res._tbl_data["num"] == res._tbl_data["duplicated_num"])


def test_gt_duplicate_column_position(mini_gt):
    res = gt_duplicate_column(mini_gt, column="num", after="char")
    html = res.as_raw_html()

    assert "num_dupe" in res._tbl_data.columns
    assert "num_dupe" in html

    columns = list(res._boxhead)
    assert columns[2].column_label == "num_dupe"


def test_gt_duplicate_column_polars():
    df = pl.DataFrame({"num": [1, 2, 3], "char": ["a", "b", "c"]})
    gt_test = GT(df)

    res = gt_duplicate_column(gt_test, column="num", append_text="_copy")
    html = res.as_raw_html()

    assert "num_copy" in res._tbl_data.columns
    assert "num_copy" in html

    original_values = res._tbl_data.get_column("num").to_list()  # type: ignore
    duplicated_values = res._tbl_data.get_column("num_copy").to_list()  # type: ignore
    assert original_values == duplicated_values


def test_gt_duplicate_column_invalid_name(mini_gt):
    with pytest.raises(
        ValueError, match="cannot be the same as the original column name"
    ):
        gt_duplicate_column(mini_gt, column="num", dupe_name="num")


@pytest.fixture
def two_dfs():
    df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    df2 = pd.DataFrame({"A": [5, 6], "B": [7, 8]})
    return df1, df2


def test_gt_two_column_layout_snapshot(snapshot, two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1, id="id1").tab_header(title="Header 1", subtitle="Subtitle 1")
    gt2 = GT(df2, id="id2").tab_header(title="Header 2", subtitle="Subtitle 2")

    result = gt_two_column_layout(gt1, gt2, table_header_from=1)
    assert snapshot == str(result)


def test_gt_two_column_layout_basic(two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1).tab_header(title="Left Table", subtitle="Left Subtitle")
    gt2 = GT(df2).tab_header(title="Right Table", subtitle="Right Subtitle")

    result = gt_two_column_layout(gt1, gt2)
    html = str(result)

    assert "Left Table" in html
    assert "Right Table" in html
    assert '<div id="mycombinedtable"' in html
    assert "<table" in html


def test_gt_two_column_layout_with_header_from_1(two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1).tab_header(title="Header 1", subtitle="Subtitle 1")
    gt2 = GT(df2).tab_header(title="Header 2", subtitle="Subtitle 2")

    result = gt_two_column_layout(gt1, gt2, table_header_from=1)
    html = str(result)

    assert "Header 1" in html
    assert "Subtitle 1" in html
    assert "Header 2" not in html
    assert "Subtitle 2" not in html


def test_gt_two_column_layout_with_header_from_2(two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1).tab_header(title="Header 1", subtitle="Subtitle 1")
    gt2 = GT(df2).tab_header(title="Header 2", subtitle="Subtitle 2")

    result = gt_two_column_layout(gt1, gt2, table_header_from=2)
    html = str(result)

    assert "Header 2" in html
    assert "Subtitle 2" in html
    assert "Header 1" not in html
    assert "Subtitle 1" not in html


def test_gt_two_column_layout_no_headers(two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1)
    gt2 = GT(df2)

    result = gt_two_column_layout(gt1, gt2, table_header_from=1)
    html = str(result)

    assert "Header" not in html
    assert "Subtitle" not in html


def test_gt_two_column_layout_with_styles(two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1)
    gt2 = GT(df2)

    gt1 = (
        GT(df1)
        .tab_header(title="Table 1", subtitle="1st Table")
        .tab_style(
            style=style.text(font=google_font("Chivo"), weight="bold"),
            locations=loc.title(),
        )
        .tab_style(
            style=style.text(font=google_font("Chivo")),
            locations=loc.subtitle(),
        )
    )

    gt2 = GT(df2).tab_header(title="Table 2", subtitle="2nd Table")

    # Create combined layout using table 1's header
    result = gt_two_column_layout(gt1, gt2, table_header_from=1)

    # Get the HTML output
    html = str(result)

    assert 'style="width:100%; font-family: Chivo;"' in html
    assert 'style="width:100%; font-family: Chivo;font-weight: bold;"' in html


def test_gt_combined_layout_repr_html():
    html = "<div>hello world</div>"
    layout = GTCombinedLayout(html)
    assert layout._repr_html_() == html


def test_gt_two_column_layout_save_target(two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1)
    gt2 = GT(df2)
    with pytest.raises(
        NotImplementedError,
        match="At the moment, only notebook and browser display options are available.",
    ):
        gt_two_column_layout(gt1, gt2, target="save")  # type: ignore


def test_gt_two_column_layout_invalid_target(two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1)
    gt2 = GT(df2)
    with pytest.raises(Exception, match="Unknown target display"):
        gt_two_column_layout(gt1, gt2, target="invalid")  # type: ignore


def test_gt_combined_layout_save_incomplete(two_dfs):
    df1, df2 = two_dfs
    gt1 = GT(df1)
    gt2 = GT(df2)
    gt_combined = gt_two_column_layout(gt1, gt2)

    with pytest.raises(NotImplementedError):
        gt_combined.save()


@pytest.mark.xfail(reason="Notebook target test not implemented yet")
def test_gt_two_column_layout_notebook_target():
    assert False


@pytest.mark.xfail(reason="Browser target test not implemented yet")
def test_gt_two_column_layout_browser_target():
    assert False
