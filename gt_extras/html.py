from __future__ import annotations

from typing import Literal

from great_tables import GT
from great_tables._tbl_data import SelectExpr, is_na

from gt_extras._utils_column import _validate_and_get_single_column

__all__ = ["with_hyperlink", "with_tooltip", "gt_merge_stack"]


def with_hyperlink(text: str, url: str, new_tab: bool = True) -> int:
    """
    Create HTML hyperlinks for use in `GT` cells.

    The `with_hyperlink()` function creates properly formatted HTML hyperlink elements that can be
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
    --------
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
        gte.with_hyperlink(name, url)
        for name, url in zip(df["name"], df["url"])
    ]

    df["Github Stars"] = [
        gte.with_hyperlink(github_stars, repo_url, new_tab=False)
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

    # Why doesn't the output have to be wrapped in GT.html()?
    return f'<abbr style="{style}" title="{tooltip}">{label}</abbr>'


def gt_merge_stack(
    gt: GT,
    col1: SelectExpr,
    col2: SelectExpr,
    font_size_main: int = 14,
    font_size_secondary: int = 10,
    font_weight_main: Literal["normal", "bold", "bolder", "lighter"] | int = "bold",
    font_weight_secondary: Literal["normal", "bold", "bolder", "lighter"]
    | int = "normal",
    color_main: str = "black",
    color_secondary: str = "grey",
    small_caps: bool = True,
) -> GT:
    """
    Merge two columns into a stacked format within a `GT` object.

    The `gt_merge_stack()` function combines two columns in a `GT` object into a single column
    with a stacked format. The top section displays values from the first column (`col1`), and
    the bottom section displays values from the second column (`col2`). Both sections can be
    styled independently with customizable font sizes, weights, colors, and text variants.

    The resulting table will hide `col2`, and the orignal `col1` will contain the merged entries.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    col1
        The column containing values to display in the top section of the stack.

    col2
        The column containing values to display in the bottom section of the stack.

    font_size_main
        The font size for the top section of the stack.

    font_size_secondary
        The font size for the bottom section of the stack.

    font_weight_main
        The font weight for the top section of the stack. Options include `"normal"`, `"bold"`,
        `"bolder"`, `"lighter"`, or an integer value.

    font_weight_secondary
        The font weight for the bottom section of the stack.

    color_main
        The text color for the top section of the stack.

    color_secondary
        The text color for the bottom section of the stack.

    small_caps
        A boolean indicating whether the top section should use small caps styling.

    Returns
    -------
    GT
        A `GT` object with the merged and styled column.

    Examples
    -------
    ```{python}
    import pandas as pd
    from great_tables import GT
    import gt_extras as gte

    df = pd.read_csv("../assets/teams_colors_logos.csv")
    df = (df.filter(items=["team_nick", "team_abbr", "team_conf", "team_division", "team_wordmark"]).head(8))

    gt = GT(df, groupname_col="team_conf", rowname_col="team_nick")
    gt = gt.fmt_image(columns="team_wordmark")


    gt.pipe(
        gte.gt_merge_stack,
        col1="team_nick",
        col2="team_division",
    )
    ```
    """

    def _make_merge_stack_html(
        col1_val: str,
        col2_val: str,
        font_size_main: int,
        font_size_secondary: int,
        font_weight_main: str,
        font_weight_secondary: str,
        color_main: str,
        color_secondary: str,
        small_caps: bool,
    ) -> str:
        font_variant = "small-caps" if small_caps else "normal"

        top_section_html = f"""
        <div style="line-height:{font_size_main}px;">
            <span style="
                font-weight:{font_weight_main};
                font-variant:{font_variant};
                color:{color_main};
                font-size:{font_size_main}px;
            ">
                {col1_val}
            </span>
        </div>
        """.strip()

        bottom_section_html = f"""
        <div style="line-height:{font_size_secondary}px;">
            <span style="
                font-weight:{font_weight_secondary};
                color:{color_secondary};
                font-size:{font_size_secondary}px;
            ">
                {col2_val}
            </span>
        </div>
        """.strip()

        html = f"""
        <div>
            {top_section_html}
            {bottom_section_html}
        </div>
        """.strip()

        return html

    _, col1_vals = _validate_and_get_single_column(gt, expr=col1)
    _, col2_vals = _validate_and_get_single_column(gt, expr=col2)

    res = gt

    for i in range(len(gt._tbl_data)):
        col1_val = col1_vals[i]
        col2_val = col2_vals[i]

        if is_na(gt._tbl_data, col1_val):
            col1_val = ""
        if is_na(gt._tbl_data, col2_val):
            col2_val = ""

        res = res.fmt(
            lambda _, col1_val=col1_val, col2_val=col2_val: _make_merge_stack_html(
                col1_val=col1_val,
                col2_val=col2_val,
                font_size_main=font_size_main,
                font_size_secondary=font_size_secondary,
                font_weight_main=font_weight_main,
                font_weight_secondary=font_weight_secondary,
                color_main=color_main,
                color_secondary=color_secondary,
                small_caps=small_caps,
            ),
            columns=col1,
            rows=[i],
        )

    res = res.cols_hide(col2)

    return res
