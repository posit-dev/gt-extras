from __future__ import annotations
import warnings

from great_tables import GT
from great_tables._tbl_data import SelectExpr, is_na
from great_tables._locations import resolve_cols_c

from great_tables._data_color.base import _rescale_numeric

__all__ = ["_validate_and_get_single_column", "_scale_numeric_column"]


def _validate_and_get_single_column(
    gt: GT,
    expr: SelectExpr,
) -> tuple[str, list]:
    """
    Validate that expr resolves to a single column and return the column name and values.

    Parameters
    ----------
    gt
        The GT object containing the data
    expr
        The column expression to resolve

    Returns
    -------
    tuple[str, list]
        A tuple of (column_name, column_values)

    Raises
    ------
    KeyError
        If the column is not found
    ValueError
        If multiple columns are resolved
    """
    col_names = resolve_cols_c(data=gt, expr=expr)

    if len(col_names) == 0:
        raise KeyError(f"Column '{expr}' not found in the table.")
    if len(col_names) > 1:
        raise ValueError(
            f"Expected a single column, but got multiple columns: {col_names}"
        )

    col_name = col_names[0]
    col_vals = gt._tbl_data[col_name].to_list()

    return col_name, col_vals


def _scale_numeric_column(
    data_table,
    col_name: str,
    col_vals: list,
    domain: list[int] | list[float] | None = None,
    default_domain_min_zero: bool = True,
) -> list[float]:
    """
    Process and scale a numeric column, handling NA values.

    Parameters
    ----------
    data_table
        The underlying data table
    col_name
        Name of the column (for error messages)
    col_vals
        The column values
    domain
        The domain for scaling. If None, uses a default domain, based on `default_domain_min_zero`
    default_domain_min_zero
        If true, the defsult domain will be [0, max(values)], otherwise [min(values), max(values)]
    Returns
    -------
    list[float]
        Scaled values with NAs mapped to 0, values above the domains mapped to 1,
        and values below the domain mapped to 0.

    Raises
    ------
    TypeError
        If the column is not numeric
    """
    col_vals_filtered = [x for x in col_vals if not is_na(data_table, x)]

    # Check that column has numeric data
    if len(col_vals_filtered) and all(
        isinstance(x, (int, float)) for x in col_vals_filtered
    ):
        # If `domain` is not provided, then set it to a default domain
        if domain is None:
            if default_domain_min_zero:
                domain = [0, max(col_vals_filtered)]
            else:
                domain = [min(col_vals_filtered), max(col_vals_filtered)]

        # Rescale based on the given domain
        scaled_vals = _rescale_numeric(df=data_table, vals=col_vals, domain=domain)
    else:
        raise TypeError(
            f"Invalid column type provided ({col_name}). Please ensure that the column is numeric."
        )

    # Map scaled values back to original positions, using 0 for NAs
    scaled_vals_fixed = []
    for orig_val, scaled_val in zip(col_vals, scaled_vals):
        if is_na(data_table, orig_val):
            scaled_vals_fixed.append(0)
        elif is_na(data_table, scaled_val):
            # If original value < domain[0], set to 0; if > domain[1], set to 1
            if orig_val < min(domain):
                warnings.warn(
                    f"Value {orig_val} in column '{col_name}' is less than the domain minimum {min(domain)}. Setting to {min(domain)}.",
                    category=UserWarning,
                )
                scaled_vals_fixed.append(0)
            else:
                warnings.warn(
                    f"Value {orig_val} in column '{col_name}' is greater than the domain maximum {max(domain)}. Setting to {max(domain)}.",
                    category=UserWarning,
                )
                scaled_vals_fixed.append(1)
        else:
            scaled_vals_fixed.append(scaled_val)

    return scaled_vals_fixed
