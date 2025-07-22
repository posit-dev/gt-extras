from __future__ import annotations

import narwhals.stable.v1 as nw
import polars as pl
from faicons import icon_svg
from great_tables import GT, loc, style
from narwhals.stable.v1.typing import IntoDataFrame

from gt_extras.themes import gt_theme_espn

__all__ = ["gt_plt_summary"]


def gt_plt_summary(df: IntoDataFrame, title: str | None = None) -> GT:
    gt = _create_summary_table(df=df)

    nw_df = nw.from_native(df, eager_only=True)
    dim_df = nw_df.shape  # (n_rows, n_cols)

    # TODO: also fix for no polars
    numeric_cols = pl.col("Type") == "numeric"

    if title is None:
        _title = getattr(df, "__name__", "Summary Table")
    else:
        _title = title

    subtitle = f"{dim_df[0]} rows x {dim_df[1]} cols"

    gt = (
        gt.tab_header(title=_title, subtitle=subtitle)
        # handle missing
        .sub_missing(columns=["Mean", "Median", "SD"])
        # Add visuals
        .fmt(_make_icon_html, columns="Type")
        .fmt(_make_summary_plot_plotnine, columns="Values")
        # Format numerics
        .fmt_percent(columns="Missing", decimals=1)
        .fmt_number(columns=["Mean", "Median", "SD"], rows=numeric_cols)  # type: ignore
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(columns="Column"),
        )
        # add style
        .pipe(gt_theme_espn)
    )

    return gt


############### Helpers for gt_plt_summary ###############


def _create_summary_table(df: IntoDataFrame) -> GT:
    nw_df = nw.from_native(df, eager_only=True)

    summary_data = []

    for col_name in nw_df.columns:
        col = nw_df.get_column(col_name)

        mean_val = None
        median_val = None
        std_val = None

        if col.dtype.is_numeric():
            col_type = "numeric"
            mean_val = col.mean()
            median_val = col.median()
            std_val = col.std()
        elif col.dtype == nw.String:
            col_type = "string"

        elif col.dtype == nw.Boolean:
            col_type = "boolean"
            mean_val = col.mean()  # Proportion of True values

        elif col.dtype == nw.Datetime:
            col_type = "datetime"
            std_val = None
        else:
            col_type = "other"

        summary_data.append(
            {
                "Type": col_type,
                "Column": col_name,
                "Values": col.to_list(),
                "Missing": col.null_count() / col.count(),
                "Mean": mean_val,
                "Median": median_val,
                "SD": std_val,
            }
        )

    ## TODO: Avoid polars?
    summary_nw_df = pl.DataFrame(summary_data)

    return GT(summary_nw_df)


def _make_icon_html(dtype: str) -> str:
    if dtype == "string":
        fa_name = "list"
        color = "#4e79a7"
    elif dtype == "numeric":
        fa_name = "signal"
        color = "#f18e2c"
    elif dtype == "datetime":
        fa_name = "clock"
        color = "#73a657"
    else:
        fa_name = "question"
        color = "black"

    icon = icon_svg(name=fa_name, fill=color, width=f"{20}px", a11y="sem")

    # Return HTML for Font Awesome icon
    return str(icon)


def _make_summary_plot_plotnine(
    data: list[str] | list[int] | list[float] | list[nw.Datetime],
) -> str:
    return "temp plot"
