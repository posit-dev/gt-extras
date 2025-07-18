import numpy as np
import pandas as pd
import pytest
from great_tables import GT

from gt_extras.icons import fa_icon_repeat, gt_fa_rank_change, gt_fa_rating
from gt_extras.tests.conftest import assert_rendered_body


def test_fa_icon_repeat_basic():
    html = fa_icon_repeat()
    assert isinstance(html, str)
    assert "<svg" in html
    assert html.count("<svg") == 1


def test_fa_icon_repeat_multiple():
    html = fa_icon_repeat(name="star", repeats=3)
    assert html.count("<svg") == 3


def test_fa_icon_repeat_fill_and_stroke():
    html = fa_icon_repeat(
        name="star", repeats=2, fill="gold", stroke="black", stroke_width="2"
    )
    assert "fill:gold" in html
    assert "stroke:black" in html
    assert html.count("<svg") == 2


def test_fa_icon_repeat_zero():
    html = fa_icon_repeat(name="star", repeats=0)
    assert html == ""


def test_fa_icon_repeat_negative():
    with pytest.raises(ValueError):
        fa_icon_repeat(name="star", repeats=-1)


def test_gt_fa_rating_basic():
    df = pd.DataFrame({"name": ["A", "B", "C"], "rating": [3.2, 4.7, 2.1]})

    gt = GT(df)
    html = gt_fa_rating(gt, columns="rating").as_raw_html()

    assert "<svg" in html
    assert "out of 5" in html
    assert "fill:gold" in html
    assert "fill:grey" in html


def test_gt_fa_rating_custom_max_rating():
    df = pd.DataFrame({"name": ["A", "B"], "rating": [2, 4]})

    gt = GT(df)
    html = gt_fa_rating(gt, columns="rating", max_rating=10).as_raw_html()

    assert "out of 10" in html
    assert html.count("<svg") == 20


def test_gt_fa_rating_custom_colors():
    df = pd.DataFrame({"name": ["A"], "rating": [3]})

    gt = GT(df)
    html = gt_fa_rating(
        gt, columns="rating", primary_color="red", secondary_color="blue"
    ).as_raw_html()

    assert "fill:red" in html
    assert "fill:blue" in html


def test_gt_fa_rating_custom_icon():
    df = pd.DataFrame({"name": ["A"], "rating": [4]})

    gt = GT(df)
    html = gt_fa_rating(gt, columns="rating", name="heart").as_raw_html()

    assert html.count("<svg") == 5
    assert "4.0 out of 5" in html


def test_gt_fa_rating_custom_height():
    df = pd.DataFrame({"name": ["A"], "rating": [2]})

    gt = GT(df)
    html = gt_fa_rating(gt, columns="rating", height=30).as_raw_html()

    assert "height:30px" in html
    assert "height:20px" not in html


def test_gt_fa_rating_with_na_values():
    df = pd.DataFrame({"name": ["A", "B", "C"], "rating": [3.0, np.nan, None]})

    gt = GT(df)
    html = gt_fa_rating(gt, columns="rating").as_raw_html()

    assert isinstance(html, str)
    assert html.count("<svg") == 5


@pytest.mark.parametrize(
    "ratings,expected_gold",
    [
        ([2.4, 2.5, 2.6, 3.0], 11),
        ([1.1, 1.9, 4.5, 5.0], 13),
        ([0.0, 0.5, 3.7, 4.2], 9),
        ([3.1, 3.2, 3.3, 3.49], 12),
    ],
)
def test_gt_fa_rating_rounding(ratings, expected_gold):
    df = pd.DataFrame({"name": ["A", "B", "C", "D"], "rating": ratings})

    gt = GT(df)
    html = gt_fa_rating(gt, columns="rating").as_raw_html()

    assert html.count("fill:gold") == expected_gold


def test_gt_fa_rating_non_numeric_error():
    df = pd.DataFrame({"name": ["A"], "rating": ["excellent"]})

    gt = GT(df)

    with pytest.raises(ValueError, match="Non-numeric rating value found"):
        gt_fa_rating(gt, columns="rating").as_raw_html()


def test_gt_fa_rating_multiple_columns():
    df = pd.DataFrame({"name": ["A", "B"], "rating1": [3, 4], "rating2": [2, 5]})

    gt = GT(df)
    html = gt_fa_rating(gt, columns=["rating1", "rating2"]).as_raw_html()

    assert html.count("<svg") == 20
    assert "out of 5" in html


def test_fa_icon_repeat_a11y_invalid_string():
    with pytest.raises(
        ValueError, match="A11y must be one of `None`, 'deco', or 'sem'"
    ):
        fa_icon_repeat(a11y="invalid")


