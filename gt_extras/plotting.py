from __future__ import annotations
from typing import Literal

from great_tables import GT
from great_tables._tbl_data import SelectExpr, is_na
from great_tables._locations import resolve_cols_c

from great_tables._data_color.palettes import GradientPalette
from great_tables._data_color.constants import DEFAULT_PALETTE, ALL_PALETTES
from great_tables._data_color.base import (
    _html_color,
    _rescale_factor,
    _get_domain_factor,
    _rescale_numeric,
)

from svg import SVG, Line, Rect, Text

__all__ = ["gt_plt_bar", "gt_plt_dot"]

# TODO: keep_columns - this is tricky because we can't copy cols in the gt object, so we will have
# to handle the underlying _tbl_data.

# TODO: make sure numeric type passed in?

# TODO: default font for labels?

# TODO: let user pass domain?


def gt_plt_bar(
    gt: GT,
    columns: SelectExpr | None = None,
    fill: str = "purple",
    bar_height: int = 20,
    height: int = 30,
    width: int = 60,
    stroke_color: str | None = "black",
    scale_type: Literal["percent", "number"] | None = None,
    scale_color: str = "white",
    # keep_columns: bool = False,
) -> GT:
    """
    Create horizontal bar plots in `GT` cells.

    The `gt_plt_bar()` function takes an existing `GT` object and adds horizontal bar charts to
    specified columns. Each cell value is represented as a horizontal bar with length proportional
    to the cell's numeric value relative to the column's maximum value.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    columns
        The columns to target. Can be a single column name or a list of column names. If `None`,
        the bar plot is applied to all numeric columns.

    fill
        The fill color for the bars.

    bar_height
        The height of each individual bar in pixels.

    height
        The height of the bar plot in pixels.

    width
        The width of the maximum bar in pixels

    stroke_color
        The color of the vertical axis on the left side of the bar. The default is black, but if
        `None` is passed no stroke will be drawn.

    scale_type
        The type of value to show on bars. Options are `"number"`, `"percent"`, or `None` for no
        labels.

    scale_color
        The color of text labels on the bars (when `scale_type` is not `None`).

    Returns
    -------
    GT
        A `GT` object with horizontal bar plots added to the specified columns.

    Examples
    --------

    ```{python}
    from great_tables import GT, style, loc
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars.iloc[0:8, list(range(0, 3)) + list(range(5, 11))]

    gt = (
        GT(gtcars_mini,rowname_col="model")
        .tab_stubhead(label="Car")
        .tab_style(style=style.css("text-align: center;"), locations=loc.column_labels())
    )

    gte.gt_plt_bar(gt, columns=["hp", "hp_rpm", "trq", "trq_rpm", "mpg_c", "mpg_h"])
    ```

    Note
    --------
    Each column's bars are scaled independently based on that column's min/max values.
    """
    # A version with svg.py

    if bar_height > height:
        bar_height = height
        # TODO: warn the user

    if bar_height < 0:
        bar_height = 0
        # TODO: warn the user

    # Helper function to make the individual bars
    def _make_bar_html(
        val: int,
        fill: str,
        bar_height: int,
        height: int,
        width: int,
        max_val: int,
        stroke_color: str,
        scale_type: Literal["percent", "number"] | None,
        scale_color: str,
    ) -> str:
        text = ""
        if scale_type == "percent":
            text = str(round((val / max_val) * 100)) + "%"
        if scale_type == "number":
            text = val

        canvas = SVG(
            width=width,
            height=height,
            elements=[
                Rect(
                    x=0,
                    y=(height - bar_height) / 2,
                    width=width * val / max_val,
                    height=bar_height,
                    fill=fill,
                    # onmouseover="this.style.fill= 'blue';",
                    # onmouseout=f"this.style.fill='{fill}';",
                ),
                Text(
                    text=text,
                    x=(width * val / max_val) * 0.98,
                    y=height / 2,
                    fill=scale_color,
                    font_size=bar_height * 0.6,
                    text_anchor="end",
                    dominant_baseline="central",
                ),
                Line(
                    x1=0,
                    x2=0,
                    y1=0,
                    y2=height,
                    stroke_width=height / 10,
                    stroke=stroke_color,
                ),
            ],
        )
        return f'<div style="display: flex;">{canvas.as_str()}</div>'

    # Allow the user to hide the vertical stroke
    if stroke_color is None:
        stroke_color = "#FFFFFF00"

    def make_bar(val: int, max_val: int) -> str:
        return _make_bar_html(
            val=val,
            fill=fill,
            bar_height=bar_height,
            height=height,
            width=width,
            max_val=max_val,
            stroke_color=stroke_color,
            scale_type=scale_type,
            scale_color=scale_color,
        )

    # Get names of columns
    columns_resolved = resolve_cols_c(data=gt, expr=columns)

    res = gt
    for column in columns_resolved:
        # Maybe a try-catch here to prevent str types?

        full_col = gt._tbl_data[column]

        res = res.fmt(
            lambda x, m=max(full_col): make_bar(x, max_val=m),
            columns=column,
        )
    return res

    ##################

    # A semi-functional version with fmt_nanoplot()

    # Get names of columns
    # columns_resolved = resolve_cols_c(data=gt, expr=columns)

    # # if keep_columns:
    # #     for column in columns_resolved:
    # #         pass

    # # Have to loop because fmt_nanoplot only supports single columns
    # for column in columns_resolved:
    #     gt = gt.fmt_nanoplot(
    #         columns=column,
    #         plot_type="bar",
    #         plot_height=height,
    #         options=nanoplot_options(
    #             data_bar_fill_color=color,
    #             data_bar_negative_fill_color=color,
    #             data_bar_negative_stroke_width="0",  # this can't be an int on account of a bug in fmt_nanoplot
    #             data_bar_stroke_width=0,
    #         ),
    #     )

    ##################

    # A passing version with plotnine
    # def _make_bar_html(
    #     val: int,
    #     fill: str,
    #     height: int,
    #     range_x: tuple[int, int],
    # ) -> str:
    #     plot = (
    #         ggplot()
    #         + aes(
    #             x=1,
    #             y=val,
    #         )
    #         + geom_hline(yintercept=0)
    #         + geom_col(width=height, fill=fill, show_legend=False)
    #         + scale_y_continuous(limits=range_x)
    #         + scale_x_continuous(limits=(0.5, 1.5))
    #         + coord_flip()
    #         + theme_void()
    #     )

    #     buf = io.StringIO()
    #     plot.save(buf, format="svg", dpi=96, width=0.5, height=0.5, verbose=False)
    #     buf.seek(0)
    #     svg_content = buf.getvalue()
    #     buf.close()

    #     html = f"<div>{svg_content}</div>"
    #     return html

    # def make_bar(val: int, range_x: tuple[int, int]) -> str:
    #     return _make_bar_html(val=val, fill=color, height=height, range_x=range_x)

    # # Get names of columns
    # columns_resolved = resolve_cols_c(data=gt, expr=columns)

    # res = gt
    # for column in columns_resolved:
    #     full_col = gt._tbl_data[column]
    #     range_x = (0, max(full_col) * 1.02)

    #     res = res.fmt(
    #         lambda x, rng=range_x: make_bar(x, range_x=rng),
    #         columns=column,
    #     )

    # return res


