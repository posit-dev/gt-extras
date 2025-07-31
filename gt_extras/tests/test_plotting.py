import numpy as np
import pandas as pd
import pytest
from great_tables import GT, loc, style

from gt_extras import (
    gt_plt_bar,
    gt_plt_bar_pct,
    gt_plt_bar_stack,
    gt_plt_bullet,
    gt_plt_conf_int,
    gt_plt_dot,
    gt_plt_dumbbell,
    gt_plt_winloss,
)
from gt_extras.tests.conftest import assert_rendered_body


def test_gt_plt_bar_snap(snapshot, mini_gt):
    res = gt_plt_bar(gt=mini_gt, columns="num")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_bar(mini_gt):
    result = gt_plt_bar(gt=mini_gt, columns=["num"])
    html = result.as_raw_html()
    assert html.count("<svg") == 3


def test_gt_plt_bar_bar_height_too_high(mini_gt):
    with pytest.warns(
        UserWarning,
        match="Bar_height must be less than or equal to the plot height. Adjusting bar_height to 567.",
    ):
        result = gt_plt_bar(gt=mini_gt, columns=["num"], bar_height=1234, height=567)
        html = result.as_raw_html()

    assert html.count('height="567"') == 3
    assert 'height="1234"' not in html


def test_gt_plt_bar_bar_height_too_low(mini_gt):
    with pytest.warns(
        UserWarning,
        match="Bar_height cannot be negative. Adjusting bar_height to 0.",
    ):
        result = gt_plt_bar(gt=mini_gt, columns=["num"], bar_height=-345, height=1234)
        html = result.as_raw_html()

    assert html.count('height="1234"') == 3
    assert 'height="-345"' not in html


def test_gt_plt_bar_show_labels_true(mini_gt):
    result = gt_plt_bar(gt=mini_gt, columns=["num"], show_labels=True)
    html = result.as_raw_html()
    assert ">33.33</text>" in html


def test_gt_plt_bar_keep_columns(mini_gt):
    gt = mini_gt.tab_style(
        style=style.fill("lightblue"),
        locations=loc.body(),
    )
    result = gt_plt_bar(gt=gt, columns=["num"], keep_columns=True)
    html = result.as_raw_html()

    assert ">num plot</th>" in html
    assert ">num</th>" in html
    assert ">2.222</td>" in html
    assert html.count("<svg") == 3


def test_gt_plt_bar_show_labels_false(mini_gt):
    result = gt_plt_bar(gt=mini_gt, columns=["num"], show_labels=False)
    html = result.as_raw_html()
    assert "</text>" not in html


def test_gt_plt_bar_no_stroke_color(mini_gt):
    result = gt_plt_bar(gt=mini_gt, columns=["num"], stroke_color=None)
    html = result.as_raw_html()
    assert html.count('line stroke="transparent"') == 3


def test_gt_plt_bar_type_error(mini_gt):
    with pytest.raises(TypeError, match="Invalid column type provided"):
        gt_plt_bar(gt=mini_gt, columns=["char"])


def test_gt_plt_dot_snap(snapshot, mini_gt):
    res = gt_plt_dot(gt=mini_gt, category_col="fctr", data_col="currency")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_dot_basic(mini_gt):
    result = gt_plt_dot(gt=mini_gt, category_col="char", data_col="num")
    html = result.as_raw_html()

    assert html.count("<svg") == 3
    assert html.count('<circle cx="5.818181818181818" cy="15.0"') == 3
    assert html.count('<text dominant-baseline="central"') == 3
    assert html.count('text-anchor="start" font-size="16"') == 3
    assert html.count('<rect x="0"') == 3


def test_gt_plt_dot_with_palette(mini_gt):
    result = gt_plt_dot(
        gt=mini_gt,
        category_col="char",
        data_col="num",
        palette=["#FF0000", "#00FF00", "#0000FF"],
    )
    html = result.as_raw_html()

    assert "#ff0000" in html
    assert "#00ff00" in html
    assert "#0000ff" in html


def test_gt_plt_dot_with_domain_expanded(mini_gt):
    result = gt_plt_dot(
        gt=mini_gt, category_col="char", data_col="num", domain=[0, 100]
    )
    html = result.as_raw_html()

    assert '<rect x="0" y="24.6" width="39.995999999999995"' in html
    assert '<rect x="0" y="24.6" width="2.6664"' in html
    assert '<rect x="0" y="24.6" width="0.13332"' in html


