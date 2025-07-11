from __future__ import annotations

import narwhals.stable.v1 as nw
from great_tables import GT
from great_tables._gt_data import Boxhead, ColInfo
from great_tables._tbl_data import SelectExpr, is_na

from gt_extras._utils_column import _validate_and_get_single_column

__all__ = ["fmt_pct_extra", "gt_duplicate_column"]


def fmt_pct_extra(
    gt: GT,
    columns: SelectExpr,
    scale: float = 100,
    threshold: float = 1.0,
    color: str = "grey",
    decimals: int = 1,
) -> GT:
    # TODO: would we want to infer the range? (as we do in gt_plt_bar_pct)
    """
    Convert to percent and show less than `1%` as `<1%` in grey.

    The `fmt_pct_extra()` function takes an existing `GT` object and formats a column of numeric
    values as percentages. Values below the specified threshold are displayed as `"<threshold%"`
    instead of their actual percentage value, and in a color of your choosing. The default behavior
    expects values in the range `[0, 1]`, use `scale` if your values are in a different range.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    columns
        The columns containing numeric values to format as percentages.

    scale
        Multiplication factor to convert values to percentages. For some common cases:
        use `100` if values are decimals `(0.05 -> 5%)` (default),
        use `1` if values are already percentages `(5 -> 5%)`.

    threshold
        The percentage threshold below which values are displayed as `"<threshold%"` instead of
        their actual value. Note this refers to the scaled value, not the original, so you will
        have to provide `5` for `<5%` even if your original are in the range `[0,1]`.

    color
        The color to use for values below the threshold.

    decimals
        Number of decimal places to display for percentages.

    Returns
    -------
    GT
        A `GT` object with formatted percentage column.

    Examples
    --------
    ```{python}
    from great_tables import GT
    from great_tables.data import towny
    import gt_extras as gte

    towny_mini = towny[
        [
            "name",
            "pop_change_1996_2001_pct",
            "pop_change_2001_2006_pct",
            "pop_change_2006_2011_pct",
        ]
    ].tail(10)

    gt = (
        GT(towny_mini)
        .tab_spanner(label="Population Change", columns=[1, 2, 3])
        .cols_label(
            pop_change_1996_2001_pct="'96-'01",
            pop_change_2001_2006_pct="'01-'06",
            pop_change_2006_2011_pct="'06-'11",
        )
    )

    gt.pipe(
        gte.fmt_pct_extra,
        columns=[1, 2, 3],
        threshold=5,
        color="green",
    )
    ```
    """
    # TODO: consider how to handle negative values

    def _fmt_pct_single_val(value: float):
        if is_na(gt._tbl_data, value):
            return ""

        # Convert to percentage
        pct_value = value * scale

        if abs(pct_value) < threshold:
            return f"<span style='color:{color};'><{threshold:g}%</span>"
        else:
            return f"{pct_value:.{decimals}f}%"

    res = gt
    res = res.fmt(_fmt_pct_single_val, columns=columns)

    return res


def gt_duplicate_column(
    gt: GT,
    column: SelectExpr,
    after: str | None = None,
    append_text: str | None = "_dupe",
    dupe_name: str | None = None,
) -> GT:
    """
    Duplicate a column in a `GT` object.

    The `gt_duplicate_column()` function takes an existing `GT` object and creates a duplicate
    (without styling) of the specified column. The duplicated column can be renamed using either
    `dupe_name` or by appending text to the original column name, and positioned at a
    specific location in the table.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    column
        The column to duplicate. Can be a column name or index.

    after
        The column after which to place the duplicated column. If `None`, the duplicated
        column will be moved to the end of the table.

    append_text
        Text to append to the original column name for the duplicate. Only used if
        `dupe_name` is not provided. Defaults to `"_dupe"`.

    dupe_name
        The name for the duplicated column. If provided, this overrides `append_text`.

    Returns
    -------
    GT
        A `GT` object with the duplicated column added.

    Examples
    --------
    ```{python}
    from great_tables import GT
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["mfr", "model", "year", "hp"]].head(5)
    gt = GT(gtcars_mini)

    # Duplicate with custom name and position
    gt.pipe(
        gte.gt_duplicate_column,
        column="hp",
        after="year",
    )
    ```
    """
    original_name, _ = _validate_and_get_single_column(gt, column)

    # If dupe_name is given, it overrides append_text
    append_text = append_text or "_dupe"
    if dupe_name is not None:
        new_col_name = dupe_name
    else:
        new_col_name = original_name + append_text

    if new_col_name == original_name:
        raise ValueError(
            f"The new column name '{new_col_name}' cannot be the same as the original column name '{original_name}'."
        )

    res = gt
    new_data_table = res._tbl_data
    new_body = res._body

    # get the boxhead info
    original_col_info = None
    for col_info in res._boxhead:
        if col_info.var == original_name:
            original_col_info = col_info
            break

    # make the new boxhead entry
    new_col_info = ColInfo(
        var=new_col_name,
        type=original_col_info.type,
        column_label=new_col_name,
        column_align=original_col_info.column_align,
        column_width=original_col_info.column_width,
    )

    new_data_table = nw.to_native(
        nw.from_native(new_data_table).with_columns(
            nw.col(original_name).alias(new_col_name)
        )
    )

    new_body.body = nw.to_native(
        nw.from_native(new_body.body).with_columns(
            nw.col(original_name).alias(new_col_name)
        )
    )

    new_boxhead_list = list(res._boxhead._d) + [new_col_info]
    new_boxhead = Boxhead(new_boxhead_list)

    res = res._replace(_tbl_data=new_data_table, _boxhead=new_boxhead, _body=new_body)

    if after is None:
        res = res.cols_move_to_end(new_col_name)
    else:
        res = res.cols_move(new_col_name, after=after)

    return res
