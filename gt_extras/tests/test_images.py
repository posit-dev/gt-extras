from base64 import b64encode
from pathlib import Path

import pandas as pd
import polars as pl
import pytest
from conftest import assert_rendered_body
from great_tables import GT
from great_tables._text import Html

from gt_extras.images import FmtImage, add_text_img, gt_fmt_img_circle, img_header


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


def test_gt_fmt_img_circle_snapshot(snapshot):
    df = pd.DataFrame({"img": ["https://www.avatar1.png", "https://www.avatar2.png"]})
    gt_test = GT(df)

    res = gt_fmt_img_circle(gt_test, columns="img", encode=False, border_width="2px")
    assert_rendered_body(snapshot, gt=res)


def test_gt_fmt_img_circle_basic():
    df = pd.DataFrame({"img": ["test.png"]})
    gt_test = GT(df)

    result = gt_fmt_img_circle(gt_test, columns="img", encode=False, border_width="3px")
    html = result.as_raw_html()

    assert "border-radius: 50%;" in html
    assert "border-width: 3px;" in html
    assert "border-color: #0A0A0A;" in html
    assert "border-style: solid;" in html
    assert "test.png" in html


def test_gt_fmt_img_circle_custom_border():
    df = pd.DataFrame({"img": ["custom.jpg"]})
    gt_test = GT(df)

    result = gt_fmt_img_circle(
        gt_test,
        columns="img",
        encode=False,
        border_width=5,
        border_color="red",
        border_style="dashed",
    )
    html = result.as_raw_html()

    assert "border-width: 5px;" in html
    assert "border-color: red;" in html
    assert "border-style: dashed;" in html
    assert "border-radius: 50%;" in html


def test_gt_fmt_img_circle_custom_size():
    df = pd.DataFrame({"img": ["size_test.png"]})
    gt_test = GT(df)

    result = gt_fmt_img_circle(
        gt_test,
        columns="img",
        encode=False,
        height=80,
        width="80px",
        border_color="blue",
    )
    html = result.as_raw_html()

    assert "height: 80px;" in html
    assert "width: 80px;" in html
    assert "border-color: blue;" in html


def test_gt_fmt_img_circle_multiple_images():
    df = pd.DataFrame({"img": ["img1.png,img2.png"]})
    gt_test = GT(df)

    result = gt_fmt_img_circle(
        gt_test,
        columns="img",
        sep=" | ",
        encode=False,
        border_width="2px",
    )
    html = result.as_raw_html()

    assert "img1.png" in html
    assert "img2.png" in html
    assert " | " in html
    assert html.count("border-radius: 50%;") == 2


def test_gt_fmt_img_circle_no_border_defaults():
    """Test that without any border properties, no border styles are applied"""
    df = pd.DataFrame({"img": ["no_border.png"]})
    gt_test = GT(df)

    result = gt_fmt_img_circle(gt_test, columns="img", encode=False)
    html = result.as_raw_html()

    assert "border-radius: 50%;" in html
    assert "border-width:" not in html
    assert "border-color:" not in html


def test_gt_fmt_img_circle_partial_border_props():
    """Test that providing only border_color applies default width and style"""
    df = pd.DataFrame({"img": ["partial.png"]})
    gt_test = GT(df)

    result = gt_fmt_img_circle(
        gt_test, columns="img", encode=False, border_color="green"
    )
    html = result.as_raw_html()

    assert "border-color: green;" in html
    assert "border-width: 3px;" in html
    assert "border-style: solid;" in html


def test_gt_fmt_img_circle_custom_border_radius():
    df = pd.DataFrame({"img": ["radius_test.png"]})
    gt_test = GT(df)

    result = gt_fmt_img_circle(
        gt_test,
        columns="img",
        encode=False,
        border_radius="25%",
    )
    html = result.as_raw_html()

    assert "border-radius: 25%;" in html


def test_gt_fmt_img_circle_invalid_border_radius():
    df = pl.DataFrame({"img": ["test.png"], "height_col": ["80px"]})
    gt_test = GT(df)

    with pytest.raises(NotImplementedError):
        gt_fmt_img_circle(gt_test, columns="img", border_radius="4").as_raw_html()


def test_gt_fmt_img_circle_polars_expr_error():
    df = pl.DataFrame({"img": ["test.png"], "height_col": ["80px"]})
    gt_test = GT(df)

    with pytest.raises(NotImplementedError):
        gt_fmt_img_circle(
            gt_test,
            columns="img",
            height=pl.col("height_col"),
            border_width="2px",
        )


def test_gt_fmt_img_circle_as_latex():
    df = pl.DataFrame({"img": ["test.png"], "height_col": ["80px"]})
    gt_test = GT(df)

    with pytest.warns():
        gt_fmt_img_circle(gt_test, columns="img").as_latex()


def test_gt_fmt_img_circle_with_na_values():
    df = pd.DataFrame({"img": ["test.png", None, "another.jpg", pd.NA]})
    gt_test = GT(df)

    result = gt_fmt_img_circle(gt_test, columns="img", encode=False, border_width="2px")
    html = result.as_raw_html()

    assert "test.png" in html
    assert "another.jpg" in html
    assert isinstance(result, GT)


def strip_windows_drive(x):
    # this is a hacky approach to ensuring fmt_image path tests succeed
    # on our windows build. On linux root is just "/". On windows its a
    # drive name. Assumes our windows runner uses D:\
    return x.replace('src="D:\\', 'src="/')


@pytest.mark.parametrize(
    "ext,mime_type",
    [
        ("svg", "image/svg+xml"),
        ("jpg", "image/jpeg"),
        ("png", "image/png"),
    ],
)
def test_fmt_image_encode_param(tmpdir, ext, mime_type):
    content = "abc"
    p_img = Path(tmpdir) / f"some.{ext}"
    p_img.write_text(content)

    formatter = FmtImage(sep=" ", file_pattern=f"{{}}.{ext}", encode=True)
    res = formatter.to_html(f"{tmpdir}/some")

    b64_content = b64encode(content.encode()).decode()
    img_src = f"data:{mime_type};base64,{b64_content}"
    dst = formatter.SPAN_TEMPLATE.format(
        f'<img src="{img_src}" style="vertical-align: middle;">'
    )

    assert strip_windows_drive(res) == dst


@pytest.mark.parametrize(
    "url",
    ["http://posit.co/", "http://posit.co", "https://posit.co/", "https://posit.co"],
)
def test_fmt_image_path_http(url: str):
    formatter = FmtImage(encode=False, height=30, path=url, border_radius="50%")
    res = formatter.to_html("c")
    dst_img = '<img src="{}/c" style="height: 30px;border-radius: 50%;vertical-align: middle;">'.format(
        url.removesuffix("/")
    )
    dst = formatter.SPAN_TEMPLATE.format(dst_img)

    assert strip_windows_drive(res) == dst
