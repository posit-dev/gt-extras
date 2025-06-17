from __future__ import annotations
from typing import Literal

from great_tables import GT, style, loc
from great_tables._tbl_data import SelectExpr

import matplotlib.colors as mcolors


def gt_highlight_cols(
    gt: GT,
    columns: SelectExpr = None,
    fill: str = "#80bcd8",
    alpha: int | None = None,
    font_weight: Literal["normal", "bold", "bolder", "lighter"] | int = "normal",
    font_color: str = "#000000",
) -> GT:
    # TODO see if the color can be displayed in some cool way in the docs
    """
    Add color highlighting to one or more specific columns.

    The `gt_highlight_cols()` function takes an existing `GT` object and adds highlighting color
    to the cell background of a specific column(s).

    Parameters
    ----------
    gt
        An existing `GT` object.

    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list. If `None`, the alignment is applied to all columns.

    fill
        A character string indicating the fill color. If nothing is provided, then `"#80bcd8"`
        (light blue) will be used as a default.

    alpha
        An integer `[0, 1]` for the alpha transparency value for the color as single value in the
        range of `0` (fully transparent) to `1` (fully opaque). If not provided the fill color will
        either be fully opaque or use alpha information from the color value if it is supplied in
        the `"#RRGGBBAA"` format.

    font_weight
        A string or number indicating the weight of the font. Can be a text-based keyword such as
        `"normal"`, `"bold"`, `"lighter"`, `"bolder"`, or, a numeric value between `1` and `1000`,
        inclusive. Note that only variable fonts may support the numeric mapping of weight.

    font_color
        A character string indicating the text color. If nothing is provided, then `"#000000"`
        (black) will be used as a default.

    Returns
    -------
    GT
        The `GT` object is returned. This is the same object that the method is called on so that
        we can facilitate method chaining.

    Examples
    --------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
    )

    gte.gt_highlight_cols(gt, columns="hp")
    ```
    """

    def _to_alpha_hex_color(color: str, alpha: int | None) -> str:
        """
        Return a hex color string with the specified alpha (transparency) channel.
        If alpha is outside [0, 1], it is clamped to that range. If alpha is None, the original
        color is returned.
        """
        # TODO Can we do it without importing mcolors?
        if alpha is None:
            return color
        try:
            rbg_color = mcolors.to_rgb(color)
            rbg_color_with_alpha = rbg_color + (alpha,)
            hex_color_with_alpha = mcolors.to_hex(rbg_color_with_alpha, keep_alpha=True)
            return hex_color_with_alpha
        except ValueError:
            raise ValueError(f"Invalid color value: {color}")

    if alpha is not None:
        alpha = min(max(alpha, 0), 1)
    fill_with_alpha = _to_alpha_hex_color(fill, alpha=alpha)

    res = gt.tab_style(
        style=[
            style.fill(color=fill_with_alpha),
            style.text(weight=font_weight, color=font_color),
            style.borders(sides=["top", "bottom"], color=fill_with_alpha),
        ],
        locations=loc.body(columns=columns),
    )

    return res


def gt_hulk_col_numeric(
    gt: GT,
    columns: SelectExpr = None,
    palette: str | list[str] | None = "PRGn",
    domain: list[str] | list[int] | list[float] | None = None,
    na_color: str | None = None,
    alpha: int | float | None = None, # TODO see note
    reverse: bool = False,
    autocolor_text: bool = True,
) -> GT:
    # TODO alpha is incomplete
    """
    Apply a color gradient to numeric columns in a `GT` table.

    The `gt_hulk_col_numeric()` function takes an existing `GT` object and applies a color gradient
    to the background of specified numeric columns, based on their values. This is useful for
    visually emphasizing the distribution or magnitude of numeric data within a table.

    Parameters
    ----------
    gt
        An existing `GT` object.

    columns
        The columns to target. Can be a single column name or a list of column names. If `None`,
        the color gradient is applied to all columns.

    palette
        The color palette to use for the gradient. Can be a string referencing a palette name or a
        list of color hex codes. Defaults to the `"PRGn"` palette from the ColorBrewer package.

    domain
        The range of values to map to the color palette. Should be a list of two values (min and
        max). If `None`, the domain is inferred from the data.

    na_color
        The color to use for missing (`NA`) values. If `None`, a default color is used.

    alpha
        The alpha (transparency) value for the colors, as a float between `0` (fully transparent)
        and `1` (fully opaque).

    reverse
        If `True`, reverses the color palette direction.

    autocolor_text
        If `True`, automatically adjusts text color for readability against the background.

    Returns
    -------
    GT
        The modified `GT` object, allowing for method chaining.

    Examples
    --------
    ```python
    from great_tables import GT
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(9)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label="Car")
    )

    gte.gt_hulk_col_numeric(gt, columns=["hp", "trq"])
    ```
    """
    res = gt.data_color(
        columns=columns,
        palette=palette,
        domain=domain,
        na_color=na_color,
        alpha=alpha, # TODO note alpha is not supported in data_color
        reverse=reverse,
        autocolor_text=autocolor_text,
    )

    return res
