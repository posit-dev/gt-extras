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


def test_theme_excel_color(mini_gt):
    themed_gt = gt_theme_excel(gt=mini_gt, color="lightblue")
    html = themed_gt.as_raw_html()
    assert "lightblue" in html


def test_theme_dot_matrix_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_dot_matrix(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_dot_matrix_color(mini_gt):
    themed_gt = gt_theme_dot_matrix(gt=mini_gt, color="lightblue")
    html = themed_gt.as_raw_html()
    assert "lightblue" in html


def test_theme_dark_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_dark(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_pff_fonts_snap(snapshot, mini_gt):
    themed_gt = gt_theme_pff(gt=mini_gt)
    assert_rendered_global_imports(snapshot, themed_gt)


def test_theme_pff_dividers(mini_gt):
    themed_gt = gt_theme_pff(gt=mini_gt, divider="num")
    html = themed_gt.as_raw_html()
    assert "border-left: 2px solid lightgrey" in html


def test_theme_pff_spanner(mini_gt):
    gt_with_spanner = mini_gt.tab_spanner("Spanner Label", columns=["num", "char"])
    themed_gt = gt_theme_pff(gt=gt_with_spanner, spanners=["Spanner Label"])
    html = themed_gt.as_raw_html()
    assert "Spanner Label" in html
    # This assertion ensures the blank spanner is created
    assert '<span class="gt_column_spanner"> </span>' in html


def test_theme_pff_rank_col(mini_gt):
    themed_gt = gt_theme_pff(gt=mini_gt, rank_col="num")
    html = themed_gt.as_raw_html()
    assert "#e4e8ec" in html
