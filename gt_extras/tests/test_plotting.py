import pytest
from gt_extras.tests.conftest import assert_rendered_body

import pandas as pd
import numpy as np
from great_tables import GT
from gt_extras import (
    gt_plt_bar,
    gt_plt_dot,
    gt_plt_conf_int,
    gt_plt_dumbbell,
    gt_plt_winloss,
    gt_plt_bar_stack,
)


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

    assert "border-radius:50%; margin-top:4px; display:inline-block;" in html
    assert "height:0.7em; width:0.7em;" in html

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
            "ci_lower": [0, 2, 2],
            "ci_upper": [4, 6, 5],
        }
    )
    gt_test = GT(df)
    html = gt_plt_conf_int(
        gt=gt_test, column="mean", ci_columns=["ci_lower", "ci_upper"]
    ).as_raw_html()

    assert "position:absolute;left:8.333333333333336px;bottom:11.5px" in html
    assert "top:18.5px; width:55.55555555555556px;" in html
    assert "height:3.0px; background:royalblue; border-radius:2px;" in html
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
    assert '<div style="position:relative; width:100px; height:30px;"></div>' in html


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


def test_gt_plt_dumbbell_snap(snapshot):
    df = pd.DataFrame({"value_1": [10, 15, 25], "value_2": [15, 20, 30]})
    gt_test = GT(df)
    res = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2")

    assert_rendered_body(snapshot, gt=res)


def test_gt_plt_dumbbell_basic():
    df = pd.DataFrame({"value_1": [10, 15, 25], "value_2": [15, 20, 30]})
    gt_test = GT(df)
    html = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2").as_raw_html()

    assert html.count("left:24.666666666666668px; top:15.5px; width:6.0px;") == 2
    assert html.count("height:3.0px; background:grey;") == 3
    assert html.count("transform:translateX(-50%); color:purple;") == 3
    assert html.count("position:absolute;") == 15


def test_gt_plt_dumbbell_custom_colors():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    html = gt_plt_dumbbell(
        gt=gt_test,
        col1="value_1",
        col2="value_2",
        col1_color="blue",
        col2_color="red",
        bar_color="green",
    ).as_raw_html()

    assert "background:blue;" in html
    assert "background:red;" in html
    assert "background:green;" in html


def test_gt_plt_dumbbell_custom_dimensions():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    html = gt_plt_dumbbell(
        gt=gt_test, col1="value_1", col2="value_2", width=200, height=50
    ).as_raw_html()

    assert "width:200px; height:50px;" in html


def test_gt_plt_dumbbell_font_size():
    df = pd.DataFrame({"group": ["A", "B"], "value_1": [10, 20], "value_2": [15, 25]})
    gt_test = GT(df)

    html = gt_plt_dumbbell(
        gt=gt_test, col1="value_1", col2="value_2", font_size=14
    ).as_raw_html()

    assert "font-size:14px;" in html


def test_gt_plt_dumbbell_decimals():
    df = pd.DataFrame(
        {"group": ["A", "B"], "value_1": [10.123, 20.456], "value_2": [15.789, 25.012]}
    )
    gt_test = GT(df)

    html = gt_plt_dumbbell(
        gt=gt_test, col1="value_1", col2="value_2", num_decimals=2
    ).as_raw_html()

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
    html = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2").as_raw_html()

    assert "value_2" not in html
    assert "value_1" in html
    assert "group" in html


def test_gt_plt_dumbbell_with_none_values():
    df = pd.DataFrame({"value_1": [10, None, 30], "value_2": [15, 25, None]})
    gt_test = GT(df)
    html = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2").as_raw_html()

    assert (
        html.count('<div style="position:relative; width:100px; height:30px;"></div>')
        == 2
    )


def test_gt_plt_dumbbell_with_na_values():
    df = pd.DataFrame({"value_1": [10, np.nan], "value_2": [np.nan, 25]})
    gt_test = GT(df)
    html = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2").as_raw_html()

    assert (
        html.count('<div style="position:relative; width:100px; height:30px;"></div>')
        == 2
    )


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
    html = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2").as_raw_html()

    assert html.count("position:absolute;") == 15
    assert html.count("20.0") == 3
    assert html.count("30.0") == 3