def test_gt_plt_dot_with_domain_restricted(mini_gt):
    with pytest.warns(
        UserWarning,
        match="Value 33.33 in column 'num' is greater than the domain maximum 10. Setting to 10.",
    ):
        result = gt_plt_dot(
            gt=mini_gt, category_col="char", data_col="num", domain=[0, 10]
        )
        html = result.as_raw_html()

    assert '<rect x="0" y="24.6" width="1.3332"' in html
    assert '<rect x="0" y="24.6" width="26.664"' in html
    assert '<rect x="0" y="24.6" width="120"' in html


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
    assert '<rect x="0" y="24.6" width="60.0"' in html
    assert '<rect x="0" y="24.6" width="120.0"' in html
    assert html.count('<rect x="0" y="24.6" width="0"') == 2


def test_gt_plt_dot_with_na_in_category():
    df = pd.DataFrame(
        {
            "category": [np.nan, "B", None, None],
            "values": [5, 10, 10, 5],
        }
    )
    gt = GT(df)

    with pytest.warns(UserWarning, match="A color value is None and has been coerced"):
        result = gt_plt_dot(gt=gt, category_col="category", data_col="values")

    html = result.as_raw_html()

    assert isinstance(result, GT)
    assert html.count('<rect x="0" y="24.6" width="120.0"') == 1
    assert '<rect x="0" y="24.6" width="60.0"' not in html


def test_gt_plt_dot_palette_string_valid(mini_gt):
    result = gt_plt_dot(
        gt=mini_gt, category_col="char", data_col="num", palette="viridis"
    )
    html = result.as_raw_html()

    assert 'fill="#440154"' in html
    assert 'fill="#22908c"' in html
    assert 'fill="#fde725"' in html


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
            "ci_lower": [0, 2, 2],
            "ci_upper": [4, 6, 5],
        }
    )
    gt_test = GT(df)
    result = gt_plt_conf_int(
        gt=gt_test, column="mean", ci_columns=["ci_lower", "ci_upper"]
    )
    html = result.as_raw_html()

    assert html.count("<svg") == 3
    assert html.count('height="3.0" rx="2" fill="royalblue"') == 3
    assert html.count('<circle stroke="red" stroke-width="1.5"') == 3
    assert html.count('cy="20.0" r="3.0" fill="red"') == 3

    assert html.count('<text dominant-baseline="central"') == 6
    assert html.count('text-anchor="start" font-size="10" fill="black"') == 3
    assert html.count('text-anchor="end" font-size="10" fill="black"') == 3

    assert 'cx="22.222222222222225"' in html
    assert 'cx="36.111111111111114"' in html
    assert 'cx="50.000000000000014"' in html

    assert '<rect x="8.333333333333336"' in html
    assert '<rect x="36.111111111111114"' in html
    assert 'width="55.55555555555556"' in html
    assert 'width="41.66666666666667"' in html

    assert 'x="8.333333333333336" y="12.5">0</text>' in html
    assert 'x="63.88888888888889" y="12.5">4</text>' in html
    assert 'x="36.111111111111114" y="12.5">2</text>' in html
    assert 'x="91.66666666666667" y="12.5">6</text>' in html


def test_gt_plt_conf_int_computed_ci():
    df = pd.DataFrame(
        {
            "group": ["A", "B"],
            "data": [[1, 2, 2, 5, 6] * 5, [1, 5, 5, 9] * 10],
        }
    )
    gt_test = GT(df)
    result = gt_plt_conf_int(gt=gt_test, column="data")
    html = result.as_raw_html()

    assert ">2.4</text>" in html
    assert ">4</text>" in html
    assert ">4.1</text>" in html
    assert ">5.9</text>" in html


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
    result = gt_plt_conf_int(
        gt=gt_test,
        column="mean",
        ci_columns=["ci_lower", "ci_upper"],
        line_color="blue",
        dot_color="green",
        text_color="red",
    )
    html = result.as_raw_html()

    assert html.count('fill="blue"') == 2
    assert html.count('fill="green"') == 2
    assert html.count('fill="red"') == 4


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

    with pytest.raises(
        ValueError, match="Expected a single column, but got multiple columns"
    ):
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

    assert '<div style="width:100px; height:30px;"></div>' in html


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
    result = gt_plt_conf_int(gt=gt_test, column="data")
    html = result.as_raw_html()

    assert html.count("<circle") == 1
    assert html.count("<rect") == 1


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


