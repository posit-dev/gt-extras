from great_tables import GT, exibble
from gt_extras import gt_highlight_cols
from conftest import assert_rendered_body

# test with default, then one col, then other params
def test_gt_highlight_cols(snapshot):
    gt = GT(exibble, id = "cols")
    res = gt_highlight_cols(gt)
    assert_rendered_body(snapshot, gt=res)

def test_gt_highlight_cols_font():
    gt = GT(exibble, id = "cols")
    res = gt_highlight_cols(gt, font_weight="bolder").as_raw_html()
    assert "bolder" in res


