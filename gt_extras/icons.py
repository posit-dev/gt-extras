from __future__ import annotations
from typing import Literal

from great_tables import GT
from great_tables._tbl_data import SelectExpr, is_na

from math import floor

from faicons import icon_svg

__all__ = ["fa_icon_repeat", "gt_fa_rating"]


def fa_icon_repeat(
    name: str = "star",
    repeats: int = 1,
    fill: str | None = "black",
    fill_opacity: int | str | None = 1,
    stroke: str | None = None,
    stroke_width: str | None = None,
    stroke_opacity: int | str | None = None,
    height: str | None = None,
    width: str | None = None,
    margin_left: str | None = "auto",
    margin_right: str | None = "0.2em",
    position: str | None = "relative",
    title: str | None = None,
    a11y: Literal["deco", "sem"] | None = "deco",
) -> str:
    """
    Create repeated FontAwesome SVG icons as HTML.

    The `fa_icon_repeat()` function generates one or more FontAwesome SVG icons using the `faicons`
    package and returns them as a single HTML string.

    Parameters
    ----------
    name
        The name of the FontAwesome icon to use (e.g., `"star"`, `"thumbs-up"`).

    repeats
        The number of times to repeat the icon.

    fill
        The fill color for the icon (e.g., `"yellow"`, `"#ffcc00"`). If `None`, uses the default.

    fill_opacity
        The opacity of the fill color (`0.0` - `1.0`).

    stroke
        The stroke color for the icon outline.

    stroke_width
        The width of the icon outline.

    stroke_opacity
        The opacity of the outline (`0.0` - `1.0`).

    height
        The height of the icon.

    width
        The width of the icon.

    margin_left
        The left margin for the icon.

    margin_right
        The right margin for the icon.

    position
        The CSS position property for the icon (e.g., `"absolute"`, `"relative"`, etc).

    title
        The title (tooltip) for the icon.

    a11y
        Accessibility mode: `"deco"` for decorative, `"sem"` for semantic.

    Returns
    -------
    str
        An HTML string containing the repeated SVG icons. If `repeats = 0`, this string will be empty.

    Examples
    --------
    ```{python}
    import pandas as pd
    from great_tables import GT
    import gt_extras as gte

    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Carol"],
        "Stars": [
            gte.fa_icon_repeat(name="star", repeats=3, fill="gold", fill_opacity=0.66),
            gte.fa_icon_repeat(name="star", repeats=2, fill="gold", stroke="black", stroke_width="3em"),
            gte.fa_icon_repeat(name="star", repeats=1, fill="orange"),
        ]
    })

    GT(df)
    ```

    Note
    --------
    See `icon_svg()` in the `faicons` package for further implementation details.
    """
    if repeats < 0:
        raise ValueError("repeats must be >= 0")

    icon = icon_svg(
        name=name,
        fill=fill,
        fill_opacity=fill_opacity,
        stroke=stroke,
        stroke_width=stroke_width,
        stroke_opacity=stroke_opacity,
        height=height,
        width=width,
        margin_left=margin_left,
        margin_right=margin_right,
        position=position,
        title=title,
        a11y=a11y,
    )

    repeated_icon = "".join(str(icon) for _ in range(repeats))

    return repeated_icon


def gt_fa_rating(
    gt: GT,
    column: SelectExpr,
    max_rating: int = 5,
    name: str = "star",
    color: str = "gold",
    height: int = 20,
) -> GT:
    """
    Create star ratings in `GT` cells using FontAwesome icons.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    column
        The column containing numeric rating values.

    max_rating
        The maximum rating value (number of total stars).

    name
        The FontAwesome icon name to use.

    color
        The color for filled stars.

    height
        The height of the rating icons in pixels.

    Returns
    -------
    GT
        A `GT` object with star ratings added to the specified column.
    """

    def _make_rating_html(rating_value):
        if rating_value is None or is_na(gt._tbl_data, float(rating_value)):
            return ""

        # Always round up
        rounded_rating = floor(float(rating_value) + 0.5)

        # Create stars
        stars = []
        for i in range(1, max_rating + 1):
            if i <= rounded_rating:
                # Filled star
                star = icon_svg(
                    name=name,
                    fill=color,
                    height=str(height) + "px",
                    a11y="sem",
                )
            else:
                # Empty star
                star = icon_svg(
                    name=name,
                    fill="grey",
                    height=str(height) + "px",
                    a11y="sem",
                    # TODO: or outline of a star
                    # fill_opacity=0,
                    # stroke="black",
                    # stroke_width=str(height) + "px",
                )
            stars.append(str(star))

        # Create label for accessibility
        label = f"{rating_value} out of {max_rating}"

        # Create div with stars
        stars_html = "".join(stars)
        div_html = f'<div title="{label}" aria-label="{label}" role="img" style="padding:0px">{stars_html}</div>'

        return div_html

    # Apply the formatting to the column
    res = gt.fmt(
        lambda x: _make_rating_html(x),
        columns=column,
    )

    return res