def test_gt_plt_dumbbell_reversed_values():
    df = pd.DataFrame({"value_1": [200, 300, 0], "value_2": [15, 20, 400]})
    gt_test = GT(df)
    html = gt_plt_dumbbell(gt=gt_test, col1="value_1", col2="value_2").as_raw_html()

    assert 'color:purple; font-size:10px; font-weight:bold;">0.0' in html
    assert 'color:green; font-size:10px; font-weight:bold;">400.0' in html
    assert 'color:purple; font-size:10px; font-weight:bold;">200.0' in html
    assert 'color:green; font-size:10px; font-weight:bold;">15.0' in html


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

    html = gt_plt_winloss(gt=gt_test, column="games").as_raw_html()

    assert (
        html.count("""width:24.666666666666668px;
                height:12.0px;
                background:blue;""")
        == 3
    )
    assert html.count("width:24.666666666666668px;") == 6
    assert html.count("border-radius:2px;") == 6
    assert html.count("background:grey;") == 1


def test_gt_plt_winloss_custom_colors():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 1, 1, 0, 0, 0.5]]})
    gt_test = GT(df)

    html = gt_plt_winloss(
        gt=gt_test,
        column="games",
        win_color="green",
        loss_color="black",
        tie_color="#FFA500",
    ).as_raw_html()

    assert html.count("background:green;") == 3
    assert html.count("background:black;") == 2
    assert html.count("background:#FFA500;") == 1


def test_gt_plt_winloss_custom_dimensions():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0]]})
    gt_test = GT(df)

    html = gt_plt_winloss(
        gt=gt_test, column="games", width=200, height=50
    ).as_raw_html()

    assert "width:200px; height:50px;" in html


def test_gt_plt_winloss_shape_square():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0]]})
    gt_test = GT(df)

    html = gt_plt_winloss(gt=gt_test, column="games", shape="square").as_raw_html()

    assert html.count("border-radius:0.5px;") == 2


def test_gt_plt_winloss_shape_pill():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0]]})
    gt_test = GT(df)

    html = gt_plt_winloss(gt=gt_test, column="games", shape="pill").as_raw_html()

    assert html.count("border-radius:2px;") == 2


def test_gt_plt_winloss_spacing():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0, 1]]})
    gt_test = GT(df)

    html = gt_plt_winloss(gt=gt_test, column="games", width=90, spacing=6).as_raw_html()

    assert "left:30.0px;" in html
    assert "left:60.0px;" in html
    assert html.count("width:24.0px") == 3


def test_gt_plt_winloss_with_empty_list():
    df = pd.DataFrame({"team": ["A", "B"], "games": [[], [1, 0]]})
    gt_test = GT(df)

    html = gt_plt_winloss(gt=gt_test, column="games").as_raw_html()

    assert '<div style="position:relative; width:80px; height:30px;"></div>' in html


def test_gt_plt_winloss_with_none_values():
    df = pd.DataFrame({"team": ["A", "B"], "games": [[np.nan, 1, None, 0], [0.5, 1]]})
    gt_test = GT(df)

    html = gt_plt_winloss(gt=gt_test, column="games").as_raw_html()

    assert html.count("background:blue;") == 2
    assert html.count("background:red;") == 1
    assert html.count("background:grey;") == 1
    assert html.count("left:20.0px") == 2
    assert html.count("left:60.0px") == 1


def test_gt_plt_winloss_with_invalid_values():
    df = pd.DataFrame({"team": ["A"], "games": [[1, 0.2, 0.5, 2, 0, "invalid"]]})
    gt_test = GT(df)

    with pytest.warns(
        UserWarning, match="Invalid value '.*' encountered in win/loss data. Skipping."
    ):
        html = gt_plt_winloss(gt=gt_test, column="games").as_raw_html()

    assert html.count("background:blue;") == 1
    assert html.count("background:grey;") == 1
    assert html.count("background:red;") == 1


