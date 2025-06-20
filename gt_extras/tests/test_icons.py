import pytest
from gt_extras.icons import fa_icon_repeat


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


def test_fa_icon_repeat_negative_fail():
    with pytest.raises(ValueError):
        fa_icon_repeat(name="star", repeats=-1)


def test_fa_icon_repeat_a11y_invalid_string():
    with pytest.raises(
        ValueError, match="A11y must be one of `None`, 'deco', or 'sem'"
    ):
        fa_icon_repeat(a11y="invalid")
