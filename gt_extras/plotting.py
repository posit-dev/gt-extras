from __future__ import annotations
from great_tables import GT, nanoplot_options
from great_tables._tbl_data import SelectExpr
from great_tables._locations import resolve_cols_c

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
    width: int = 40,
    # scale_type: str | None = None,
    # text_color: str = "white",
) -> GT:
    """
    The `gt_plt_bar()` function takes an existing `gt` object and adds horizontal barplots via
    `GT.fmt_nanoplot()`.
    """
    # Get names of columns
    columns_resolved = resolve_cols_c(data=gt, expr=columns)

    # if keep_columns:
    #     for column in columns_resolved:
    #         pass

    # Have to loop because fmt_nanoplot only supports single columns
    for column in columns_resolved:
        gt = gt.fmt_nanoplot(
            columns=column,
            plot_type="bar",
            plot_height=width,
            options=nanoplot_options(
                data_bar_fill_color=color,
                data_bar_negative_fill_color=color,
                data_bar_negative_stroke_width="0",  # this can't be an int on account of a bug in fmt_nanoplot
                data_bar_stroke_width=0,
            ),
        )

    return gt