def test_gt_plt_winloss_different_length_lists():
    df = pd.DataFrame({"team": ["A", "B"], "games": [[1, 0], [1, 0, 0.5, 1, 0]]})
    gt_test = GT(df)

    html = gt_plt_winloss(gt=gt_test, column="games").as_raw_html()

    assert html.count("left:16.0px;") == 2
    assert html.count("left:32.0px;") == 1

    assert html.count("background:blue;") == 3
    assert html.count("background:red;") == 3
    assert html.count("background:grey;") == 1


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

    html = gt_plt_bar_stack(gt=gt_test, column="values").as_raw_html()

    assert html.count("width:32.0px;") == 2
    assert html.count("height:30px;") == 8
    assert html.count("transform:translateX(-50%) translateY(-50%);") == 6


def test_gt_plt_bar_stack_custom_palette():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    html = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        palette=["red", "blue", "green"],
    ).as_raw_html()

    assert "background:red;" in html
    assert "background:blue;" in html
    assert "background:green;" in html


def test_gt_plt_bar_stack_custom_dimensions():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    html = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        width=200,
        height=50,
    ).as_raw_html()

    assert "width:200px;" in html
    assert "height:50px;" in html


def test_gt_plt_bar_stack_with_labels():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    html = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        labels=["Group 1", "Group 2", "Group 3"],
    ).as_raw_html()

    assert "Group 1" in html
    assert "Group 2" in html
    assert "Group 3" in html


def test_gt_plt_bar_stack_relative_scaling():
    df = pd.DataFrame({"team": ["A", "B"], "values": [[1, 1], [2, 2]]})
    gt_test = GT(df)

    html = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        scale_type="relative",
    ).as_raw_html()

    assert html.count("width:49.0px;")


def test_gt_plt_bar_stack_absolute_scaling():
    df = pd.DataFrame({"team": ["A", "B"], "values": [[1, 1], [2, 2]]})
    gt_test = GT(df)

    html = gt_plt_bar_stack(
        gt=gt_test,
        column="values",
        scale_type="absolute",
    ).as_raw_html()

    assert html.count("width:49.0px") == 2
    assert html.count("width:24.5px") == 2


def test_gt_plt_bar_stack_with_empty_list():
    df = pd.DataFrame({"team": ["A", "B"], "values": [[], [10, 20, 30]]})
    gt_test = GT(df)

    html = gt_plt_bar_stack(gt=gt_test, column="values").as_raw_html()

    assert '<div style="position:relative; width:100px; height:30px;"></div>' in html


def test_gt_plt_bar_stack_with_none_values():
    df = pd.DataFrame(
        {
            "team": ["A", "B", "C"],
            "values": [[None, 10, 20], [30, None, 40], [None, None, None]],
        }
    )
    gt_test = GT(df)
    html = gt_plt_bar_stack(gt=gt_test, column="values").as_raw_html()

    assert html.count("background:") == 4


def test_gt_plt_bar_stack_with_na_values():
    df = pd.DataFrame(
        {
            "team": ["A", "B", "C"],
            "values": [[np.nan, 10, 20], [30, np.nan, 40], [None, np.nan, None]],
        }
    )
    gt_test = GT(df)
    html = gt_plt_bar_stack(gt=gt_test, column="values").as_raw_html()

    assert html.count("background:") == 4


# TODO : not working
def test_gt_plt_bar_stack_spacing_warning():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    with pytest.warns(
        UserWarning,
        match="Spacing is too large relative to the width. No bars will be displayed.",
    ):
        html = gt_plt_bar_stack(
            gt=gt_test,
            column="values",
            width=10,
            spacing=5,
        ).as_raw_html()

    assert html.count("width:0.0px;") == 3


def test_gt_plt_bar_stack_invalid_column():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    with pytest.raises(KeyError):
        gt_plt_bar_stack(gt=gt_test, column="invalid_column")


def test_gt_plt_bar_stack_invalid_scale():
    df = pd.DataFrame({"team": ["A"], "values": [[10, 20, 30]]})
    gt_test = GT(df)

    with pytest.raises(ValueError):
        gt_plt_bar_stack(gt=gt_test, column="values", scale_type="invalid")
