import pytest
import pandas as pd
from great_tables import GT

from gt_extras.styling import gt_add_divider


@pytest.fixture
def sample_gt():
    sample_df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
    return GT(sample_df)


def test_gt_add_divider_basic(sample_gt):
    html = gt_add_divider(sample_gt, columns="A").as_raw_html()

    assert html.count("border-right:") == 3
    assert html.count("2px solid grey") == 3


def test_gt_add_divider_multiple_columns(sample_gt):
    html = gt_add_divider(sample_gt, columns=["A", "B"]).as_raw_html()

    assert html.count("border-right: 2px solid grey") == 2 * 3


def test_gt_add_divider_custom_sides(sample_gt):
    html = gt_add_divider(sample_gt, columns="A", sides="left").as_raw_html()

    assert html.count("border-left:") == 3
    assert "border-right:" not in html


def test_gt_add_divider_custom_color_and_style(sample_gt):
    res = gt_add_divider(sample_gt, columns="A", color="blue", divider_style="dashed")
    html = res.as_raw_html()

    assert "border-right: 2px dashed blue;" in html
    assert "grey" not in html


def test_gt_add_divider_custom_weight(sample_gt):
    html = gt_add_divider(sample_gt, columns="A", weight=5).as_raw_html()

    assert "border-right: 5px solid grey;" in html
    assert "2px solid grey" not in html


def test_gt_add_divider_exclude_labels(sample_gt):
    html = gt_add_divider(sample_gt, columns="A", include_labels=False).as_raw_html()

    assert html.count("border-right:") == 2


def test_gt_add_divider_multiple_sides(sample_gt):
    html = gt_add_divider(sample_gt, columns="A", sides=["top", "bottom"]).as_raw_html()

    assert "border-top:" in html
    assert "border-bottom:" in html
    assert "border-right:" not in html
    assert "border-left:" not in html
