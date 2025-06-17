from gt_extras import gt_highlight_cols, gt_hulk_col_numeric
from conftest import assert_rendered_body

def test_gt_highlight_cols(snapshot, mini_gt):
    res = gt_highlight_cols(mini_gt)
    assert_rendered_body(snapshot, gt=res)

def test_gt_highlight_cols_font(mini_gt):
    res = gt_highlight_cols(mini_gt, font_weight="bolder").as_raw_html()
    assert "bolder" in res

def test_gt_hulk_col_numeric_default(snapshot, mini_gt):
    res = gt_hulk_col_numeric(mini_gt)
    assert_rendered_body(snapshot, gt=res)

def test_gt_hulk_col_numeric_specific_cols(snapshot, mini_gt):
    res = gt_hulk_col_numeric(mini_gt, columns=["num"])
    assert_rendered_body(snapshot, gt=res)

def test_gt_hulk_col_numeric_palette(snapshot, mini_gt):
    res = gt_hulk_col_numeric(mini_gt, columns=["num"], palette="viridis")
    assert_rendered_body(snapshot, gt=res)


