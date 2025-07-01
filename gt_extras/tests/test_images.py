from great_tables._text import Html
from gt_extras.images import img_header


def test_img_header_snapshot(snapshot):
    result = img_header(label="Test Label", img_url="https://example.com/image.png")
    assert snapshot == result


def test_img_header_basic():
    result = img_header(label="Test Label", img_url="https://example.com/image.png")

    assert isinstance(result, Html)
    assert "Test Label" in result.text
    assert "https://example.com/image.png" in result.text
    assert "height:60px;" in result.text
    assert "border-bottom:2px solid black;" in result.text
    assert "color:black;" in result.text


def test_img_header_custom_height_and_colors():
    result = img_header(
        label="Custom Label",
        img_url="https://example.com/custom.png",
        height=100,
        border_color="blue",
        text_color="red",
    )

    assert isinstance(result, Html)
    assert "Custom Label" in result.text
    assert "https://example.com/custom.png" in result.text
    assert "height:100px;" in result.text
    assert "border-bottom:2px solid blue;" in result.text
    assert "color:red;" in result.text


def test_img_header_custom_font_size():
    result = img_header(
        label="Font Size Test", img_url="https://example.com/font.png", font_size=20
    )

    assert isinstance(result, Html)
    assert "Font Size Test" in result.text
    assert "font-size:20px;" in result.text


def test_img_header_empty_label():
    result = img_header(label="", img_url="https://example.com/empty_label.png")

    assert isinstance(result, Html)
    assert "https://example.com/empty_label.png" in result.text
    assert "<div" in result.text
    assert "font-size:12px;" in result.text


def test_img_header_empty_url():
    result = img_header(label="Invalid URL Test", img_url="")

    assert isinstance(result, Html)
    assert "Invalid URL Test" in result.text
    assert 'src=""' in result.text


def test_img_header_no_border():
    result = img_header(
        label="No Border Test",
        img_url="https://example.com/no_border.png",
        border_color="transparent",
    )

    assert isinstance(result, Html)
    assert "No Border Test" in result.text
    assert "border-bottom:2px solid transparent;" in result.text
