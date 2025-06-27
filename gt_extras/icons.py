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
    fill: str = "black",
    fill_opacity: int | str = 1,
    stroke: str | None = None,
    stroke_width: str | None = None,
    stroke_opacity: int | str | None = None,
    height: str | None = None,
    width: str | None = None,
    margin_left: str = "auto",
    margin_right: str = "0.2em",
    position: str = "relative",
    title: str | None = None,
    a11y: Literal["deco", "sem", "none"] = "deco",
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
        Accessibility mode: `"deco"` for decorative, `"sem"` for semantic, `"none"` will result in
        no accessibility features.

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
            gte.fa_icon_repeat(repeats=3, fill="gold", fill_opacity=0.66),
            gte.fa_icon_repeat(repeats=2, stroke="red", stroke_width="3em"),
            gte.fa_icon_repeat(name="star-half", repeats=1, fill="orange"),
        ]
    })

    GT(df)
    ```

    Note
    --------
    See `icon_svg()` in the `faicons` package for further implementation details.
    """
    # Throw if `a11y` is not one of the allowed values
    if a11y not in [None, "deco", "sem"]:
        raise ValueError("A11y must be one of `None`, 'deco', or 'sem'")

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
    columns: SelectExpr,
    max_rating: int = 5,
    name: str = "star",
    primary_color: str = "gold",
    secondary_color: str = "gray",
    height: int = 20,
) -> GT:
    """
    Create icon ratings in `GT` cells using FontAwesome icons.

    This function represents numeric ratings in table column(s) by displaying a row of FontAwesome
    icons (such as stars) in each cell. Filled icons indicate the rating value, while
    unfilled icons represent the remainder up to the maximum rating. Hover the icons to see the
    original numeric rating.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    columns
        One or more columns containing numeric rating values.

    max_rating
        The maximum rating value (number of total icons).

    name
        The FontAwesome icon name to use.

    primary_color
        The color for filled icons.

    secondary_color
        The color for unfilled icons.

    height
        The height of the rating icons in pixels.

    Returns
    -------
    GT
        A `GT` object with icon ratings added to the specified column(s).

    Example
    -------
    ```{python}
    from random import randint
    from great_tables import GT
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = (
        gtcars
        .loc[8:15, ["model", "mfr", "hp", "trq", "mpg_c"]]
        .assign(rating=[randint(1, 5) for _ in range(8)])
    )

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label="Car")
    )

    gt.pipe(gte.gt_fa_rating, columns="rating", name="r-project")
    ```
    """

    def _make_rating_html(rating_value):
        if rating_value is None or is_na(gt._tbl_data, rating_value):
            return ""
        try:
            rating_value = float(rating_value)
        except ValueError as e:
            raise ValueError(
                f"Non-numeric rating value found in column. Could not convert rating value '{rating_value}' to float."
            ) from e

        # Round to nearest integer
        rounded_rating = floor(float(rating_value) + 0.5)

        # Create label for accessibility
        label = f"{rating_value} out of {max_rating}"

        # Create stars
        icons = []
        for i in range(1, max_rating + 1):
            if i <= rounded_rating:
                # Filled star
                icon = icon_svg(
                    name=name,
                    fill=primary_color,
                    height=str(height) + "px",
                    a11y="sem",
                    title=label,
                )
            else:
                # Empty star
                icon = icon_svg(
                    name=name,
                    fill=secondary_color,
                    height=str(height) + "px",
                    a11y="sem",
                    title=label,
                    # TODO: or outline of a star
                    # fill_opacity=0,
                    # stroke="black",
                    # stroke_width=str(height) + "px",
                )
            icons.append(str(icon))

        # Create div with stars
        icons_html = "".join(icons)
        div_html = f'<div title="{label}" aria-label="{label}" role="img" style="padding:0px">{icons_html}</div>'

        return div_html

    # Apply the formatting to the columns
    res = gt.fmt(
        lambda x: _make_rating_html(x),
        columns=columns,
    )

    return res
