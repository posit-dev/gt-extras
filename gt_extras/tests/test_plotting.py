import pytest

from gt_extras import (
    gt_plt_bar,
)


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


def test_gt_plt_bar_scale_type_invalid_string(mini_gt):
    with pytest.raises(
        ValueError, match="Scale_type must be one of `None`, 'percent', or 'number'"
    ):
        gt_plt_bar(mini_gt, scale_type="invalid")


@pytest.mark.xfail(
    reason="TypeError is expected for now, but should be fixed in the future"
)
def test_gt_plt_bar_type_error(mini_gt):
    gt_plt_bar(gt=mini_gt, columns=["char"]).as_raw_html()
