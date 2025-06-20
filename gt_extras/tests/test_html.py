# import pytest
import pandas as pd
from great_tables import GT
from gt_extras.html import gt_hyperlink

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
    df = pd.DataFrame({
        "Name": ["Google", "GitHub"],
        "Link": [
            gt_hyperlink("Visit Google", "https://google.com"),
            gt_hyperlink("View GitHub", "https://github.com", new_tab=False)
        ]
    })
    
    gt_table = GT(df)
    html_output = gt_table.as_raw_html()
    
    assert '<a href="https://google.com" target="_blank">Visit Google</a>' in html_output
    assert "https://github.com" in html_output
    assert 'target="_blank"' in html_output
    assert 'target="_self"' in html_output