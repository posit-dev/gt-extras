import numpy as np
import pandas as pd
import polars as pl
import pytest
from conftest import assert_rendered_body
from great_tables import GT

from gt_extras import (
    gt_color_box,
    gt_data_color_by_group,
    gt_highlight_cols,
    gt_highlight_rows,
    gt_hulk_col_numeric,
)


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_data_color_by_group_no_groups(DataFrame):
    df = DataFrame({"B": [1, 2, 3, 4, 5, 6]})
    html = gt_data_color_by_group(GT(df)).as_raw_html()
    assert 'style="color:' not in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_data_color_by_group_single_group(DataFrame):
    df = DataFrame({"A": [1, 1, 1, 1, 1, 1], "B": [1, 2, 3, 4, 5, 6]})
    html = gt_data_color_by_group(GT(df, groupname_col="A")).as_raw_html()

    assert "color: #FFFFFF; background-color: #000000;" in html
    assert "color: #000000; background-color: #ad8560;" in html
    assert "color: #000000; background-color: #2fa2c8;" in html


@pytest.mark.parametrize("DataFrame", [pd.DataFrame, pl.DataFrame])
def test_gt_data_color_by_group_multiple_singletons(DataFrame):
    df = DataFrame({"A": [1, 2, 3, 4, 5, 6], "B": [1, 2, 3, 4, 5, 6]})
    html = gt_data_color_by_group(GT(df, groupname_col="A")).as_raw_html()
    assert html.count("color: #FFFFFF; background-color: #000000;") == 6


def test_gt_data_color_by_group_multiple_groups_snap(snapshot):
    for DataFrame in [pd.DataFrame, pl.DataFrame]:
        df = DataFrame({"A": [1, 2, 2, 3, 3, 3], "B": [1, 2, 3, 4, 5, 6]})
        gt = gt_data_color_by_group(GT(df, groupname_col="A"))
        assert_rendered_body(snapshot(name="pd_and_pl"), gt)


def test_gt_highlight_cols_snap(snapshot, mini_gt):
    res = gt_highlight_cols(mini_gt)
    assert_rendered_body(snapshot, gt=res)


def test_gt_highlight_cols_all_params(mini_gt):
    html = gt_highlight_cols(
        mini_gt,
        columns=[1, 2],
        font_weight="bolder",
        font_color="#cccccc",
        fill="#aaaaaa",
        include_column_labels=True,
    ).as_raw_html()

    assert "bolder" in html
    assert html.count("background-color: #aaaaaa;") == 8
    assert html.count("#cccccc") == 8


def test_gt_highlight_cols_alpha(mini_gt):
    html = gt_highlight_cols(mini_gt, alpha=0.2, columns="num").as_raw_html()
    assert "#80bcd833" in html


def test_gt_highlight_cols_font_weight_invalid_string(mini_gt):
    with pytest.raises(
        ValueError,
        match="Font_weight must be one of 'normal', 'bold', 'bolder', or 'lighter', or an integer",
    ):
        gt_highlight_cols(mini_gt, font_weight="invalid")  # type: ignore


@pytest.mark.parametrize("invalid_weight", [(1.5, 5), [], {}, None])
def test_gt_highlight_cols_font_weight_invalid_type(mini_gt, invalid_weight):
    with pytest.raises(TypeError, match="Font_weight must be an int, float, or str"):
        gt_highlight_cols(mini_gt, font_weight=invalid_weight)


def test_gt_highlight_rows_snap(snapshot, mini_gt):
    res = gt_highlight_rows(mini_gt, rows=[0, 1])
    assert_rendered_body(snapshot, gt=res)


def test_gt_highlight_rows_all_params():
    df = pd.DataFrame({"rowname": ["A", "B", "C"], "num": [1, 2, 3]})
    gt_with_rowname = GT(df, rowname_col="rowname")
    html = gt_highlight_rows(
        gt_with_rowname,
        rows=[1, 2],
        font_weight="bolder",
        font_color="#cccccc",
        fill="#aaaaaa",
        include_row_labels=True,
    ).as_raw_html()

    assert "bolder" in html
    assert html.count("background-color: #aaaaaa;") == 4
    assert html.count("#cccccc") == 4


def test_gt_highlight_rows_alpha(mini_gt):
    html = gt_highlight_rows(mini_gt, rows=[0], alpha=0.3).as_raw_html()
    assert "#80bcd84C" in html


