import numpy as np
import pandas as pd
import pytest
from great_tables import GT

from gt_extras import gt_merge_stack, with_hyperlink, with_tooltip
from gt_extras.tests.conftest import assert_rendered_body


def test_with_hyperlink_basic():
    result = with_hyperlink("Google", "https://google.com")
    expected = '<a href="https://google.com" target="_blank">Google</a>'
    assert result == expected


def test_with_hyperlink_new_tab_false():
    result = with_hyperlink("Google", "https://google.com", new_tab=False)
    expected = '<a href="https://google.com" target="_self">Google</a>'
    assert result == expected


def test_with_hyperlink_new_tab_true():
    result = with_hyperlink("GitHub", "https://github.com", new_tab=True)
    expected = '<a href="https://github.com" target="_blank">GitHub</a>'
    assert result == expected


def test_with_hyperlink_empty_text():
    result = with_hyperlink("", "https://example.com")
    expected = '<a href="https://example.com" target="_blank"></a>'
    assert result == expected


def test_with_hyperlink_in_table():
    df = pd.DataFrame(
        {
            "Name": ["Google", "GitHub"],
            "Link": [
                with_hyperlink("Visit Google", "https://google.com"),
                with_hyperlink("View GitHub", "https://github.com", new_tab=False),
            ],
        }
    )

    gt = GT(df)
    html_output = gt.as_raw_html()

    assert (
        '<a href="https://google.com" target="_blank">Visit Google</a>' in html_output
    )
    assert "https://github.com" in html_output
    assert 'target="_blank"' in html_output
    assert 'target="_self"' in html_output


def test_with_tooltip_basic():
    result = with_tooltip("1", "Number One")
    expected = '<abbr style="cursor: help; text-decoration: underline; text-decoration-style: dotted; color: blue; " title="Number One">1</abbr>'
    assert result == expected


def test_with_tooltip_underline_style():
    result = with_tooltip("1", "Number One", text_decoration_style="solid")
    expected = '<abbr style="cursor: help; text-decoration: underline; text-decoration-style: solid; color: blue; " title="Number One">1</abbr>'
    assert result == expected


def test_with_tooltip_underline_fail():
    with pytest.raises(ValueError):
        with_tooltip("1", "Number One", text_decoration_style="underline")


def test_with_tooltip_None_color_fail():
    with pytest.raises(ValueError):
        with_tooltip("1", "Number One", color=None)


def test_with_tooltip_underline_style_none():
    result = with_tooltip("1", "Number One", text_decoration_style="none")
    expected = '<abbr style="cursor: help; text-decoration: none; color: blue; " title="Number One">1</abbr>'
    assert result == expected


def test_with_tooltip_color_none_pass():
    result = with_tooltip("1", "Number One", color="none")
    expected = '<abbr style="cursor: help; text-decoration: underline; text-decoration-style: dotted; " title="Number One">1</abbr>'
    assert result == expected


def test_with_tooltip_custom_color():
    result = with_tooltip("1", "Number One", color="red")
    expected = '<abbr style="cursor: help; text-decoration: underline; text-decoration-style: dotted; color: red; " title="Number One">1</abbr>'
    assert result == expected


def test_with_tooltip_in_table():
    df = pd.DataFrame(
        {
            "Number": ["1", "2"],
            "Description": [
                with_tooltip("1", "Number One"),
                with_tooltip(
                    "2", "Number Two", text_decoration_style="solid", color="red"
                ),
            ],
        }
    )

    html_output = GT(df).as_raw_html()

    assert 'title="Number One"' in html_output
    assert 'title="Number Two"' in html_output
    assert "cursor: help" in html_output
    assert "text-decoration-style: dotted" in html_output
    assert "text-decoration-style: solid" in html_output
    assert "color: blue" in html_output
    assert "color: red" in html_output


@pytest.fixture
def sample_gt():
    sample_df = pd.DataFrame(
        {
            "col1": ["AA", "BB", "CC", np.nan],
            "col2": ["XX", "YY", "ZZ", None],
            "col3": ["1", "2", "3", "4"],
        }
    )
    return GT(sample_df)


def test_gt_merge_stack_basic(sample_gt):
    gt = gt_merge_stack(
        sample_gt,
        col1="col1",
        col2="col2",
    )
    html = gt.as_raw_html()

    assert html.count("AA") == 1
    assert html.count("BB") == 1
    assert html.count("CC") == 1
    assert html.count("XX") == 1
    assert html.count("YY") == 1
    assert html.count("ZZ") == 1

    assert html.count("</span>") == 8
    assert html.count("color:grey;") == 4


def test_gt_merge_stack_snap(snapshot):
    df = pd.DataFrame({"col1": ["A", "B", "C"], "col2": ["X", 1, None]})
    gt = GT(df)
    res = gt_merge_stack(gt, col1="col1", col2="col2")
    assert_rendered_body(snapshot, gt=res)


def test_gt_merge_stack_empty_columns():
    sample_df = pd.DataFrame(
        {
            "col1": [None, None, np.nan],
            "col2": [None, np.nan, np.nan],
        }
    )
    gt = GT(sample_df)
    gt = gt_merge_stack(
        gt,
        col1="col1",
        col2="col2",
    )
    html = gt.as_raw_html()

    assert "None" not in html
    assert "nan" not in html


def test_gt_merge_stack_mixed_values():
    sample_df = pd.DataFrame(
        {
            "col1": ["AA", 2, None, np.nan, "EE"],
            "col2": [None, "YY", 3.5, np.nan, "ZZ"],
        }
    )
    gt = GT(sample_df)
    gt = gt_merge_stack(
        gt,
        col1="col1",
        col2="col2",
    )
    html = gt.as_raw_html()

    assert "AA" in html
    assert "2" in html
    assert "EE" in html
    assert "YY" in html
    assert "3.5" in html
    assert "ZZ" in html

    assert "None" not in html
    assert "nan" not in html


def test_gt_merge_stack_custom_styles(sample_gt):
    gt = gt_merge_stack(
        sample_gt,
        col1="col1",
        col2="col2",
        font_size_main=18,
        font_size_secondary=12,
        font_weight_main="lighter",
        font_weight_secondary="bold",
        color_main="blue",
        color_secondary="red",
        small_caps=False,
    )
    html = gt.as_raw_html()

    assert html.count("font-size:18px;") == 4
    assert html.count("font-size:12px;") == 4
    assert html.count("font-weight:lighter;") == 4
    assert html.count("font-weight:bold;") == 4
    assert html.count("color:blue;") == 4
    assert html.count("color:red;") == 4
    assert html.count("small-caps") == 0
