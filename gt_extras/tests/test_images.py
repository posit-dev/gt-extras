from great_tables._text import Html

from gt_extras.images import add_text_img, img_header


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


def test_add_text_img_snapshot(snapshot):
    result = add_text_img(
        text="Test Text",
        img_url="https://example.com/image.png",
        height=40,
        left=True,
    )
    assert snapshot == result


def test_add_text_img_basic():
    result = add_text_img(
        text="Test Text",
        img_url="https://example.com/image.png",
        height=40,
        left=False,
    )

    assert isinstance(result, str)
    assert "Test Text" in result
    assert "https://example.com/image.png" in result
    assert "height:40px;" in result
    assert "flex-direction:row-reverse;" in result


def test_add_text_img_left():
    result = add_text_img(
        text="Left Aligned Text",
        img_url="https://example.com/left_image.png",
        height=50,
        left=True,
    )

    assert isinstance(result, str)
    assert "Left Aligned Text" in result
    assert "https://example.com/left_image.png" in result
    assert "height:50px;" in result
    assert "flex-direction:row;" in result


def test_add_text_img_custom_gap():
    result = add_text_img(
        text="Custom Gap Text",
        img_url="https://example.com/custom_gap.png",
        height=30,
        gap=15.0,
        left=False,
    )

    assert isinstance(result, str)
    assert "Custom Gap Text" in result
    assert "https://example.com/custom_gap.png" in result
    assert "height:30px;" in result
    assert "gap:15.0px;" in result


def test_add_text_img_alt_text():
    result = add_text_img(
        text="Alt Text Test",
        img_url="https://example.com/image.png",
        height=40,
        left=True,
        alt_text="Example Alt Text",
    )

    print(result)

    assert isinstance(result, str)
    assert "Alt Text Test" in result
    assert "https://example.com/image.png" in result
    assert "alt='Example Alt Text'" in result
    assert "height:40px;" in result


def test_add_text_img_empty_text():
    result = add_text_img(
        text="",
        img_url="https://example.com/empty_text.png",
        height=30,
        left=True,
    )

    assert isinstance(result, str)
    assert "https://example.com/empty_text.png" in result
    assert "<div" in result
    assert "height:30px;" in result


def test_add_text_img_empty_url():
    result = add_text_img(
        text="Empty URL Test",
        img_url="",
        height=30,
        left=False,
    )

    assert isinstance(result, str)
    assert "Empty URL Test" in result
    assert "src=''" in result
