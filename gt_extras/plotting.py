from __future__ import annotations
from great_tables import GT
from great_tables._tbl_data import SelectExpr

# from great_tables._locations import resolve_cols_c
import io

from plotnine import (
    ggplot,
    geom_hline,
    aes,
    geom_col,
    scale_x_continuous,
    scale_y_continuous,
    coord_flip,
    theme_void,
)

__all__ = ["gt_plt_bar"]

# TODO: At a high level, should I be writing more of the plotting myself?
# That's what's happening in gtExtras, with ggplot.

# TODO: keep_columns - this is tricky because we can't copy cols in the gt object, so we will have
# to handle the underlying _tbl_data.

# TODO: scale_type and text_color can't be implemented by simply wrapping fmt_nanoplot


def gt_plt_bar(
    gt: GT,
    columns: SelectExpr | None = None,  # Better to have no default?
    color: str = "purple",
    # keep_columns: bool = False,
    # width: int | None = None,
    height: int = 0.5,
    # scale_type: str | None = None,
    # text_color: str = "white",
) -> GT:
    """
    The `gt_plt_bar()` function takes an existing `gt` object and adds horizontal barplots via
    `GT.fmt_nanoplot()`.
    """
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

    def _make_bar_html(val: int, fill: str, height: int) -> str:
        plot = (
            ggplot()
            + aes(
                x=1,
                y=val,
            )
            + geom_hline(yintercept=0)
            + geom_col(width=height, fill=fill, show_legend=False)
            + scale_y_continuous(limits=(0, 1))
            + scale_x_continuous(limits=(0.5, 1.5))
            + coord_flip()
            + theme_void()
        )

        buf = io.StringIO()
        plot.save(buf, format="svg", dpi=96, width=0.5, height=0.5)
        buf.seek(0)
        svg_content = buf.getvalue()
        buf.close()

        html = f"<div>{svg_content}</div>"
        return html

    def make_bar(val: int) -> str:
        print("calling mbh ", val, color, height)
        return _make_bar_html(val=val, fill=color, height=height)

    res = gt.fmt(make_bar, columns=columns)

    return res
