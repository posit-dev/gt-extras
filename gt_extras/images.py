from __future__ import annotations

from great_tables import html
from great_tables._text import Html

__all__ = ["img_header"]


def img_header(
    label: str,
    img_url: str,
    height: float = 60,
    font_size: int = 12,
    border_color: str = "black",
    text_color: str = "black",
) -> Html:
    """
    Create an HTML header with an image and a label, apt for a column label.

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
    """

    img_html = f"""
    <img src="{img_url}" style="
        height:{height}px;
        border-bottom:2px solid {border_color};"
    />
    """.strip()

    label_html = f"""
    <div style="
        font-size:{font_size}px;
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
