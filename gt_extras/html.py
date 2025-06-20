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
        A character string that will be displayed as the clickable link text.

    url
        A character string indicating the destination URL for the hyperlink.

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
    text_decoration_style: Literal["underline", "dotted"] | None = "dotted",
    color: str | None = "blue",
) -> str:
    """
    Create HTML text with tooltip functionality for use in GT table cells.

    The `with_tooltip()` function creates an HTML `<abbr>` element with a tooltip that appears
    when users hover over the text. The text is styled with an underline and blue color to
    indicate it's interactive.

    Parameters
    ----------
    label
        A character string that will be displayed as the visible text.

    tooltip
        A character string that will appear as the tooltip when hovering over the label.

    Returns
    -------
    str
        An HTML string containing the formatted tooltip element.
    """

    style = "cursor: help; "

    if text_decoration_style is not None:
        style += "text-decoration: underline; "
        style += f"text-decoration-style: {text_decoration_style}; "
    else:
        style += "text-decoration: none; "

    if color is not None:
        style += f"color: {color}; "

    return f'<abbr style="{style}" title="{tooltip}">{label}</abbr>'