def test_gt_highlight_rows_font_weight_invalid_string(mini_gt):
    with pytest.raises(
        ValueError,
        match="Font_weight must be one of 'normal', 'bold', 'bolder', or 'lighter', or an integer",
    ):
        gt_highlight_rows(mini_gt, rows=[0], font_weight="invalid")  # type: ignore


@pytest.mark.parametrize("invalid_weight", [(1.5, 5), [], {}, None])
def test_gt_highlight_rows_font_weight_invalid_type(mini_gt, invalid_weight):
    with pytest.raises(TypeError, match="Font_weight must be an int, float, or str"):
        gt_highlight_rows(mini_gt, rows=[0], font_weight=invalid_weight)


def test_gt_hulk_col_numeric_snap(snapshot, mini_gt):
    res = gt_hulk_col_numeric(mini_gt)
    assert_rendered_body(snapshot, gt=res)


def test_gt_hulk_col_numeric_specific_cols(mini_gt):
    res = gt_hulk_col_numeric(mini_gt, columns=["num"])
    html = res.as_raw_html()
    assert 'style="color: #FFFFFF; background-color: #621b6f;"' in html
    assert 'style="color: #FFFFFF; background-color: #00441b;"' in html


def test_gt_hulk_col_numeric_palette(mini_gt):
    res = gt_hulk_col_numeric(mini_gt, columns=["num"], palette="viridis")
    html = res.as_raw_html()
    assert 'style="color: #FFFFFF; background-color: #440154;"' in html
    assert 'style="color: #000000; background-color: #fde725;"' in html


@pytest.mark.xfail(
    reason="Will pass when great-tables updates the alpha bug in data_color()"
)
def test_gt_hulk_col_numeric_alpha(mini_gt):
    res = gt_hulk_col_numeric(mini_gt, columns=["num"], palette="viridis", alpha=0.2)
    html = res.as_raw_html()
    assert 'background-color: #44015433;"' in html
    assert 'background-color: #fde72533;"' in html


def test_gt_color_box_snap(snapshot, mini_gt):
    res = gt_color_box(mini_gt, columns="num")
    assert_rendered_body(snapshot, gt=res)


def test_gt_color_box_basic(mini_gt):
    res = gt_color_box(mini_gt, columns="num")
    html = res.as_raw_html()

    assert html.count("display:flex; border-radius:5px;") == 3
    assert html.count("align-items:center; padding:0px 7.0px;") == 3
    assert html.count("height:13.0px; width:13.0px;") == 3
    assert html.count("min-height:20px; min-width:70px;") == 3


def test_gt_color_box_custom_dimensions(mini_gt):
    res = gt_color_box(mini_gt, columns="num", min_width=100, min_height=30)
    html = res.as_raw_html()

    assert html.count("min-height:30px; min-width:100px;") == 3
    assert "height:19.5px;" in html  # 30 * 0.65


def test_gt_color_box_custom_palette(mini_gt):
    res = gt_color_box(mini_gt, columns="num", palette=["red", "blue"])
    html = res.as_raw_html()

    assert "background-color:#0000ff;" in html
    assert "background-color:#ff0000;" in html


def test_gt_color_box_string_palette(mini_gt):
    res = gt_color_box(mini_gt, columns="num", palette="PRGn")
    html = res.as_raw_html()

    assert "background-color:#00441b;" in html
    assert "background-color:#621b6f33;" in html


def test_gt_color_box_font_weight(mini_gt):
    res = gt_color_box(mini_gt, columns="num", font_weight="bold")
    html = res.as_raw_html()

    assert "font-weight:bold;" in html


def test_gt_color_box_alpha(mini_gt):
    res = gt_color_box(mini_gt, columns="num", alpha=0.5)
    html = res.as_raw_html()

    assert "7F" in html


def test_gt_color_box_with_na():
    df = pd.DataFrame({"name": ["A", "B", "C"], "values": [1.0, np.nan, None]})
    gt = GT(df)

    res = gt_color_box(gt, columns="values")
    html = res.as_raw_html()

    assert html.count("<div></div>") == 2


def test_gt_color_box_custom_domain(mini_gt):
    with pytest.warns(UserWarning) as record:
        res = gt_color_box(mini_gt, columns="num", domain=[1, 3])

    messages = [str(w.message) for w in record]
    assert any(
        "Value 0.1111 in column 'num' is less than the domain minimum 1" in m
        for m in messages
    )
    assert any(
        "Value 33.33 in column 'num' is greater than the domain maximum 3" in m
        for m in messages
    )

    html = res.as_raw_html()
    assert "background-color:#000000;" in html
    assert "background-color:#56a6da;" in html
    assert "background-color:#9e9e9e;" in html