def test_gt_plt_dumbbell_snap(snapshot):
    df = pd.DataFrame({"value_1": [10, 15, 25], "value_2": [15, 20, 30]})
    gt_test = GT(df)
    res = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_dumbbell_basic():
    df = pd.DataFrame({"value_1": [10, 15, 25], "value_2": [15, 20, 30]})
    gt_test = GT(df)
    result = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")
    html = result.as_raw_html()

    assert html.count('<circle stroke="white" stroke-width="1.5"') == 6
    assert html.count('r="3.75" fill="purple"') == 3
    assert html.count('r="3.75" fill="green"') == 3

    assert html.count("<rect") == 3
    assert html.count('height="3.0" rx="2" fill="grey"') == 3

    assert 'x="8.333333333333332" y="18.5" width="20.833333333333336"' in html
    assert 'x="29.166666666666668" y="18.5" width="20.833333333333332"' in html
    assert 'x="70.83333333333334" y="18.5" width="20.833333333333314"' in html

    assert html.count('<text dominant-baseline="lower" text-anchor="middle"') == 6
    assert html.count('font-size="10" font-weight="bold" fill="green"') == 3
    assert html.count('font-size="10" font-weight="bold" fill="purple"') == 3

    assert ">10</text>" in html
    assert ">15</text>" in html
    assert ">20</text>" in html
    assert ">25</text>" in html
    assert ">30</text>" in html


def test_gt_plt_dumbbell_custom_colors():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    result = gt_plt_dumbbell(
        gt=gt_test,
        col1="value_1",
        col2="value_2",
        col1_color="blue",
        col2_color="red",
        bar_color="green",
    )
    html = result.as_raw_html()

    assert html.count('fill="blue"') == 4
    assert html.count('fill="red"') == 4
    assert html.count('fill="green"') == 2


def test_gt_plt_dumbbell_custom_dimensions():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    result = gt_plt_dumbbell(
        gt=gt_test, col1="value_1", col2="value_2", width=200, height=50
    )
    html = result.as_raw_html()

    assert '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="50">' in html


def test_gt_plt_dumbbell_font_size():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    result = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2", font_size=14)
    html = result.as_raw_html()

    assert html.count('font-size="14"') == 4


def test_gt_plt_dumbbell_decimals():
    df = pd.DataFrame(
        {"group": ["A", "B"], "value_1": [10.123, 20.456], "value_2": [15.789, 25.012]}
    )
    gt_test = GT(df)

    result = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2", num_decimals=2)
    html = result.as_raw_html()

    assert "10.12" in html
    assert "15.79" in html


def test_gt_plt_dumbbell_with_label():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    result = gt_plt_dumbbell(
        gt=gt_test, col1="value_1", col2="value_2", label="Custom Label"
    )

    html = result.as_raw_html()
    assert "Custom Label" in html


def test_gt_plt_dumbbell_hides_col2():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)
    result = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")
    html = result.as_raw_html()

    assert "value_2" not in html
    assert "value_1" in html
    assert "group" in html


def test_gt_plt_dumbbell_with_none_values():
    df = pd.DataFrame({"value_1": [10, None, 30], "value_2": [15, 25, None]})
    gt_test = GT(df)

    result = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")
    html = result.as_raw_html()

    assert html.count('<div style="width:100px; height:30px;"></div>') == 2


def test_gt_plt_dumbbell_with_na_values():
    df = pd.DataFrame({"value_1": [10, np.nan], "value_2": [np.nan, 25]})
    gt_test = GT(df)
    result = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")
    html = result.as_raw_html()

    assert html.count('<div style="width:100px; height:30px;"></div>') == 2


def test_gt_plt_dumbbell_invalid_col1():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    with pytest.raises(KeyError):
        gt_plt_dumbbell(gt=gt_test, col1="invalid_col", col2="value_2")


