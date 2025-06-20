from __future__ import annotations

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


def with_tooltip() -> str:
    return ""