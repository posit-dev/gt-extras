from great_tables import GT
import numpy as np
import pandas as pd
from gt_extras import gt_highlight_cols, gt_hulk_col_numeric, gt_color_box
from conftest import assert_rendered_body
import pytest


def test_gt_highlight_cols(snapshot, mini_gt):
    res = gt_highlight_cols(mini_gt)
    assert_rendered_body(snapshot, gt=res)


def test_gt_highlight_cols_font(mini_gt):
    res = gt_highlight_cols(mini_gt, font_weight="bolder").as_raw_html()
    assert "bolder" in res


def test_gt_highlight_cols_alpha(mini_gt):
    res = gt_highlight_cols(mini_gt, alpha=0.2, columns="num")
    html = res.as_raw_html()
    assert "#80bcd833" in html


def test_gt_highlight_cols_font_weight_invalid_string(mini_gt):
    with pytest.raises(
        ValueError,
        match="Font_weight must be one of 'normal', 'bold', 'bolder', or 'lighter', or an integer",
    ):
        gt_highlight_cols(mini_gt, font_weight="invalid")


@pytest.mark.parametrize("invalid_weight", [(1.5, 5), [], {}, None])
def test_gt_highlight_cols_font_weight_invalid_type(mini_gt, invalid_weight):
    with pytest.raises(TypeError, match="Font_weight must be an int, float, or str"):
        gt_highlight_cols(mini_gt, font_weight=invalid_weight)


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
