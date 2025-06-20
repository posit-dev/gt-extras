from __future__ import annotations
from great_tables import GT
from great_tables._tbl_data import SelectExpr
from great_tables._locations import resolve_cols_c

from svg import SVG, Line, Rect

# import io

# from plotnine import (
#     ggplot,
#     geom_hline,
#     aes,
#     geom_col,
#     scale_x_continuous,
#     scale_y_continuous,
#     coord_flip,
#     theme_void,
# )

__all__ = ["gt_plt_bar"]

# TODO: keep_columns - this is tricky because we can't copy cols in the gt object, so we will have
# to handle the underlying _tbl_data.

# TODO: make sure numeric type passed in?


def gt_plt_bar(
    gt: GT,
    columns: SelectExpr | None = None,
    fill: str = "purple",
    bar_height: int = 20,
    width: int = 60,
    height: int = 30,
    stroke_color: str = "black",
    # keep_columns: bool = False,
    # scale_type: str | None = None,
    # text_color: str = "white",
) -> GT:
    """
    The `gt_plt_bar()` function takes an existing `gt` object and adds horizontal barplots via svg.py`.
    """

    # A version with svg.py
    def _make_bar_html(
        val: int,
        fill: str,
        bar_height: int,
        height: int,
        width: int,
        max_val: int,
        stroke_color: str,
    ) -> str:
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

    def make_bar(val: int, max_val: int) -> str:
        return _make_bar_html(
            val=val,
            fill=fill,
            bar_height=bar_height,
            height=height,
            width=width,
            max_val=max_val,
            stroke_color=stroke_color,
        )

    # Get names of columns
    columns_resolved = resolve_cols_c(data=gt, expr=columns)

    res = gt
    for column in columns_resolved:
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
