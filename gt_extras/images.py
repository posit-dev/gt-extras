from __future__ import annotations

from great_tables import html
from great_tables._helpers import px
from great_tables._text import Html

__all__ = ["add_text_img", "img_header"]


def img_header(
    label: str,
    img_url: str,
    height: float = 60,
    font_size: int = 12,
    border_color: str = "black",
    text_color: str = "black",
) -> Html:
    """
    Create an HTML header with an image and a label, suitable for a column label.

    Parameters
    ----------
    label
        The text label to display below the image.

    img_url
        The URL of the image to display. This can be a filepath or an image on the web.

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
    import pandas as pd
    from great_tables import GT, md
    import gt_extras as gte

    df = pd.DataFrame(
        {
            "Category": ["Points", "Rebounds", "Assists", "Blocks", "Steals"],
            "Hart": [1051, 737, 453, 27, 119],
            "Brunson": [1690, 187, 475, 8, 60],
            "Bridges": [1444, 259, 306, 43, 75],
        }
    )

    hart_header = gte.img_header(
        label="Josh Hart",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3062679.png",
    )

    brunson_header = gte.img_header(
        label="Jalen Brunson",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3934672.png",
    )

    bridges_header = gte.img_header(
        label="Mikal Bridges",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3147657.png",
    )

    (
        GT(df, rowname_col="Category")
        .tab_source_note(md("Images and data courtesy of [ESPN](https://www.espn.com)"))
        .cols_label(
            {
                "Hart": hart_header,
                "Brunson": brunson_header,
                "Bridges": bridges_header,
            }
        )
    )
    ```
    See Also
    -------
    [`add_text_img()`](https://posit-dev.github.io/gt-extras/reference/add_text_img)
    """

    img_html = f"""
    <img src="{img_url}" style="
        height:{px(height)};
        object-fit:contain;
        object-position: bottom;
        border-bottom:2px solid {border_color};"
    />
    """.strip()

    label_html = f"""
    <div style="
        font-size:{px(font_size)};
        color:{text_color};
        text-align:center;
        width:100%;
    ">
        {label}
    </div>
    """.strip()

    full_element = f"""
    <div style="text-align:center;">
        {img_html}
        {label_html}
    </div>
    """.strip()

    return html(full_element)


def add_text_img(
    text: str,
    img_url: str,
    height: int = 30,
    gap: float = 3.0,
    left: bool = False,
    alt_text: str = "",
) -> str:
    """
    Create an HTML element with text and an image, displayed inline.

    Note that depending on where
    you are placing the output in the table, you may want to wrap it in
    [`GT.html()`](https://posit-dev.github.io/great-tables/reference/html).

    Parameters
    ----------
    text
        The text to display alongside the image.

    img_url
        The URL of the image to display. This can be a filepath or an image on the web.

    height
        The height of the image in pixels.

    gap
        The spacing between the text and the image in pixels.

    left
        If `True`, the image is displayed to the left of the text.

    alt_text
        The alternative text for the image, used for accessibility and displayed if the image
        cannot be loaded.

    Returns
    -------
    str
        A string with html content of the combined image and text. Depending on where you are
        placing the output in the table, you may want to wrap it in
        [`GT.html()`](https://posit-dev.github.io/great-tables/reference/html).

    Examples
    --------
    ```{python}
    import pandas as pd
    from great_tables import GT, md, html
    import gt_extras as gte

    df = pd.DataFrame(
        {
            "Player": ["Josh Hart", "Jalen Brunson"],
            "Points": [1051, 1690],
            "Assists": [453, 475],
        }
    )

    hart_img = gte.add_text_img(
        text="Josh Hart",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3062679.png",
    )

    brunson_img = gte.add_text_img(
        text="Jalen Brunson",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3934672.png",
    )

    df["Player"] = [hart_img, brunson_img]
    gt = (
        GT(df, rowname_col="Player")
        .tab_source_note(md("Images and data courtesy of [ESPN](https://www.espn.com)"))
    )

    gt
    ```

    We can even apply the `add_text_img()` function to content outside of body/stub cells.
    We must remember to wrap the output in [`GT.html()`](https://posit-dev.github.io/great-tables/reference/html)
    so the table renders the element properly.

    ```{python}
    points_with_img = gte.add_text_img(
        text="Points",
        img_url="../assets/hoop.png",
        left=True,
    )

    assists_with_img = gte.add_text_img(
        text="Assists",
        img_url="../assets/pass.png",
        left=True,
    )

    points_img_html = html(points_with_img)
    assists_img_html = html(assists_with_img)

    (
        gt
        .cols_label({"Points": points_img_html, "Assists": assists_img_html})
        .cols_align("center")
    )
    ```
    See Also
    --------
    [`img_header()`](https://posit-dev.github.io/gt-extras/reference/img_header)
    """

    flex_direction = "row" if left else "row-reverse"

    combined_html = f"""
    <div style='display:flex; flex-direction:{flex_direction}; align-items:center; gap:{px(gap)};'>
        <div style='flex-shrink: 0;'>
            <img src='{img_url}' alt='{alt_text}'
            style='height:{px(height)}; width:auto; object-fit:contain;'/>
        </div>
        <div style='flex-grow:1;'>
            {text}
        </div>
    </div>
    """.strip()

    return combined_html
