import pytest
from gt_extras.tests.conftest import assert_rendered_body

import pandas as pd
import numpy as np
from great_tables import GT
from gt_extras import gt_plt_bar, gt_plt_dot, gt_plt_conf_int


def test_gt_plt_bar_snap(snapshot, mini_gt):
    res = gt_plt_bar(gt=mini_gt, columns="num")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_bar(mini_gt):
    html = gt_plt_bar(gt=mini_gt, columns=["num"]).as_raw_html()
    assert html.count("<svg") == 3


def test_gt_plt_bar_bar_height_too_high(mini_gt):
    with pytest.warns(
        UserWarning,
        match="Bar_height must be less than or equal to the plot height. Adjusting bar_height to 567.",
    ):
        html = gt_plt_bar(
            gt=mini_gt, columns=["num"], bar_height=1234, height=567
        ).as_raw_html()

    assert html.count('height="567px"') == 6
    assert 'height="1234px"' not in html


def test_gt_plt_bar_bar_height_too_low(mini_gt):
    with pytest.warns(
        UserWarning,
        match="Bar_height cannot be negative. Adjusting bar_height to 0.",
    ):
        html = gt_plt_bar(
            gt=mini_gt, columns=["num"], bar_height=-345, height=1234
        ).as_raw_html()

    assert html.count('height="1234px"') == 3
    assert 'height="-345px"' not in html


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


def test_gt_plt_bar_scale_type_invalid_string(mini_gt):
    with pytest.raises(
        ValueError, match="Scale_type must be one of `None`, 'percent', or 'number'"
    ):
        gt_plt_bar(mini_gt, scale_type="invalid")


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
    with pytest.warns(
        UserWarning,
        match="Value 33.33 in column 'num' is greater than the domain maximum 10. Setting to 10.",
    ):
        html = gt_plt_dot(
            gt=mini_gt, category_col="char", data_col="num", domain=[0, 10]
        ).as_raw_html()

    assert "width:1.111%; height:4px; border-radius:2px;" in html
    assert "width:22.220000000000002%; height:4px; border-radius:2px;" in html
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


def test_gt_plt_dot_with_na_in_category():
    df = pd.DataFrame(
        {
            "category": [np.nan, "B", None, None],
            "values": [5, 10, 10, 5],
        }
    )
    gt = GT(df)

    result = gt_plt_dot(gt=gt, category_col="category", data_col="values")
    html = result.as_raw_html()

    assert isinstance(result, GT)
    assert html.count("width:100.0%; height:4px; border-radius:2px;") == 1
    assert "width:50.0%; height:4px; border-radius:2px;" not in html


def test_gt_plt_dot_palette_string_valid(mini_gt):
    html = gt_plt_dot(
        gt=mini_gt, category_col="char", data_col="num", palette="viridis"
    ).as_raw_html()

    assert "background:#440154;" in html


def test_gt_plt_conf_int_snap(snapshot):
    df = pd.DataFrame(
        {
            "group": ["A", "B", "C"],
            "mean": [5.2, 7.8, 3.4],
            "ci_lower": [4.1, 6.9, 2.8],
            "ci_upper": [6.3, 8.7, 4.0],
        }
    )
    gt_test = GT(df)
    res = gt_plt_conf_int(
        gt=gt_test, column="mean", ci_columns=["ci_lower", "ci_upper"]
    )

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_conf_int_basic():
    df = pd.DataFrame(
        {
            "group": ["A", "B", "C"],
            "mean": [1, 2, 3],
            "ci_lower": [0, 1, 2],
            "ci_upper": [4, 6, 5],
        }
    )
    gt_test = GT(df)
    html = gt_plt_conf_int(
        gt=gt_test, column="mean", ci_columns=["ci_lower", "ci_upper"]
    ).as_raw_html()

    assert "position:absolute;left:6.666666666666669px;bottom:15px;color:black;" in html
    assert "top:29.0px; width:55.55555555555556px;" in html
    assert "height:4px; background:royalblue; border-radius:2px;" in html
    assert html.count("position:absolute;") == 12


def test_gt_plt_conf_int_computed_ci():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "data": [[1, 2, 2, 5, 6] * 5, [1, 5, 5, 9] * 10],
        }
    )
    gt_test = GT(df)
    html = gt_plt_conf_int(gt=gt_test, column="data").as_raw_html()

    assert ">2.4</div>" in html
    assert ">4</div>" in html
    assert ">4.1</div>" in html
    assert ">5.9</div>" in html


@pytest.mark.parametrize(
    "text_size, expected_font_size",
    [
        ("none", "font-size:0px;"),
        ("small", "font-size:6px;"),
        ("default", "font-size:10px;"),
        ("large", "font-size:14px;"),
        ("largest", "font-size:18px;"),
    ],
)
def test_gt_plt_conf_int_text_size(text_size, expected_font_size):
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "mean": [5.2, 7.8],
            "ci_lower": [4.1, 6.9],
            "ci_upper": [6.3, 8.7],
        }
    )
    gt_test = GT(df)
    html = gt_plt_conf_int(
        gt=gt_test,
        column="mean",
        ci_columns=["ci_lower", "ci_upper"],
        text_size=text_size,
    ).as_raw_html()

    assert html.count(expected_font_size) == 4