def test_gt_plt_dumbbell_invalid_col2():
    df = pd.DataFrame({"value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    with pytest.raises(KeyError):
        gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="invalid_col")


def test_gt_plt_dumbbell_non_numeric_col1():
    df = pd.DataFrame({"value_1": ["text", "more_text"], "value_2": [15, 25]})
    gt_test = GT(df)

    with pytest.raises(ValueError, match="Expected all entries to be numeric or None."):
        gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")


def test_gt_plt_dumbbell_non_numeric_col2():
    df = pd.DataFrame({"value_1": [10, 20], "value_2": ["123", 30]})
    gt_test = GT(df)

    with pytest.raises(ValueError, match="Expected all entries to be numeric or None."):
        gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")


def test_gt_plt_dumbbell_same_values():
    df = pd.DataFrame({"value_1": [20, 20, 30], "value_2": [20, 30, 30]})
    gt_test = GT(df)

    result = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")
    html = result.as_raw_html()

    assert html.count('<text dominant-baseline="lower"') == 6
    assert html.count(">20</text>") == 3
    assert html.count(">30</text>") == 3
    assert html.count('width="0.0"') == 2


def test_gt_plt_dumbbell_reversed_values():
    df = pd.DataFrame({"value_1": [200, 300, 0], "value_2": [15, 20, 400]})
    gt_test = GT(df)

    result = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")
    html = result.as_raw_html()

    assert 'fill="purple" x="50.0" y="14.45">200</text>' in html
    assert 'fill="purple" x="70.83333333333334" y="14.45">300</text>' in html
    assert 'fill="purple" x="8.333333333333332" y="14.45">0</text>' in html

    assert 'fill="green" x="11.458333333333332" y="14.45">15</text>' in html
    assert 'fill="green" x="12.5" y="14.45">20</text>' in html
    assert 'fill="green" x="91.66666666666666" y="14.45">400</text>' in html


def test_gt_plt_winloss_snap(snapshot):
    df = pd.DataFrame(
        {
            "team": ["A", "B"],
            "games": [
                [1, 0.5, 0],
                [0, 0, 1],
            ],
        }
    )
    gt_test = GT(df)
    res = gt_plt_winloss(gt=gt_test, column="games")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_winloss_basic():
    df = pd.DataFrame({"team": ["A", "B"], "games": [[1, 0, 0.5], [0, 1, 1]]})
    gt_test = GT(df)

    result = gt_plt_winloss(gt=gt_test, column="games")
    html = result.as_raw_html()

    assert html.count('y="6.0" width="24.666666666666668" ') == 3
    assert html.count('y="12.0" width="24.666666666666668" ') == 3

    assert html.count('height="12.0" rx="2"') == 5
    assert html.count('height="6.0" rx="2"') == 1

    assert html.count('<rect x="0.0"') == 2
    assert html.count('<rect x="26.666666666666668"') == 2
    assert html.count('<rect x="53.333333333333336"') == 2

    assert html.count('fill="grey"') == 1
    assert html.count('fill="red"') == 2
    assert html.count('fill="blue"') == 3


def test_gt_plt_winloss_custom_colors():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 1, 1, 0, 0, 0.5]]})
    gt_test = GT(df)

    result = gt_plt_winloss(
        gt=gt_test,
        column="games",
        win_color="green",
        loss_color="black",
        tie_color="#FFA500",
    )
    html = result.as_raw_html()

    assert html.count('fill="green"') == 3
    assert html.count('fill="black"') == 2
    assert html.count('fill="#FFA500"') == 1


def test_gt_plt_winloss_custom_dimensions():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0]]})
    gt_test = GT(df)

    result = gt_plt_winloss(gt=gt_test, column="games", width=200, height=50)
    html = result.as_raw_html()

    assert '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="50">' in html
    assert '<rect x="0.0" y="10.0" width="98.0" height="20.0" rx="2"' in html
    assert '<rect x="100.0" y="20.0" width="98.0" height="20.0" rx="2"' in html


def test_gt_plt_winloss_shape_square():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0]]})
    gt_test = GT(df)

    result = gt_plt_winloss(gt=gt_test, column="games", shape="square")
    html = result.as_raw_html()

    assert html.count('rx="0.5"') == 2


def test_gt_plt_winloss_shape_pill():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0]]})
    gt_test = GT(df)

    result = gt_plt_winloss(gt=gt_test, column="games", shape="pill")
    html = result.as_raw_html()

    assert html.count('rx="2"') == 2


def test_gt_plt_winloss_spacing():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0, 1]]})
    gt_test = GT(df)

    result = gt_plt_winloss(gt=gt_test, column="games", width=90, spacing=6)
    html = result.as_raw_html()

    assert '<rect x="0.0" y="6.0" width="24.0"' in html
    assert '<rect x="30.0" y="12.0" width="24.0"' in html
    assert '<rect x="60.0" y="6.0" width="24.0"' in html


def test_gt_plt_winloss_with_empty_list():
    df = pd.DataFrame({"team": ["A", "B"], "games": [[], [1, 0]]})
    gt_test = GT(df)

    result = gt_plt_winloss(gt=gt_test, column="games")
    html = result.as_raw_html()

    assert '<div style="width:80px; height:30px;"></div>' in html


