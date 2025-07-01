from __future__ import annotations
from typing import Literal

from great_tables import GT, style, loc
from great_tables._tbl_data import SelectExpr


__all__ = ["gt_add_divider"]


def gt_add_divider(
    gt: GT,
    columns: SelectExpr,
    sides: Literal["right", "left", "top", "bottom", "all"]
    | list[Literal["right", "left", "top", "bottom", "all"]] = "right",
    color: str = "grey",
    divider_style: Literal["solid", "dashed", "dotted", "hidden", "double"] = "solid",
    weight: int = 2,
    include_labels: bool = True,
) -> GT:
    locations = [
        loc.body(
            columns=columns,
        )
    ]

    if include_labels:
        locations.append(loc.column_labels(columns=columns))

    res = gt.tab_style(
        style=style.borders(
            sides=sides,
            color=color,
            weight=weight,
            style=divider_style,
        ),
        locations=locations,
    )

    return res
