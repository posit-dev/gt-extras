import pandas as pd
from great_tables import GT

from gt_extras.styling import gt_add_divider


def test_gt_add_divider_basic():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    gt = GT(df)

    html = gt_add_divider(gt, columns="A").as_raw_html()

    assert html.count("border-right:") == 3
    assert html.count("2px solid grey") == 3


def test_gt_add_divider_multiple_columns():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
    gt = GT(df)

    html = gt_add_divider(gt, columns=["A", "B"]).as_raw_html()

    assert html.count("border-right: 2px solid grey") == 2 * 3


def test_gt_add_divider_custom_sides():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    gt = GT(df)

    html = gt_add_divider(gt, columns="A", sides="left").as_raw_html()

    assert html.count("border-left:") == 3
    assert "border-right:" not in html


def test_gt_add_divider_custom_color_and_style():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    gt = GT(df)

    res = gt_add_divider(gt, columns="A", color="blue", divider_style="dashed")
    html = res.as_raw_html()

    assert "border-right: 2px dashed blue;" in html
    assert "grey" not in html


def test_gt_add_divider_custom_weight():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    gt = GT(df)

    html = gt_add_divider(gt, columns="A", weight=5).as_raw_html()

    assert "border-right: 5px solid grey;" in html
    assert "2px solid grey" not in html


def test_gt_add_divider_exclude_labels():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    gt = GT(df)

    html = gt_add_divider(gt, columns="A", include_labels=False).as_raw_html()

    assert html.count("border-right:") == 2


def test_gt_add_divider_multiple_sides():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    gt = GT(df)

    html = gt_add_divider(gt, columns="A", sides=["top", "bottom"]).as_raw_html()

    assert "border-top:" in html
    assert "border-bottom:" in html
    assert "border-right:" not in html
    assert "border-left:" not in html
