from __future__ import annotations

from great_tables import GT
from great_tables._tbl_data import SelectExpr, is_na

__all__ = ["fmt_pct_extra"]


def fmt_pct_extra(
    gt: GT,
    columns: SelectExpr,
    scale: float = 100,
    threshold: float = 1.0,
    color: str = "grey",
    decimals: int = 1,
) -> GT:
    """
    Convert to percent and show less than `1%` as `<1%` in grey.

    The `fmt_pct_extra()` function takes an existing `GT` object and formats a column of numeric
    values as percentages. Values below the specified threshold are displayed as `"<threshold%"`
    instead of their actual percentage value, and in a unique color.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    columns
        The columns containing numeric values to format as percentages.

    scale
        Multiplication factor to convert values to percentages.
        Use `100` if values are decimals `(0.05 -> 5%)` (default),
        use `1` if values are already percentages `(5 -> 5%)`.

    threshold
        The percentage threshold below which values are displayed as `"<threshold%"` instead of
        their actual value. Note this refers to the scaled value, not the original.

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

    return gt.fmt(_fmt_pct_single_val, columns=columns)
