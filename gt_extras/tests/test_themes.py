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


def test_theme_538_fonts_snap(snapshot):
    themed_gt = gt_theme_538(gt=GT(exibble, id="538_table"))
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_espn_fonts_snap(snapshot):
    themed_gt = gt_theme_espn(gt=GT(exibble, id="espn_table"))
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_nytimes_fonts_snap(snapshot):
    themed_gt = gt_theme_nytimes(gt=GT(exibble, id="nytimes_table"))
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_guardian_fonts_snap(snapshot):
    themed_gt = gt_theme_guardian(gt=GT(exibble, id="guardian_table"))
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_excel_fonts_snap(snapshot):
    themed_gt = gt_theme_excel(gt=GT(exibble, id="excel_table"))
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_dot_matrix_fonts_snap(snapshot):
    themed_gt = gt_theme_dot_matrix(gt=GT(exibble, id="dot_matrix_table"))
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_dark_fonts_snap(snapshot):
    themed_gt = gt_theme_dark(gt=GT(exibble, id="dark_table"))
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_pff_fonts_snap(snapshot):
    themed_gt = gt_theme_pff(gt=GT(exibble, id="pff_table"))
    assert_rendered_global_imports(snapshot, themed_gt)
