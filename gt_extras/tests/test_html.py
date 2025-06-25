import pytest
import pandas as pd
from great_tables import GT
from gt_extras.html import gt_hyperlink, with_tooltip


def test_gt_hyperlink_basic():
    result = gt_hyperlink("Google", "https://google.com")
    expected = '<a href="https://google.com" target="_blank">Google</a>'
    assert result == expected


def test_gt_hyperlink_new_tab_false():
    result = gt_hyperlink("Google", "https://google.com", new_tab=False)
    expected = '<a href="https://google.com" target="_self">Google</a>'
    assert result == expected


def test_gt_hyperlink_new_tab_true():
    result = gt_hyperlink("GitHub", "https://github.com", new_tab=True)
    expected = '<a href="https://github.com" target="_blank">GitHub</a>'
    assert result == expected


def test_gt_hyperlink_empty_text():
    result = gt_hyperlink("", "https://example.com")
    expected = '<a href="https://example.com" target="_blank"></a>'
    assert result == expected


def test_gt_hyperlink_in_table():
    df = pd.DataFrame(
        {
            "Name": ["Google", "GitHub"],
            "Link": [
                gt_hyperlink("Visit Google", "https://google.com"),
                gt_hyperlink("View GitHub", "https://github.com", new_tab=False),
            ],
        }
    )

    gt_table = GT(df)
    html_output = gt_table.as_raw_html()

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