def test_gt_plt_winloss_with_none_values():
    df = pd.DataFrame({"team": ["A", "B"], "games": [[np.nan, 1, None, 0], [0.5, 1]]})
    gt_test = GT(df)

    result = gt_plt_winloss(gt=gt_test, column="games")
    html = result.as_raw_html()

    assert html.count('fill="blue"') == 2
    assert html.count('fill="red"') == 1
    assert html.count('fill="grey"') == 1
    assert html.count('x="20.0"') == 2
    assert html.count('x="60.0"') == 1


def test_gt_plt_winloss_with_invalid_values():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0.2, 0.5, 2, 0, "invalid"]]})
    gt_test = GT(df)

    with pytest.warns(
        UserWarning, match="Invalid value '.*' encountered in win/loss data. Skipping."
    ):
        result = gt_plt_winloss(gt=gt_test, column="games")
        html = result.as_raw_html()

    assert html.count('fill="blue"') == 1
    assert html.count('fill="grey"') == 1
    assert html.count('fill="red"') == 1


def test_gt_plt_winloss_different_length_lists():
    df = pd.DataFrame({"team": ["A", "B"], "games": [[1, 0], [1, 0, 0.5, 1, 0]]})
    gt_test = GT(df)

    result = gt_plt_winloss(gt=gt_test, column="games")
    html = result.as_raw_html()

    assert html.count('x="16.0"') == 2
    assert html.count('x="32.0"') == 1

    assert html.count('fill="blue"') == 3
    assert html.count('fill="red"') == 3
    assert html.count('fill="grey"') == 1


def test_gt_plt_winloss_invalid_column():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0]]})
    gt_test = GT(df)

    with pytest.raises(KeyError):
        gt_plt_winloss(gt=gt_test, column="invalid_column")


def test_gt_plt_winloss_spacing_warning():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0, 1, 0, 1]]})
    gt_test = GT(df)

    with pytest.warns(
        UserWarning,
        match="Spacing is too large relative to the width. No bars will be displayed.",
    ):
        gt_plt_winloss(
            gt=gt_test,
            column="games",
            width=10,
            spacing=5,
        )


def test_gt_plt_bar_stack_snap(snapshot):
    df = pd.DataFrame({"team": ["A", "B"], "values": [[10, 20], [40, 30]]})
    gt_test = GT(df)
    res = gt_plt_bar_stack(
        gt=gt_test, column="values", palette=["red", "blue", "green"]
    )

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_bar_stack_basic():
    df = pd.DataFrame({"team": ["A", "B"], "values": [[10, 20, 30], [40, 30, 20]]})
    gt_test = GT(df)

    result = gt_plt_bar_stack(gt=gt_test, column="values")
    html = result.as_raw_html()

    assert html.count('width="32.0"') == 2
    assert html.count('height="30"') == 8
    assert html.count("<rect") == 6

    assert html.count('height="30" fill="#000000"') == 2
    assert html.count('height="30" fill="#25bce6"') == 2
    assert html.count('height="30" fill="#9e9e9e"') == 2

    assert html.count('<text dominant-baseline="central" text-anchor="middle"') == 6


def test_gt_plt_bar_stack_custom_palette():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    result = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        palette=["red", "blue", "green"],
    )
    html = result.as_raw_html()

    assert 'fill="red"' in html
    assert 'fill="blue"' in html
    assert 'fill="green"' in html


def test_gt_plt_bar_stack_custom_dimensions():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    result = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        width=200,
        height=50,
    )
    html = result.as_raw_html()

    assert '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="50">' in html


def test_gt_plt_bar_stack_with_labels():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    result = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        labels=["Group 1", "Group 2", "Group 3"],
    )
    html = result.as_raw_html()

    assert "Group 1" in html
    assert "Group 2" in html
    assert "Group 3" in html


def test_gt_plt_bar_stack_relative_scaling():
    df = pd.DataFrame({"team": ["A", "B"], "values": [[1, 1], [2, 2]]})
    gt_test = GT(df)

    result = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        scale_type="relative",
    )
    html = result.as_raw_html()

    assert html.count('width="49.0"') == 4


def test_gt_plt_bar_stack_absolute_scaling():
    df = pd.DataFrame({"team": ["A", "B"], "values": [[1, 1], [2, 2]]})
    gt_test = GT(df)

    result = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        scale_type="absolute",
    )
    html = result.as_raw_html()

    assert html.count('width="49.0"') == 2
    assert html.count('width="24.5"') == 2


