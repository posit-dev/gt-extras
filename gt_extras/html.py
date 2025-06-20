from __future__ import annotations
from typing import Literal

__all__ = ["gt_hyperlink", "with_tooltip"]


def gt_hyperlink(text: str, url: str, new_tab: bool = True) -> int:
    """
    Create HTML hyperlinks for use in `GT` object cells.

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
    """
    target = "_self"
    if new_tab:
        target = "_blank"

    return f'<a href="{url}" target="{target}">{text}</a>'


def with_tooltip(
    label: str,
    tooltip: str,
    text_decoration_style: Literal["solid", "dotted"] | None = "dotted",
    color: str | None = "blue",
) -> str:
    """
    Create HTML text with tooltip functionality for use in GT table cells.

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
        `"dotted"`, or `None`. If nothing is provided, then `"dotted"` will be used as a default.

    color
        A string indicating the text color. If `None`, no color styling is applied.
        If nothing is provided, then `"blue"` will be used as a default.

    Returns
    -------
    str
        An HTML string containing the formatted tooltip element.
    """

    # Throw if `text_decoration_style` is not one of the three allowed values
    if text_decoration_style not in [None, "solid", "dotted"]:
        raise ValueError("Text_decoration_style must be one of `None`, 'solid', or 'dotted'")

    style = "cursor: help; "

    if text_decoration_style is not None:
        style += "text-decoration: underline; "
        style += f"text-decoration-style: {text_decoration_style}; "
    else:
        style += "text-decoration: none; "

    if color is not None:
        style += f"color: {color}; "

    return f'<abbr style="{style}" title="{tooltip}">{label}</abbr>'
