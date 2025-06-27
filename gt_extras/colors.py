from __future__ import annotations
from typing import Literal

from great_tables import GT, style, loc
from great_tables._tbl_data import SelectExpr, is_na
from great_tables._locations import resolve_cols_c

from great_tables._data_color.base import _html_color, _add_alpha
from great_tables._data_color.constants import DEFAULT_PALETTE, ALL_PALETTES
from great_tables._data_color.palettes import GradientPalette


from gt_extras._utils_column import (
    _scale_numeric_column,
    _validate_and_get_single_column,
)

__all__ = ["gt_highlight_cols", "gt_hulk_col_numeric", "gt_color_box"]


def gt_highlight_cols(
    gt: GT,
    columns: SelectExpr = None,
    fill: str = "#80bcd8",
    alpha: int | None = None,
    font_weight: Literal["normal", "bold", "bolder", "lighter"] | int = "normal",
    font_color: str = "#000000",
) -> GT:
    # TODO: see if the color can be displayed in some cool way in the docs
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
        A string indicating the fill color. If nothing is provided, then `"#80bcd8"`
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
        A string indicating the text color. If nothing is provided, then `"#000000"`
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

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(8)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
    )

    gt.pipe(gte.gt_highlight_cols, columns="hp")
    ```
    """
    # Throw if `font_weight` is not one of the allowed values
    if isinstance(font_weight, str):
        if font_weight not in ["normal", "bold", "bolder", "lighter"]:
            raise ValueError(
                "Font_weight must be one of 'normal', 'bold', 'bolder', or 'lighter', or an integer"
            )
    elif not isinstance(font_weight, (int, float)):
        raise TypeError("Font_weight must be an int, float, or str")

    if alpha:
        fill = _html_color(colors=[fill], alpha=alpha)[0]

    res = gt.tab_style(
        style=[
            style.fill(color=fill),
            style.text(weight=font_weight, color=font_color),
            style.borders(sides=["top", "bottom"], color=fill),
        ],
        locations=loc.body(columns=columns),
    )

    return res


def gt_hulk_col_numeric(
    gt: GT,
    columns: SelectExpr = None,
    palette: str | list[str] = "PRGn",
    domain: list[int] | list[float] | None = None,
    na_color: str | None = None,
    alpha: int | float | None = None,  # TODO: see note
    reverse: bool = False,
    autocolor_text: bool = True,
) -> GT:
    # TODO: alpha is incomplete
    """
    Apply a color gradient to numeric columns in a `GT` object.

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
    ```{python}
    from great_tables import GT
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars.loc[0:8, ["model", "mfr", "year", "hp", "trq", "mpg_h"]]

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label="Car")
    )

    gt.pipe(gte.gt_hulk_col_numeric, columns=["hp", "trq", "mpg_h"])
    ```

    A more involved setup.

    ```{python}
    from great_tables.data import towny

    towny_mini = towny[
        [
            "name",
            "pop_change_1996_2001_pct",
            "pop_change_2001_2006_pct",
            "pop_change_2006_2011_pct",
            "pop_change_2011_2016_pct",
            "pop_change_2016_2021_pct",
        ]
    ].head(10)

    gt = (
        GT(towny_mini, rowname_col="name")
        .tab_stubhead(label="Town")
        .tab_spanner(
            label="Population Change",
            columns=[1, 2, 3, 4, 5]
        )
        .cols_label(
            pop_change_1996_2001_pct="1996-2001",
            pop_change_2001_2006_pct="2001-2006",
            pop_change_2006_2011_pct="2006-2011",
            pop_change_2011_2016_pct="2011-2016",
            pop_change_2016_2021_pct="2016-2021",
        )
    )

    gt.pipe(gte.gt_hulk_col_numeric, columns=[1, 2, 3, 4, 5], domain = [-0.1, 0.23])
    ```
    """
    res = gt.data_color(
        columns=columns,
        palette=palette,
        domain=domain,
        na_color=na_color,
        alpha=alpha,  # TODO: note alpha is not supported in data_color
        reverse=reverse,
        autocolor_text=autocolor_text,
    )

    return res


def gt_color_box(
    gt: GT,
    columns: SelectExpr,
    domain: list[int] | list[float] | None = None,
    palette: list[str] | str | None = None,
    alpha: float = 0.2,
    # TODO: decide between allowing the user to set this or width
    min_width: int | float = 70,
    min_height: int | float = 20,
    font_weight: str = "normal",
) -> GT:
    """
    Add PFF-style color boxes to numeric columns in a `GT` object.

    The `gt_color_box()` function takes an existing `GT` object and adds colored boxes to
    specified numeric columns. Each box contains a colored square and the numeric value,
    with colors mapped to the data values using a gradient palette.

    Parameters
    ----------
    gt
        An existing `GT` object.

    columns
        The columns to target. Can be a single column name or a list of column names.

    domain
        The range of values to map to the color palette. Should be a list of two values (min and
        max). If `None`, the domain is inferred to be the min and max of the data range.

    palette
        The color palette to use. This should be a list of colors
        (e.g., `["#FF0000", "#00FF00", "#0000FF"]`). A ColorBrewer palette could also be used,
        just supply the name (see [`GT.data_color()`](https://posit-dev.github.io/great-tables/reference/GT.data_color.html#great_tables.GT.data_color) for additional reference).
        If `None`, then a default palette will be used.

    alpha
        The alpha (transparency) value for the background colors, as a float between `0` (fully
        transparent) and `1` (fully opaque).

    min_width
        The minimum width of each color box in pixels.

    min_height
        The minimum height of each color box in pixels.

    font_weight
        A string indicating the weight of the font for the numeric values. Can be `"normal"`,
        `"bold"`, or other CSS font-weight values. Defaults to `"normal"`.

    Returns
    -------
    GT
        The modified `GT` object, allowing for method chaining.

    Examples
    --------
    ```{python}
    from great_tables import GT
    from great_tables.data import islands
    import gt_extras as gte

    islands_mini = (
        islands
        .sort_values(by="size", ascending=False)
        .head(10)
    )

    gt = (
        GT(islands_mini, rowname_col="name")
        .tab_stubhead(label="Island")
    )

    gt.pipe(gte.gt_color_box, columns="size", palette=["lightblue", "navy"])
    ```
    """
    # Get the underlying `GT` data
    data_table = gt._tbl_data

    def _make_color_box(value: float, fill: str, alpha: float = 0.2):
        if is_na(data_table, value):
            return "<div></div>"

        background_color = fill
        fill_with_alpha = _add_alpha([fill], alpha)[0]

        # Main container style
        main_box_style = (
            f"min-height:{min_height}px; min-width:{min_width}px;"
            f"background-color:{fill_with_alpha}; display:flex; border-radius:5px;"
            f"align-items:center; padding:0px {min_width / 10}px;"
        )

        # Small color square style
        color_square_style = (
            f"height:{min_height * 0.65}px; width:{min_height * 0.65}px;"
            f"background-color:{background_color}; display:flex; border-radius:4px;"
        )

        # Value text style
        value_text_style = (
            f"line-height:20px; margin-left: {min_width / 10}px;"
            f"font-weight:{font_weight}; white-space:nowrap;"
        )

        html = f'''
        <div>
            <div style="{main_box_style}">
                <div style="{color_square_style}"></div>
                <div style="{value_text_style}">{str(value)}</div>
            </div>
        </div>
            '''

        return html.strip()

    columns_resolved = resolve_cols_c(data=gt, expr=columns)

    res = gt
    for column in columns_resolved:
        # Validate and get data column
        col_name, col_vals = _validate_and_get_single_column(
            gt,
            column,
        )

        # Process numeric data column
        scaled_vals = _scale_numeric_column(
            data_table, col_name, col_vals, domain, default_domain_min_zero=False
        )

        # If palette is not provided, use a default palette
        if palette is None:
            palette = DEFAULT_PALETTE
        # Otherwise get the palette from great_tables._data_color
        elif isinstance(palette, str):
            palette = ALL_PALETTES.get(palette, [palette])

        # Standardize values in `palette` to hexadecimal color values
        palette = _html_color(colors=palette)

        # Create a color scale function from the palette
        color_scale_fn = GradientPalette(colors=palette)

        # Call the color scale function on the scaled values to get a list of colors
        color_vals = color_scale_fn(scaled_vals)

        # Apply gt.fmt() to each row individually, so we can access the color_value for that row
        for i in range(len(data_table)):
            color_val = color_vals[i]

            res = res.fmt(
                lambda x, fill=color_val: _make_color_box(
                    value=x, fill=fill, alpha=alpha
                ),
                columns=column,
                rows=[i],
            )

    return res
