from __future__ import annotations

from math import floor
from typing import Literal

from faicons import icon_svg
from great_tables import GT
from great_tables._tbl_data import SelectExpr, is_na

__all__ = ["fa_icon_repeat", "gt_fa_rating", "gt_fa_rank_change"]


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
    res = gt
    res = res.fmt(
        lambda x: _make_rating_html(x),
        columns=columns,
    )

    return res


def gt_fa_rank_change(
    gt: GT,
    column: SelectExpr,
    neutral_range: list[int] | int = [0],
    icon_type: Literal["angles", "arrow", "turn", "chevron", "caret"] = "angles",
    color_up: str = "green",
    color_down: str = "red",
    color_neutral: str = "grey",
    show_text: bool = True,
    font_color: str = "black",
    size: int = 12,
) -> GT:
    """
    Create rank change indicators in `GT` cells using FontAwesome icons.

    This function represents numeric rank changes in table column(s) by displaying FontAwesome
    icons alongside the numeric values. Positive values show up-pointing icons (e.g., arrows up),
    negative values show down-pointing icons (e.g., arrows down), and values within the neutral
    range show neutral indicators (equals sign).

    Parameters
    ----------
    gt
        A `GT` object to modify.

    column
        The column containing numeric rank change values.

    neutral_range
        A single number or list of two numbers defining the neutral range. If a single number,
        only that exact value is considered neutral. If a list of two numbers, any value within
        that range (inclusive) is considered neutral.

    icon_type
        The type of FontAwesome icon to use for indicating direction. Options include `"angles"`,
        `"arrow"`, `"turn"`, `"chevron"`, and `"caret"`.

    width
        The width of the icons in pixels.

    color_up
        The color for positive (upward) rank changes.

    color_down
        The color for negative (downward) rank changes.

    color_neutral
        The color for neutral rank changes (values within the neutral range).

    show_text
        Whether to display the numeric value alongside the icon.

    font_color
        The color for the numeric text displayed alongside the icons.

    font_size
        The font size for the numeric text in pixels.

    Returns
    -------
    GT
        A `GT` object with rank change indicators added to the specified column.

    Example
    -------
    ```{python}
    import pandas as pd
    from great_tables import GT
    import gt_extras as gte

    df = pd.DataFrame({
        "Team": ["Lakers", "Warriors", "Celtics", "Heat"],
        "Rank_Change": [3, -2, 0, 1]
    })

    gt = GT(df)
    gt.pipe(gte.gt_fa_rank_change, column="Rank_Change")
    ```
    """

    # TODO: consider in this and in others, do I really need to pass all these params in?
    # I can just get them from the parent function, but maybe that's less clean.
    def _make_ranked_cell_html(
        value: float,
        icon_type: Literal["angles", "arrow", "turn", "chevron", "caret"],
        color_up: str,
        color_down: str,
        color_neutral: str,
        show_text: bool,
        font_color: str,
        size: int,
        neutral_range: list[int],  # note not an int\
    ) -> str:
        if value is None or is_na(gt._tbl_data, value):
            return "<bold style='color:#d3d3d3;'>--</bold>"

        # Ensure neutral_range is a list with two elements (min and max)
        if isinstance(neutral_range, (int, float)):
            neutral_min, neutral_max = neutral_range, neutral_range
        elif isinstance(neutral_range, list):
            neutral_min, neutral_max = min(neutral_range), max(neutral_range)
        else:
            raise ValueError("neutral_range must be a single number or a list")

        if neutral_min <= value <= neutral_max:
            color = color_neutral
            fa_name = "equals"
        elif value > neutral_max:
            color = color_up
            fa_name = f"{icon_type}-up"
        else:  # value < neutral_min
            color = color_down
            fa_name = f"{icon_type}-down"

        my_fa = icon_svg(name=fa_name, fill=color, width=f"{size}px", a11y="sem")
        text_div = (
            f'<div style="text-align:right;">{str(value)}</div>' if show_text else ""
        )

        with_auto = "auto" if show_text else ""

        html = f"""
        <div aria-label="{str(value)}" role="img" style="
            padding:0px;
            display:inline-grid;
            grid-template-columns: {with_auto} {size}px;
            align-items:center;
            gap:{size / 8}px;
            color:{font_color};
            font-weight:bold;
            font-size:{size}px;
            min-width:{size}px;
        ">
            <div>{my_fa}</div>
            {text_div}
        </div>
        """
        return html.strip()

    res = gt
    res = res.fmt(
        lambda x: _make_ranked_cell_html(
            x,
            icon_type=icon_type,
            color_up=color_up,
            color_down=color_down,
            color_neutral=color_neutral,
            font_color=font_color,
            size=size,
            show_text=show_text,
            neutral_range=neutral_range,
        ),
        columns=column,
    )

    return res
