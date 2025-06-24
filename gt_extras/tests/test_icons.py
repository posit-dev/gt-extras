from great_tables import GT
import pandas as pd
import numpy as np
import pytest
from gt_extras.icons import fa_icon_repeat, gt_fa_rating


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
    assert "fill:gray" in html


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