def gt_plt_dot(
    gt: GT,
    category_col: SelectExpr,
    data_col: SelectExpr,
    # TODO: Add domain to `gt_plt_bar()`
    domain: list[int] | list[float] | None = None,  # TODO: pick default
    palette: list[str] | str | None = None,
) -> GT:
    """
    Create dot plots with thin horizontal bars in `GT` cells.

    The `gt_plt_dot()` function takes an existing `GT` object and adds dot plots with horizontal
    bar charts to a specified category column. Each cell displays a colored dot with the category
    label and a horizontal bar representing the corresponding numeric value from the data column.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    category_col
        The column containing category labels that will be displayed next to colored dots.

    data_col
        The column containing numeric values that will determine the length of the horizontal bars.

    domain
        The domain of values to use for the color scheme. This can be a list of floats or integers.
        If `None`, the domain is automatically set to `[0, max(data_col)]`.

    palette
        The color palette to use. This should be a list of colors
        (e.g., `["#FF0000", "#00FF00", "#0000FF"]`). A ColorBrewer palette could also be used,
        just supply the name (see [`GT.data_color()`](https://posit-dev.github.io/great-tables/reference/GT.data_color.html#great_tables.GT.data_color) for additional reference).
        If `None`, then a default palette will be used.

    Returns
    -------
    GT
        A `GT` object with dot plots and horizontal bars added to the specified category column.

    Examples
    --------
    ```{python}
    from great_tables import GT, style, loc
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars.loc[8:20, ["model", "mfr", "hp", "trq", "mpg_c"]]

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label="Car")
    )

    gte.gt_plt_dot(gt, category_col="mfr", data_col="hp")
    ```
    """

    def _make_bottom_bar_html(
        val: int,
        fill: str,
    ) -> str:
        scaled_value = val * 100
        inner_html = f' <div style="background:{fill}; width:{scaled_value}%; height:4px; border-radius: 2px;"></div>'
        html = f'<div style="flex-grow:1; margin-left:0px;"> {inner_html} </div>'

        return html

    def _make_dot_and_bar_html(
        bar_val: int,
        fill: str,
        dot_category_label: str,  # TODO: type?
    ) -> str:
        label_div_style = "display:inline-block; float:left; margin-right:0px;"

        dot_style = (
            f"height: 0.7em; width: 0.7em; background-color: {fill};"
            "border-radius: 50%; margin-top:4px; display:inline-block;"
            "float:left; margin-right:2px;"
        )

        padding_div_style = (
            "display: inline-block; float:right; line-height:20px;padding: 0px 2.5px;"
        )

        bar_container_style = "position: relative; top: 1.2em;"

        html = f'''
        <div>
            <div style="{label_div_style}">
                {dot_category_label}
                <div style="{dot_style}"></div>
                <div style="{padding_div_style}"></div>
            </div>
            <div style="{bar_container_style}">
                <div>{_make_bottom_bar_html(bar_val, fill=fill)}</div>
            </div>
        </div>
        '''

        return html.strip()

    # Get the underlying Dataframe
    data_table = gt._tbl_data

    # Get the data column
    data_col_name = resolve_cols_c(data=gt, expr=data_col)[
        0
    ]  # TODO: maybe some column not found error?
    data_col_vals = data_table[data_col_name].to_list()
    data_col_vals_filtered = [x for x in data_col_vals if not is_na(data_table, x)]

    # Check that data_col has numeric data
    if len(data_col_vals_filtered) and all(
        isinstance(x, (int, float)) for x in data_col_vals_filtered
    ):
        # If `domain` is not provided, then set it to [0, max]
        # Note this is different from the default behavior in data_color()
        if domain is None:
            domain = [0, max(data_col_vals_filtered)]

        # Rescale based on the given domain
        scaled_data_vals_filtered = _rescale_numeric(
            df=data_table, vals=data_col_vals_filtered, domain=domain
        )
    else:
        raise ValueError(
            f"Invalid column type provided ({data_col_name}). Please ensure that the column is numeric."
        )

    # Reconstruct full-length scaled_data_vals with NAs as 0
    # TODO: is there a better way to do this?
    scaled_data_vals = []
    filtered_idx = 0
    for original_val in data_col_vals:
        if is_na(data_table, original_val):
            scaled_data_vals.append(0)  # NA becomes 0
        else:
            scaled_data_vals.append(scaled_data_vals_filtered[filtered_idx])
            filtered_idx += 1

    # Get the category column, used for colors
    category_col_name = resolve_cols_c(data=gt, expr=category_col)[0]
    category_col_vals = data_table[category_col_name].to_list()

    # If palette is not provided, use a default palette
    if palette is None:
        palette = DEFAULT_PALETTE

    # Otherwise get the palette from great_tables._data_color
    elif isinstance(palette, str):
        palette = ALL_PALETTES.get(palette, [palette])

    # Standardize values in `palette` to hexadecimal color values
    palette = _html_color(colors=palette)

    # Rescale the category column for the purpose of assigning colors to each dot
    category_domain = _get_domain_factor(df=data_table, vals=category_col_vals)
    scaled_category_vals = _rescale_factor(
        df=data_table, vals=category_col_vals, domain=category_domain, palette=palette
    )

    # Create a color scale function from the palette
    color_scale_fn = GradientPalette(colors=palette)

    # Call the color scale function on the scaled categoy values to get a list of colors
    color_vals = color_scale_fn(scaled_category_vals)

    # Apply gt.fmt() to each row individually, so we can access the data_value for that row
    res = gt
    for i in range(len(data_table)):
        data_val = scaled_data_vals[i]
        color_val = color_vals[i]

        res = res.fmt(
            lambda x, data=data_val, fill=color_val: _make_dot_and_bar_html(
                dot_category_label=x, fill=fill, bar_val=data
            ),
            columns=category_col,
            rows=[i],
        )

    return res
