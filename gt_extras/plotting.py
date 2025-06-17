from __future__ import annotations
from typing import Literal

from great_tables import GT, style, loc
from great_tables._tbl_data import SelectExpr

__all__ = ["gt_plt_bar"]


def gt_plt_bar(
    gt: GT,
    column: SelectExpr, # Best is no default?
    color: str = "purple",
    keep_column: bool = False,
    width: int = 40,
    scale_type: str | None = None,
    text_color: str = "white",
) -> GT:

    # TODO: ensure column has length 1, since SelectExpr can be longer

    res = gt

    return res