# TODO: snapshot test
def test_gt_fa_rank_change_snap(snapshot):
    df = pd.DataFrame({"name": ["A", "B", "C"], "change": [3, -2, 0]})
    gt = GT(df)
    gt = gt_fa_rank_change(gt, column="change")

    assert_rendered_body(snapshot, gt)


def test_gt_fa_rank_change_basic():
    df = pd.DataFrame({"name": ["A", "B", "C"], "change": [3, -2, 0]})
    gt = GT(df)
    html = gt_fa_rank_change(gt, column="change").as_raw_html()

    assert '<div aria-label="-2" role="img"' in html
    assert html.count("<svg") == 3
    assert html.count("grid-template-columns: auto 1.2em;") == 3
    assert html.count("font-size:12px;") == 3
    assert html.count("min-width:12px;") == 3
    assert html.count("text-align:right;") == 3


def test_gt_fa_rank_change_colors():
    df = pd.DataFrame({"name": ["A", "B", "C"], "change": [5, -3, 0]})
    gt = GT(df)
    html = gt_fa_rank_change(
        gt,
        column="change",
        color_up="blue",
        color_down="orange",
        color_neutral="purple",
        font_color="yellow",
    ).as_raw_html()

    assert "fill:blue" in html
    assert "fill:orange" in html
    assert "fill:purple" in html
    assert "color:yellow" in html


def test_gt_fa_rank_change_neutral_range_single():
    df = pd.DataFrame({"name": ["A", "B", "C"], "change": [0, 1, -1]})
    gt = GT(df)
    html = gt_fa_rank_change(gt, column="change", neutral_range=0).as_raw_html()

    assert "Equals" in html
    assert "Angles up" in html
    assert "Angles down" in html


def test_gt_fa_rank_change_neutral_range_list():
    df = pd.DataFrame({"name": ["A", "B", "C", "D"], "change": [-2, -1, 1, 2]})
    gt = GT(df)
    html = gt_fa_rank_change(gt, column="change", neutral_range=[-1, 1]).as_raw_html()

    assert html.count('aria-label="Equals"') == 2
    assert html.count('aria-label="Angles up"') == 1
    assert html.count('aria-label="Angles down"') == 1


@pytest.mark.parametrize("icon_type", ["angles", "arrow", "turn", "chevron", "caret"])
def test_gt_fa_rank_change_icon_types(icon_type):
    df = pd.DataFrame({"name": ["A", "B"], "change": [1, -1]})
    gt = GT(df)
    html = gt_fa_rank_change(gt, column="change", icon_type=icon_type).as_raw_html()

    assert (
        f"{icon_type.capitalize()} Up" in html
        or f"{icon_type.capitalize()} up" in html
        or f"{icon_type}-up" in html
    )
    assert (
        f"{icon_type.capitalize()} Down" in html
        or f"{icon_type.capitalize()} down" in html
        or f"{icon_type}-down" in html
    )


def test_gt_fa_rank_change_show_text_false():
    df = pd.DataFrame({"name": ["A", "B"], "change": [3, -2]})
    gt = GT(df)
    html = gt_fa_rank_change(gt, column="change", show_text=False).as_raw_html()

    assert '<div style="text-align:right;">3</div>' not in html
    assert '<div style="text-align:right;">-2</div>' not in html
    assert "<svg" in html
    assert "grid-template-columns: auto;" in html


def test_gt_fa_rank_change_custom_size():
    df = pd.DataFrame({"name": ["A"], "change": [1]})
    gt = GT(df)
    html = gt_fa_rank_change(gt, column="change", size=20).as_raw_html()

    assert "width:20px" in html
    assert "font-size:20px" in html
    assert "gap:2.5px" in html


def test_gt_fa_rank_change_with_na_values():
    df = pd.DataFrame({"name": ["A", "B", "C"], "change": [3, np.nan, None]})
    gt = GT(df)
    html = gt_fa_rank_change(gt, column="change").as_raw_html()

    assert "color:#d3d3d3" in html
    assert "--" in html
    assert "<svg" in html  # Should still have svg for valid values


def test_gt_fa_rank_change_max_text_width_calculation():
    df = pd.DataFrame({"name": ["A", "B", "C"], "change": [5, -200, 1]})
    gt = GT(df)
    html = gt_fa_rank_change(gt, column="change", show_text=True).as_raw_html()

    # Max text width should be based on "-200" (4 characters)
    assert html.count("grid-template-columns: auto 2.4em;") == 3  # 4 chars * 0.6em


def test_gt_fa_rank_change_invalid_neutral_range():
    df = pd.DataFrame({"name": ["A"], "change": [1]})
    gt = GT(df)

    with pytest.raises(
        ValueError, match="neutral_range must be a single number or a list"
    ):
        gt_fa_rank_change(gt, column="change", neutral_range="invalid").as_raw_html()
