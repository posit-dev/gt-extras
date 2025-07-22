from __future__ import annotations

from great_tables import GT
from narwhals.stable.v1.typing import IntoFrame

__all__ = ["gt_plt_summary"]


def gt_plt_summary(df: IntoFrame) -> GT:
    gt = GT(df)
    return gt
