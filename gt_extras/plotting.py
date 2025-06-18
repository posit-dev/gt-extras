from __future__ import annotations
from typing import Literal

from great_tables import GT, style, loc
from great_tables._tbl_data import SelectExpr
from great_tables._locations import resolve_cols_c

__all__ = ["gt_plt_bar"]


def gt_plt_bar(
    gt: GT,
    columns: SelectExpr | None = None, # Better to have no default?
    color: str = "purple",
    keep_columns: bool = False,
    width: int = 40,
    scale_type: str | None = None,
    text_color: str = "white",
) -> GT:
    
    # Get names of columns
    columns_resolved = resolve_cols_c(data=gt, expr=columns)

    if keep_columns:
        for column in columns_resolved:
            pass

    # Have to loop because fmt_nanoplot only supports single columns
    for column in columns_resolved:
        gt = gt.fmt_nanoplot(columns=column, plot_type="bar")

    return gt