@pytest.mark.parametrize(
    "width, expected_width_style, expected_label_c1, expected_label_c2",
    [
        (50, "width:50px;", 1, 7),
        (70, "width:70px;", 1.2, 7),
        (90, "width:90px;", 1.23, 6.99),
        (110, "width:110px;", 1.235, 6.988),
        (150, "width:150px;", 1.2346, 6.9877),
    ],
)
def test_gt_plt_conf_int_width_parametrized(
    width, expected_width_style, expected_label_c1, expected_label_c2
):
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "mean": [5, 7],
            "ci_lower": [1.23456, 5.12345],
            "ci_upper": [6.98765, 9.87654],
        }
    )
    gt_test = GT(df)
    html = gt_plt_conf_int(
        gt=gt_test,
        column="mean",
        ci_columns=["ci_lower", "ci_upper"],
        width=width,
    ).as_raw_html()

    assert html.count(expected_width_style) == 2
    assert f">{expected_label_c1}</div>" in html
    assert f">{expected_label_c2}</div>" in html


def test_gt_plt_conf_int_custom_colors():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "mean": [5.2, 7.8],
            "ci_lower": [4.1, 6.9],
            "ci_upper": [6.3, 8.7],
        }
    )
    gt_test = GT(df)
    html = gt_plt_conf_int(
        gt=gt_test,
        column="mean",
        ci_columns=["ci_lower", "ci_upper"],
        line_color="blue",
        dot_color="green",
        text_color="red",
    ).as_raw_html()

    assert html.count("background:blue;") == 2
    assert html.count("background:green;") == 2
    assert html.count("color:red;") == 4


def test_gt_plt_conf_int_invalid_column():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "mean": [5.2, 7.8],
            "ci_lower": [4.1, 6.9],
            "ci_upper": [6.3, 8.7],
        }
    )
    gt_test = GT(df)

    with pytest.raises(ValueError, match="Expected 1 col in the column parameter"):
        gt_plt_conf_int(gt=gt_test, column=["mean", "group"])


def test_gt_plt_conf_int_invalid_ci_columns():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "mean": [5.2, 7.8],
            "ci_lower": [4.1, 6.9],
            "ci_upper": [6.3, 8.7],
        }
    )
    gt_test = GT(df)

    with pytest.raises(ValueError, match="Expected 2 ci_columns"):
        gt_plt_conf_int(gt=gt_test, column="mean", ci_columns=["ci_lower"])


def test_gt_plt_conf_int_invalid_text_size():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "mean": [5.2, 7.8],
            "ci_lower": [4.1, 6.9],
            "ci_upper": [6.3, 8.7],
        }
    )
    gt_test = GT(df)

    with pytest.raises(ValueError, match="Text_size expected to be one of"):
        gt_plt_conf_int(
            gt=gt_test,
            column="mean",
            ci_columns=["ci_lower", "ci_upper"],
            text_size="invalid",
        )


def test_gt_plt_conf_int_with_none_values():
    df = pd.DataFrame(
        {
            "group": ["A", "B", "C"],
            "mean": [5.2, None, 3.4],
            "ci_lower": [4.1, None, 2.8],
            "ci_upper": [6.3, np.nan, 4.0],
        }
    )
    gt_test = GT(df)
    result = gt_plt_conf_int(
        gt=gt_test, column="mean", ci_columns=["ci_lower", "ci_upper"]
    )

    assert isinstance(result, GT)
    html = result.as_raw_html()
    assert "<div></div>" in html


def test_gt_plt_conf_int_computed_invalid_data():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "data": [5.2, 7.8],  # Not lists
        }
    )
    gt_test = GT(df)

    with pytest.raises(
        ValueError, match="Expected entries in data to be lists or None"
    ):
        gt_plt_conf_int(gt=gt_test, column="data")


def test_gt_plt_conf_int_empty_data():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "data": [[], [1, 2, 3, 4, 5, 6]],
        }
    )
    gt_test = GT(df)
    html = gt_plt_conf_int(gt=gt_test, column="data").as_raw_html()

    assert html.count("border-radius:50%;") == 1


def test_gt_plt_conf_int_precomputed_invalid_data():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "mean": [["not", "numeric"], [7.8]],  # Not numeric
            "ci_lower": [4.1, 6.9],
            "ci_upper": [6.3, 8.7],
        }
    )
    gt_test = GT(df)

    with pytest.raises(
        ValueError, match="Expected all entries in mean to be numeric or None"
    ):
        gt_plt_conf_int(gt=gt_test, column="mean", ci_columns=["ci_lower", "ci_upper"])
