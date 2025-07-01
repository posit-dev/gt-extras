from __future__ import annotations

from great_tables import html

__all__ = ["img_header"]


def img_header(
    label: str,
    img_url: str,
    height: float = 60,
    font_size: int = 12,
    border_color: str = "black",
    text_color: str = "black",
) -> html:
    """
    Create an HTML header with an image and a label.

    Parameters
    ----------
    label
        The text label to display below the image.

    img_url
        The URL of the image to display. This can be a local filepath or an image on the web.

    height
        The height of the image in pixels.

    font_size
        The font size of the label text.

    border_color
        The color of the border below the image.

    text_color
        The color of the label text.

    Returns
    -------
    html
        A Great Tables `html` element for the header.

    Examples
    -------
    ```{python}

    ```
    """

    img_html = f"""
    <img src="{img_url}" style="
        height:{height}px;
        border-bottom:2px solid {border_color};"
    />
    """

    label_html = f"""
    <div style="
        font-size:{font_size}px;
        color:{text_color};
        text-align:center;
        width:100%;
    ">
        {label}
    </div>
    """

    full_element = f"""
    <div style="text-align:center;">
        {img_html}
        {label_html}
    </div>
    """

    return html(full_element)