def test_gt_plt_bar_stack_with_empty_list():
    df = pd.DataFrame({"team": ["A", "B"], "values": [[], [10, 20, 30]]})
    gt_test = GT(df)

    result = gt_plt_bar_stack(gt=gt_test, column="values")
    html = result.as_raw_html()

    assert '<div style="width:100px; height:30px;"></div>' in html


def test_gt_plt_bar_stack_with_none_values():
    df = pd.DataFrame(
        {
            "team": ["A", "B", "C"],
            "values": [[None, 10, 20], [30, None, 40], [None, None, None]],
        }
    )
    gt_test = GT(df)
    result = gt_plt_bar_stack(gt=gt_test, column="values")
    html = result.as_raw_html()

    assert '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="30"></svg>'
    assert html.count("<rect") == 4


def test_gt_plt_bar_stack_with_na_values():
    df = pd.DataFrame(
        {
            "team": ["A", "B", "C"],
            "values": [[np.nan, 10, 20], [30, np.nan, 40], [None, np.nan, None]],
        }
    )
    gt_test = GT(df)
    result = gt_plt_bar_stack(gt=gt_test, column="values")
    html = result.as_raw_html()

    assert '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="30"></svg>'
    assert html.count("<rect") == 4


def test_gt_plt_bar_stack_spacing_warning():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    with pytest.warns(
        UserWarning,
        match="Spacing is too large relative to the width. No bars will be displayed.",
    ):
        result = gt_plt_bar_stack(
            gt=gt_test,
            column="values",
            width=10,
            spacing=5,
        )
        html = result.as_raw_html()

    assert (
        '<div style="display: flex;"><div style="width:10px; height:30px;"></div></div>'
        in html
    )


def test_gt_plt_bar_stack_invalid_column():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    with pytest.raises(KeyError):
        gt_plt_bar_stack(gt=gt_test, column="invalid_column")


def test_gt_plt_bar_stack_invalid_scale():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    with pytest.raises(ValueError):
        gt_plt_bar_stack(gt=gt_test, column="values", scale_type="invalid")  # type: ignore


def test_gt_plt_bar_pct_snap(snapshot, mini_gt):
    res = gt_plt_bar_pct(gt=mini_gt, column="num")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_bar_pct(mini_gt):
    result = gt_plt_bar_pct(gt=mini_gt, column="num")
    html = result.as_raw_html()
    assert html.count("<svg") == 3


def test_gt_plt_bar_pct_autoscale_on(mini_gt):
    result = gt_plt_bar_pct(mini_gt, column="num", autoscale=True, labels=True)
    html = result.as_raw_html()
    assert ">100%</text>" in html


def test_gt_plt_bar_pct_autoscale_off(mini_gt):
    result = gt_plt_bar_pct(mini_gt, column="num", autoscale=False, labels=True)
    html = result.as_raw_html()
    assert ">33.3%</text>" in html


def test_gt_plt_bar_pct_without_labels(mini_gt):
    result = gt_plt_bar_pct(mini_gt, column="num", labels=False)
    html = result.as_raw_html()
    assert "</text>" not in html


def test_gt_plt_bar_pct_column_decimal(mini_gt):
    result = gt_plt_bar_pct(
        mini_gt, column="num", autoscale=False, labels=True, decimals=2
    )
    html = result.as_raw_html()
    assert ">33.33%</text>" in html


def test_gt_plt_bar_pct_label_placement():
    df = pd.DataFrame({"x": [10, 20, 30, 40]})
    gt = GT(df)
    result_autoscale_on = gt_plt_bar_pct(gt, "x", autoscale=True, labels=True)
    html_autoscale_on = result_autoscale_on.as_raw_html()

    assert html_autoscale_on.count('x="5.0px" y="8.0px"') == 3
    assert 'x="30.0px" y="8.0px"' in html_autoscale_on

    result_autoscale_off = gt_plt_bar_pct(gt, "x", autoscale=False, labels=True)
    html_autoscale_off = result_autoscale_off.as_raw_html()

    assert 'x="5.0px" y="8.0px"' in html_autoscale_off
    assert 'x="15.0px" y="8.0px"' in html_autoscale_off
    assert 'x="25.0px" y="8.0px"' in html_autoscale_off
    assert 'x="35.0px" y="8.0px"' in html_autoscale_off


def test_gt_plt_bar_pct_column_containing_effective_int():
    df = pd.DataFrame({"num": [1, 2.0]})
    result = gt_plt_bar_pct(GT(df), column="num", autoscale=False, labels=True)
    html = result.as_raw_html()
    assert ">1%</text>" in html
    assert ">2%</text>" in html


