import pytest
from gt_extras.tests.conftest import assert_rendered_body

import pandas as pd
import numpy as np
from great_tables import GT
from gt_extras import gt_plt_bar, gt_plt_dot


def test_gt_plt_bar_snap(snapshot, mini_gt):
    res = gt_plt_bar(gt=mini_gt, columns="num")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_bar(mini_gt):
    html = gt_plt_bar(gt=mini_gt, columns=["num"]).as_raw_html()
    assert html.count("<svg") == 3


def test_gt_plt_bar_bar_height_too_high(mini_gt):
    html = gt_plt_bar(
        gt=mini_gt, columns=["num"], bar_height=1234, height=567
    ).as_raw_html()
    assert html.count('height="567"') == 6
    assert 'height="1234"' not in html


def test_gt_plt_bar_bar_height_too_low(mini_gt):
    html = gt_plt_bar(
        gt=mini_gt, columns=["num"], bar_height=-345, height=1234
    ).as_raw_html()
    assert html.count('height="1234"') == 3
    assert 'height="-345"' not in html


def test_gt_plt_bar_scale_percent(mini_gt):
    html = gt_plt_bar(gt=mini_gt, columns=["num"], scale_type="percent").as_raw_html()
    assert html.count("%</text>") == 3


def test_gt_plt_bar_scale_number(mini_gt):
    html = gt_plt_bar(gt=mini_gt, columns=["num"], scale_type="number").as_raw_html()
    assert ">33.33</text>" in html


def test_gt_plt_bar_scale_none(mini_gt):
    html = gt_plt_bar(gt=mini_gt, columns=["num"], scale_type=None).as_raw_html()
    assert "</text>" not in html


def test_gt_plt_bar_no_stroke_color(mini_gt):
    html = gt_plt_bar(gt=mini_gt, columns=["num"], stroke_color=None).as_raw_html()
    assert html.count("#FFFFFF00") == 3


def test_gt_plt_bar_type_error(mini_gt):
    with pytest.raises(TypeError, match="Invalid column type provided"):
        gt_plt_bar(gt=mini_gt, columns=["char"]).as_raw_html()


def test_gt_plt_dot_snap(snapshot, mini_gt):
    res = gt_plt_dot(gt=mini_gt, category_col="fctr", data_col="currency")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_dot_basic(mini_gt):
    html = gt_plt_dot(gt=mini_gt, category_col="char", data_col="num").as_raw_html()

    # Should contain dot styling
    assert "border-radius:50%; margin-top:4px; display:inline-block;" in html
    assert "height:0.7em; width:0.7em;" in html

    # Should contain bar styling
    assert "flex-grow:1; margin-left:0px;" in html
    assert "width:100.0%; height:4px; border-radius:2px;" in html


# TODO: remove when test_gt_plt_dot_with_palette_xfail() passes.
def test_gt_plt_dot_with_palette(mini_gt):
    html = gt_plt_dot(
        gt=mini_gt,
        category_col="char",
        data_col="num",
        palette=["#FF0000", "#00FF00", "#0000FF"],
    ).as_raw_html()

    assert "#ff0000" in html


@pytest.mark.xfail(reason="Palette bug, issue #717 in great_tables")
def test_gt_plt_dot_with_palette_xfail(mini_gt):
    html = gt_plt_dot(
        gt=mini_gt,
        category_col="char",
        data_col="num",
        palette=["#FF0000", "#00FF00", "#0000FF"],
    ).as_raw_html()

    assert "#ff0000" in html
    assert "#00ff00" in html
    assert "#0000ff" in html


def test_gt_plt_dot_with_domain_expanded(mini_gt):
    html = gt_plt_dot(
        gt=mini_gt, category_col="char", data_col="num", domain=[0, 100]
    ).as_raw_html()

    assert "width:0.1111%; height:4px; border-radius:2px;" in html
    assert "width:2.222%; height:4px; border-radius:2px;" in html
    assert "width:33.33%; height:4px; border-radius:2px;" in html


def test_gt_plt_dot_with_domain_restricted(mini_gt):
    html = gt_plt_dot(
        gt=mini_gt, category_col="char", data_col="num", domain=[1, 10]
    ).as_raw_html()

    assert "width:0%; height:4px; border-radius:2px;" in html
    assert "width:13.577777777777778%; height:4px; border-radius:2px;" in html
    assert "width:100%; height:4px; border-radius:2px;" in html


def test_gt_plt_dot_invalid_data_col(mini_gt):
    with pytest.raises(KeyError, match="Column 'invalid_col' not found"):
        gt_plt_dot(gt=mini_gt, category_col="char", data_col="invalid_col")


def test_gt_plt_dot_invalid_category_col(mini_gt):
    with pytest.raises(KeyError, match="Column 'invalid_col' not found"):
        gt_plt_dot(gt=mini_gt, category_col="invalid_col", data_col="num")


def test_gt_plt_dot_multiple_data_cols(mini_gt):
    with pytest.raises(
        ValueError, match="Expected a single column, but got multiple columns"
    ):
        gt_plt_dot(gt=mini_gt, category_col="char", data_col=["num", "char"])


def test_gt_plt_dot_multiple_category_cols(mini_gt):
    with pytest.raises(
        ValueError, match="Expected a single column, but got multiple columns"
    ):
        gt_plt_dot(gt=mini_gt, category_col=["char", "num"], data_col="num")


def test_gt_plt_dot_non_numeric_data_col(mini_gt):
    with pytest.raises(TypeError, match="Invalid column type provided"):
        gt_plt_dot(gt=mini_gt, category_col="char", data_col="char")


def test_gt_plt_dot_with_na_values():
    df = pd.DataFrame(
        {
            "category": ["A", "B", "C", "D"],
            "values": [10, np.nan, 20, None],
        }
    )
    gt = GT(df)

    result = gt_plt_dot(gt=gt, category_col="category", data_col="values")
    html = result.as_raw_html()

    assert isinstance(result, GT)
    assert "width:100.0%; height:4px; border-radius:2px;" in html
    assert html.count("width:0%; height:4px; border-radius:2px;") == 2


def test_gt_plt_dot_palette_string_valid(mini_gt):
    html = gt_plt_dot(
        gt=mini_gt, category_col="char", data_col="num", palette="viridis"
    ).as_raw_html()

    assert "background:#440154;" in html
