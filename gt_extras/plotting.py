from __future__ import annotations
from typing import Literal

from great_tables import GT
from great_tables._tbl_data import SelectExpr
from great_tables._locations import resolve_cols_c

from svg import SVG, Line, Rect, Text

__all__ = ["gt_plt_bar"]

# TODO: keep_columns - this is tricky because we can't copy cols in the gt object, so we will have
# to handle the underlying _tbl_data.

# TODO: make sure numeric type passed in?

# TODO: default font for labels?


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

    # Throw if `scale_type` is not one of the allowed values
    if scale_type not in [None, "percent", "number"]:
        raise ValueError("Scale_type must be one of `None`, 'percent', or 'number'")

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
        return canvas.as_str()
    
    # Allow the user to hide the vertical stroke
    if stroke_color is None:
        stroke_color = "#FFFFFF00"

    def _make_bar(val: int, max_val: int) -> str:
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
            lambda x, m=max(full_col): _make_bar(x, max_val=m),
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