@pytest.mark.parametrize("height, width", [(16, 100), (17, 101)])
def test_gt_plt_bar_pct_height_width(mini_gt, height, width):
    result = gt_plt_bar_pct(
        mini_gt, column="num", height=height, width=width, labels=True
    )
    html = result.as_raw_html()
    assert f'height="{height}px">' in html
    assert f'width="{width}px"' in html


@pytest.mark.parametrize(
    "font_style, font_size", [("bold", 10), ("italic", 11), ("normal", 12)]
)
def test_gt_plt_bar_pct_fnot_style_size(mini_gt, font_style, font_size):
    result = gt_plt_bar_pct(
        mini_gt,
        column="num",
        labels=True,
        font_style=font_style,
        font_size=font_size,
    )
    html = result.as_raw_html()
    assert f'font-style="{font_style}"' in html
    assert f'font-size="{font_size}px"' in html


def test_gt_plt_bar_pct_column_containing_some_none():
    df = pd.DataFrame({"num": [1, None, None]})
    result = gt_plt_bar_pct(GT(df), column="num")
    html = result.as_raw_html()
    assert html.count('fill="transparent"/>') == 2


def test_gt_plt_bar_pct_column_containing_all_none():
    df = pd.DataFrame({"num": [None, None, None]})
    with pytest.raises(ValueError, match="All values in the column are None."):
        gt_plt_bar_pct(GT(df), column="num")


def test_gt_plt_bar_pct_label_cutoff_invalid_number(mini_gt):
    with pytest.raises(
        ValueError, match="Label_cutoff must be a number between 0 and 1."
    ):
        gt_plt_bar_pct(mini_gt, column="num", label_cutoff=100)


def test_gt_plt_bar_pct_font_style_invalid_string(mini_gt):
    with pytest.raises(
        ValueError, match="Font_style must be one of 'bold', 'italic', or 'normal'."
    ):
        gt_plt_bar_pct(mini_gt, column="num", font_style="invalid")  # type: ignore


def test_gt_plt_bullet_snap(snapshot):
    df = pd.DataFrame(
        {"name": ["A", "B", "C"], "actual": [10, 15, 25], "target": [12, 18, 20]}
    )
    gt_test = GT(df)
    res = gt_plt_bullet(gt=gt_test, data_column="actual", target_column="target")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_bullet_basic():
    df = pd.DataFrame(
        {"name": ["A", "B", "C"], "actual": [10, 15, 25], "target": [12, 18, 20]}
    )
    gt_test = GT(df)
    result = gt_plt_bullet(gt=gt_test, data_column="actual", target_column="target")
    html = result.as_raw_html()

    assert html.count("<svg") == 3
    assert "target" not in html
    assert "actual" in html


def test_gt_plt_bullet_bar_height_too_high():
    df = pd.DataFrame({"actual": [10], "target": [12]})
    gt_test = GT(df)

    with pytest.warns(
        UserWarning,
        match="Bar_height must be less than or equal to the plot height. Adjusting bar_height to 100.",
    ):
        result = gt_plt_bullet(
            gt=gt_test,
            data_column="actual",
            target_column="target",
            bar_height=1000,
            height=100,
        )
        html = result.as_raw_html()

    assert html.count('height="100"') == 1
    assert 'height="1000"' not in html


def test_gt_plt_bullet_bar_height_too_low():
    df = pd.DataFrame({"actual": [10], "target": [12]})
    gt_test = GT(df)

    with pytest.warns(
        UserWarning,
        match="Bar_height cannot be negative. Adjusting bar_height to 0.",
    ):
        result = gt_plt_bullet(
            gt=gt_test,
            data_column="actual",
            target_column="target",
            bar_height=-100,
            height=1000,
        )
        html = result.as_raw_html()

    assert html.count('height="1000"') == 1
    assert 'height="-100"' not in html


def test_gt_plt_bullet_custom_colors():
    df = pd.DataFrame({"actual": [10, 20], "target": [15, 25]})
    gt_test = GT(df)

    result = gt_plt_bullet(
        gt=gt_test,
        data_column="actual",
        target_column="target",
        fill="blue",
        target_color="red",
    )
    html = result.as_raw_html()

    assert html.count('fill="blue"') == 2
    assert html.count('stroke="red"') == 2


