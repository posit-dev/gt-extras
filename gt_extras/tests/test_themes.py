from great_tables import GT, exibble
import gt_extras
# import pytest

def test_theme_538():
    assert True

def test_theme_538_snap(snapshot):
    themed_gt = gt_extras.gt_theme_538(gt=GT(exibble, id="538_table"))
    assert snapshot == themed_gt.as_raw_html()
    # TODO: make snapshot smaller (google font import + family)