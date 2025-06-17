from great_tables import GT, exibble
from gt_extras import (
    gt_theme_538,
    gt_theme_espn,
    gt_theme_nytimes,
    gt_theme_guardian,
    gt_theme_excel,
    gt_theme_dot_matrix,
    gt_theme_dark,
    gt_theme_pff,
)

from conftest import (
    # assert_rendered_body,
    # assert_rendered_columns,
    # assert_rendered_heading,
    # assert_rendered_source_notes,
    assert_rendered_global_imports,
)


def test_theme_538_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_538(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)

def test_theme_espn_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_espn(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)

def test_theme_nytimes_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_nytimes(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)

def test_theme_guardian_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_guardian(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)

def test_theme_excel_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_excel(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)

def test_theme_dot_matrix_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_dot_matrix(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)

def test_theme_dark_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_dark(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)

def test_theme_pff_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_pff(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)