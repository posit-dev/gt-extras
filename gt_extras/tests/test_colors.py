from gt_extras import gt_highlight_cols, gt_hulk_col_numeric
from conftest import assert_rendered_body
import pytest

def test_gt_highlight_cols(snapshot, mini_gt):
    res = gt_highlight_cols(mini_gt)
    assert_rendered_body(snapshot, gt=res)

def test_gt_highlight_cols_font(mini_gt):
    res = gt_highlight_cols(mini_gt, font_weight="bolder").as_raw_html()
    assert "bolder" in res

def test_gt_highlight_cols_alpha(mini_gt):
    res = gt_highlight_cols(mini_gt, alpha=0.2, columns="num")
    html = res.as_raw_html()
    assert "#80bcd833" in html

def test_gt_hulk_col_numeric_snap(snapshot, mini_gt):
    res = gt_hulk_col_numeric(mini_gt)
    assert_rendered_body(snapshot, gt=res)

def test_gt_hulk_col_numeric_specific_cols(mini_gt):
    res = gt_hulk_col_numeric(mini_gt, columns=["num"])
    html = res.as_raw_html()
    assert 'style="color: #FFFFFF; background-color: #621b6f;"' in html
    assert 'style="color: #FFFFFF; background-color: #00441b;"' in html

def test_gt_hulk_col_numeric_palette(mini_gt):
    res = gt_hulk_col_numeric(mini_gt, columns=["num"], palette="viridis")
    html = res.as_raw_html()
    assert 'style="color: #FFFFFF; background-color: #440154;"' in html
    assert 'style="color: #000000; background-color: #fde725;"' in html 

@pytest.mark.xfail(reason="Will pass when great-tables updates the alpha bug in data_color()")
def test_gt_hulk_col_numeric_alpha(mini_gt):
    res = gt_hulk_col_numeric(mini_gt, columns=["num"], palette="viridis", alpha=0.2)
    html = res.as_raw_html()
    assert 'background-color: #44015433;"' in html
    assert 'background-color: #fde72533;"' in html 
    


