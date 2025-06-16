from __future__ import annotations

from great_tables import GT, style, loc
from great_tables._tbl_data import SelectExpr

from typing import Literal

import matplotlib.colors as mcolors


def highlight_cols(
    gt: GT,
    columns: SelectExpr = None,  ## Todo check that this is good
    fill: str = "#80bcd8",
    alpha: int = 1,  ## Todo this doesn't exist in Python
    font_weight: Literal["normal", "bold", "bolder", "lighter"] | int = "normal",
    font_color: str = "#000000",
) -> GT:
    """
    Add color highlighting to one or more specific columns

    The `gt_highlight_cols()` function takes an existing `GT` object and adds highlighting color
    to the cell background of a specific column(s).

    Parameters
    ----------
    gt
        An existing `GT` object

    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list. If `None`, the alignment is applied to all columns.

    fill
        A character string indicating the fill color. If nothing is provided, then `"#80bcd8"`
        (light blue) will be used as a default.
    TODO see if the color can be displayed in some cool way

    alpha??
        TODO

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

    TODO
    The example below relabels columns from the `countrypops` data to start with uppercase.

    ```{python}
    from great_tables import GT
    from great_tables.data import countrypops

    countrypops_mini = countrypops.loc[countrypops["country_name"] == "Uganda"][
        ["country_name", "year", "population"]
    ].tail(5)

    (
        GT(countrypops_mini)
        .cols_label(
            country_name="Country Name",
            year="Year",
            population="Population"
        )
    )
    ```
    """

    # Altered wrt R package - no alpha
    def _to_alpha_hex_color(color: str, alpha: int) -> str:
        """
        Function description 
        TODO Can we do it without importing mcolors?
        """
        try:
            rbg_color = mcolors.to_rgb(color)        
            rbg_color_with_alpha = rbg_color + (alpha, )
            hex_color_with_alpha = mcolors.to_hex(rbg_color_with_alpha, keep_alpha=True)
            return hex_color_with_alpha
        except ValueError:
            raise ValueError(f"Invalid color value: {color}")

    alpha = min(max(alpha, 0), 1)
    fill_with_alpha = _to_alpha_hex_color(fill, alpha=alpha)

    res = gt.tab_style(
        style=[
            style.fill(color=fill_with_alpha),
            style.text(weight=font_weight, color=font_color),
            style.borders(sides=["top", "bottom"], color=fill),
        ],
        locations=loc.body(columns=columns),
    )

    return res