def test_gt_plt_bullet_no_stroke_color():
    df = pd.DataFrame({"actual": [10], "target": [12]})
    gt_test = GT(df)

    result = gt_plt_bullet(
        gt=gt_test, data_column="actual", target_column="target", stroke_color=None
    )
    html = result.as_raw_html()

    assert 'stroke="transparent"' in html


def test_gt_plt_bullet_keep_data_column():
    df = pd.DataFrame({"actual": [10, 15], "target": [12, 18]})
    gt_test = GT(df)

    result = gt_plt_bullet(
        gt=gt_test, data_column="actual", target_column="target", keep_data_column=True
    )
    html = result.as_raw_html()

    assert ">actual plot</th>" in html
    assert ">actual</th>" in html
    assert html.count("<svg") == 2


def test_gt_plt_bullet_custom_dimensions():
    df = pd.DataFrame({"actual": [10, 18], "target": [12, 15]})
    gt_test = GT(df)

    result = gt_plt_bullet(
        gt=gt_test, data_column="actual", target_column="target", width=200, height=50
    )
    html = result.as_raw_html()

    assert html.count('width="200"') == 2
    assert html.count('height="50"') == 2


@pytest.mark.parametrize(
    "actual, target",
    [
        ([10, None, 30], [15, 25, None]),
        ([10, np.nan, 30], [15, 25, np.nan]),
    ],
)
def test_gt_plt_bullet_with_none_and_nan_values(actual, target):
    df = pd.DataFrame({"actual": actual, "target": target})
    gt_test = GT(df)

    result = gt_plt_bullet(gt=gt_test, data_column="actual", target_column="target")
    html = result.as_raw_html()

    assert isinstance(result, GT)
    assert html.count('<line stroke="darkgrey"') == 2
    assert html.count('fill="purple"') == 3
    assert html.count('width="0px" height="20px" fill="purple"') == 1


def test_gt_plt_bullet_invalid_data_column():
    df = pd.DataFrame({"actual": [10], "target": [12]})
    gt_test = GT(df)

    with pytest.raises(KeyError, match="Column 'invalid_col' not found"):
        gt_plt_bullet(gt=gt_test, data_column="invalid_col", target_column="target")


def test_gt_plt_bullet_invalid_target_column():
    df = pd.DataFrame({"actual": [10], "target": [12]})
    gt_test = GT(df)

    with pytest.raises(KeyError, match="Column 'invalid_col' not found"):
        gt_plt_bullet(gt=gt_test, data_column="actual", target_column="invalid_col")


def test_gt_plt_bullet_multiple_data_cols():
    df = pd.DataFrame({"actual": [10], "target": [12], "other": [5]})
    gt_test = GT(df)

    with pytest.raises(
        ValueError, match="Expected a single column, but got multiple columns"
    ):
        gt_plt_bullet(
            gt=gt_test, data_column=["actual", "other"], target_column="target"
        )


def test_gt_plt_bullet_multiple_target_cols():
    df = pd.DataFrame({"actual": [10], "target": [12], "other": [5]})
    gt_test = GT(df)

    with pytest.raises(
        ValueError, match="Expected a single column, but got multiple columns"
    ):
        gt_plt_bullet(
            gt=gt_test, data_column="actual", target_column=["target", "other"]
        )


def test_gt_plt_bullet_non_numeric_data_col():
    df = pd.DataFrame({"actual": ["text"], "target": [12]})
    gt_test = GT(df)

    with pytest.raises(TypeError, match="Invalid column type provided"):
        gt_plt_bullet(gt=gt_test, data_column="actual", target_column="target")


def test_gt_plt_bullet_non_numeric_target_col():
    df = pd.DataFrame({"actual": [10], "target": ["text"]})
    gt_test = GT(df)

    with pytest.raises(TypeError, match="Invalid column type provided"):
        gt_plt_bullet(gt=gt_test, data_column="actual", target_column="target")


def test_gt_plt_bullet_scaling():
    df = pd.DataFrame(
        {
            "actual": [10, 20, 30],
            "target": [40, 15, 25],
        }
    )
    gt_test = GT(df)

    result = gt_plt_bullet(gt=gt_test, data_column="actual", target_column="target")
    html = result.as_raw_html()

    assert html.count("<svg") == 3
    assert 'x1="58.5px" y1="0" x2="58.5px" y2="30px"' in html
    assert 'x1="21.0px" y1="0" x2="21.0px" y2="30px"' in html
    assert 'x1="36.0px" y1="0" x2="36.0px" y2="30px"' in html
