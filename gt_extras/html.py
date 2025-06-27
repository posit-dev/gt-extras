from __future__ import annotations
from typing import Literal

__all__ = ["gt_hyperlink", "with_tooltip"]


def gt_hyperlink(text: str, url: str, new_tab: bool = True) -> int:
    """
    Create HTML hyperlinks for use in `GT` cells.

    The `gt_hyperlink()` function creates properly formatted HTML hyperlink elements that can be
    used within table cells.

    Parameters
    ----------
    text
        A string that will be displayed as the clickable link text.

    url
        A string indicating the destination URL for the hyperlink.

    new_tab
        A boolean indicating whether the link should open in a new browser tab or the current tab.

    Returns
    -------
    str
        An string containing the HTML formatted hyperlink element.

    Examples
    -------
    ```{python}
    import pandas as pd
    from great_tables import GT
    import gt_extras as gte

    df = pd.DataFrame(
        {
            "name": ["Great Tables", "Plotnine", "Quarto"],
            "url": [
                "https://posit-dev.github.io/great-tables/",
                "https://plotnine.org/",
                "https://quarto.org/",
            ],
            "github_stars": [2334, 4256, 4628],
            "repo_url": [
                "https://github.com/posit-dev/great-tables",
                "https://github.com/has2k1/plotnine",
                "https://github.com/quarto-dev/quarto-cli",
            ],
        }
    )

    df["Package"] = [
        gte.gt_hyperlink(name, url)
        for name, url in zip(df["name"], df["url"])
    ]

    df["Github Stars"] = [
        gte.gt_hyperlink(github_stars, repo_url, new_tab=False)
        for github_stars, repo_url in zip(df["github_stars"], df["repo_url"])
    ]

    GT(df[["Package", "Github Stars"]])
    ```
    """
    target = "_self"
    if new_tab:
        target = "_blank"

    return f'<a href="{url}" target="{target}">{text}</a>'


def with_tooltip(
    label: str,
    tooltip: str,
    text_decoration_style: Literal["solid", "dotted", "none"] = "dotted",
    color: str | Literal["none"] = "blue",
) -> str:
    """
    Create HTML text with tooltip functionality for use in `GT` cells.

    The `with_tooltip()` function creates an HTML `<abbr>` element with a tooltip that appears
    when users hover over the text. The text can be styled with customizable underline styles
    and colors to indicate it's interactive.

    Parameters
    ----------
    label
        A string that will be displayed as the visible text.

    tooltip
        A string that will appear as the tooltip when hovering over the label.

    text_decoration_style
        A string indicating the style of underline decoration. Options are `"solid"`,
        `"dotted"`, or "none".

    color
        A string indicating the text color. If "none", no color styling is applied.

    Returns
    -------
    str
        An HTML string containing the formatted tooltip element.

    Examples
    -------
    ```{python}
    import pandas as pd
    from great_tables import GT
    import gt_extras as gte

    df = pd.DataFrame(
        {
            "name": ["Great Tables", "Plotnine", "Quarto"],
            "description": [
                "Absolutely Delightful Table-making in Python",
                "A grammar of graphics for Python",
                "An open-source scientific and technical publishing system",
            ],
        }
    )

    df["Package"] = [
        gte.with_tooltip(name, description, color = "none")
        for name, description in zip(df["name"], df["description"])
    ]

    GT(df[["Package"]])
    ```
    """

    # Throw if `text_decoration_style` is not one of the allowed values
    if text_decoration_style not in ["none", "solid", "dotted"]:
        raise ValueError(
            "Text_decoration_style must be one of 'none', 'solid', or 'dotted'"
        )

    if color is None:
        raise ValueError("color must be a string or 'none', not None.")

    style = "cursor: help; "

    if text_decoration_style != "none":
        style += "text-decoration: underline; "
        style += f"text-decoration-style: {text_decoration_style}; "
    else:
        style += "text-decoration: none; "

    if color != "none":
        style += f"color: {color}; "

    return f'<abbr style="{style}" title="{tooltip}">{label}</abbr>'
