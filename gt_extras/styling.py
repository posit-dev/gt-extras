from __future__ import annotations
from typing import Literal

from great_tables import GT, style, loc
from great_tables._tbl_data import SelectExpr


__all__ = ["gt_add_divider"]


def gt_add_divider(
    gt: GT,
    columns: SelectExpr,
    sides: (
        Literal["right", "left", "top", "bottom", "all"]
        | list[Literal["right", "left", "top", "bottom", "all"]]
    ) = "right",
    color: str = "grey",
    divider_style: Literal["solid", "dashed", "dotted", "hidden", "double"] = "solid",
    weight: int = 2,
    include_labels: bool = True,
) -> GT:
    """
    Add dividers to specified columns in a GT table.

    The `gt_add_divider()` function takes an existing `GT` object and adds dividers to the specified
    columns. Dividers can be applied to one or more sides of the cells, with customizable color,
    style, and weight. Optionally, dividers can also be applied to column labels.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    columns
        The columns to which dividers should be applied.

    sides
        The sides of the cells where dividers should be added. Options include `"right"`, `"left"`,
        `"top"`, `"bottom"`, or `"all"`. A list of sides can also be provided to apply dividers to
        multiple sides.

    color
        The color of the dividers.

    divider_style
        The style of the dividers. Options include `"solid"`, `"dashed"`, `"dotted"`, `"hidden"`,
        and `"double"`.

    weight
        The thickness of the dividers in pixels.

    include_labels
        Whether to include dividers in the column labels. If `True`, dividers will be applied to
        both the body and the column labels. If `False`, dividers will only be applied to the body.

    Returns
    -------
    GT
        A `GT` object with dividers added to the specified columns.

    Examples
    --------
    ```{python}
    import pandas as pd
    from great_tables import GT
    from great_tables.data import peeps
    import gt_extras as gte

    peeps_mini = peeps.head(6)

    gt = (
        GT(peeps_mini)
        .cols_hide([
            "name_family", "postcode", "country", "country_code",
            "dob", "gender", "state_prov", "email_addr",
        ])
        .tab_spanner("Location", ["address", "city"])
        .tab_spanner("Body Measurements", ["height_cm", "weight_kg"])
    )

    gt.pipe(
        gte.gt_add_divider,
        columns="name_given",
        color="#FFB90F",
        divider_style="double",
        weight=8,
    ).pipe(
        gte.gt_add_divider,
        columns="phone_number",
        color="purple",
        sides=["right", "left"],
        weight=5,
    )
    ```
    """

    locations = [loc.body(columns=columns)]

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
