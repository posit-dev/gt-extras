from __future__ import annotations

import os
import statistics
import tempfile

import narwhals.stable.v1 as nw
import pandas as pd
from faicons import icon_svg
from great_tables import GT, loc, style
from great_tables._tbl_data import is_na
from narwhals.stable.v1.typing import IntoDataFrame, IntoDataFrameT
from plotnine import (
    aes,
    element_line,
    element_text,
    expand_limits,
    geom_histogram,
    geom_vline,
    ggplot,
    scale_x_continuous,
    scale_y_continuous,
    theme,
    theme_void,
)

from gt_extras.themes import gt_theme_espn

__all__ = ["gt_plt_summary"]


def gt_plt_summary(df: IntoDataFrame, title: str | None = None) -> GT:
    summary_df = _create_summary_df(df)

    nw_df = nw.from_native(df, eager_only=True)
    dim_df = nw_df.shape

    nw_summary_df = nw.from_native(summary_df, eager_only=True)
    numeric_cols = [
        i
        for i, t in enumerate(nw_summary_df.get_column("Type").to_list())
        if t in ("numeric", "boolean")
    ]

    if title is None:
        # TODO: check that this gets name?
        _title = getattr(df, "__name__", "Summary Table")
    else:
        _title = title

    subtitle = f"{dim_df[0]} rows x {dim_df[1]} cols"

    gt = (
        GT(summary_df)
        .tab_header(title=_title, subtitle=subtitle)
        # handle missing
        .sub_missing(columns=["Mean", "Median", "SD"])
        # Add visuals
        .fmt(_make_icon_html, columns="Type")
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

    for i, vals in enumerate(nw_summary_df.get_column("Values")):
        col_type = nw_summary_df.item(row=i, column="Type")
        gt = gt.fmt(
            lambda _, vals=vals, col_type=col_type: _make_summary_plot_plotnine(
                gt=gt,  # TODO: dont pass gt
                data=vals,
                col_type=col_type,
            ),
            columns="Values",
            rows=i,
        )

    return gt


############### Helpers for gt_plt_summary ###############


def _create_summary_df(df: IntoDataFrameT) -> IntoDataFrameT:
    nw_df = nw.from_native(df, eager_only=True)

    summary_data = {
        "Type": [],
        "Column": [],
        "Values": [],
        "Missing": [],
        "Mean": [],
        "Median": [],
        "SD": [],
    }

    for col_name in nw_df.columns:
        col = nw_df.get_column(col_name)

        mean_val = None
        median_val = None
        std_val = None
        values = None

        if col.dtype.is_numeric():
            col_type = "numeric"
            mean_val = col.mean()
            median_val = col.median()
            std_val = col.std()
            values = col.to_list()

        elif col.dtype == nw.String:
            col_type = "string"
            values = col.to_list()

        elif col.dtype == nw.Boolean:
            col_type = "boolean"
            mean_val = col.mean()  # Proportion of True values
            values = col.to_list()

        elif col.dtype == nw.Datetime:
            col_type = "datetime"
            std_val = None
            values = col.to_list()

        else:
            col_type = "other"

        summary_data["Type"].append(col_type)
        summary_data["Column"].append(col_name)
        summary_data["Values"].append(values)
        summary_data["Missing"].append(col.null_count() / col.count())
        summary_data["Mean"].append(mean_val)
        summary_data["Median"].append(median_val)
        summary_data["SD"].append(std_val)

    summary_nw_df = nw.from_dict(summary_data, backend=nw_df.implementation)
    return summary_nw_df.to_native()


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
    elif dtype == "boolean":
        fa_name = "check"
        color = "black"
    else:
        fa_name = "question"
        color = "red"

    icon = icon_svg(name=fa_name, fill=color, width=f"{20}px", a11y="sem")

    # Return HTML for Font Awesome icon
    return str(icon)


def _make_summary_plot_plotnine(
    gt: GT,
    data: list,
    col_type: str,
) -> str:
    total = len(data)
    missing = (
        sum(1 for x in data if is_na(gt._tbl_data, x)) / total if total > 0 else 1.0
    )

    # If mostly missing, return empty div
    if missing >= 0.99:
        return "<div></div>"

    clean_data = [x for x in data if not is_na(gt._tbl_data, x)]

    if not clean_data:
        return "<div></div>"

    # TODO: add boolean
    if col_type == "string":
        return "<div></div>"
        # return _plot_categorical(clean_data)
    elif col_type == "numeric":
        return _plot_numeric(clean_data)
    elif col_type == "datetime":
        return _plot_datetime(clean_data)
    else:
        return "<div></div>"


# def _plot_categorical(data: list[str]) -> str:
#     # Count occurrences
#     df = pd.DataFrame({"vals": data})
#     counts = df["vals"].value_counts()
#     n_unique = len(counts)

#     # Create color palette (light to dark blue)
#     colors = ["red", "blue", "green"]
#     # for i in range(n_unique):
#     #     intensity = 0.2 + (0.8 * i / max(1, n_unique - 1))  # From light to dark
#     #     colors.append(f"rgba(49, 129, 189, {intensity})")

#     plot_df = pd.DataFrame({"vals": counts.index, "count": counts.values, "y": 1})
#     print(plot_df)
#     plot_df["vals"] = pd.Categorical(
#         plot_df["vals"], categories=counts.index[::-1], ordered=True
#     )

#     plot = ggplot(plot_df, aes(y="y", fill="vals")) + geom_bar(
#         position="fill", width=0.8
#     )

#     return _save_plot_as_svg(plot)


def _plot_numeric(data: list[float]) -> str:
    df = pd.DataFrame({"x": data})

    # Calculate binwidth using Freedman-Diaconis rule
    quantiles = statistics.quantiles(data)
    q25, q75 = quantiles[0], quantiles[2]
    iqr = q75 - q25
    bw = 2 * iqr / (len(data) ** (1 / 3))

    if bw <= 0:
        bw = (max(data) - min(data)) / 30  # Fallback

    data_range = [min(data), max(data)]

    plot = (
        ggplot(df, aes(x="x"))
        + geom_histogram(color="white", fill="#f8bb87", binwidth=bw)
        + scale_x_continuous(
            breaks=data_range, labels=[f"{x:,.0f}" for x in data_range]
        )
        + scale_y_continuous(expand=(0, 0))
        + theme_void()
        + theme(
            axis_text_x=element_text(color="black", vjust=-2, size=6),
            axis_line_x=element_line(color="black"),
            axis_ticks_major_x=element_line(color="black"),
            # plot_margin=margin(1, 1, 3, 1, "mm"),
        )
        + expand_limits()
    )

    # Add median line if more than 2 unique values
    if len(set(data)) > 2:
        median_val = statistics.median(data)
        plot += geom_vline(xintercept=median_val, color="black")

    return _save_plot_as_svg(plot)


def _plot_datetime(data: list) -> str:
    dates = pd.to_datetime(data)
    df = pd.DataFrame({"x": dates})

    # Calculate binwidth for dates (in days)
    date_range = (dates.max() - dates.min()).days
    if date_range > 365:
        bins = 30  # Monthly bins
    elif date_range > 30:
        bins = date_range // 7  # Weekly bins
    else:
        bins = max(5, date_range)  # Daily bins

    plot = (
        ggplot(df, aes(x="x"))
        + geom_histogram(color="white", fill="#73a657", bins=bins)
        # + scale_x_continuous(
        #     breaks=[dates.min(), dates.max()],
        #     labels=[d.strftime("%Y-%m-%d") for d in [dates.min(), dates.max()]],
        # )
        + theme_void()
        + theme(
            axis_text_x=element_text(color="black", vjust=-2, size=6),
            axis_line_x=element_line(color="black"),
            axis_ticks_major_x=element_line(color="black"),
            # plot_margin=margin(1, 1, 3, 1, "mm"),
        )
    )

    return _save_plot_as_svg(plot)


def _save_plot_as_svg(plot: ggplot) -> str:
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Save plot
        plot.save(tmp_path, dpi=25, height=12, width=50, units="mm", format="svg")

        # Read SVG content
        with open(tmp_path, "r") as f:
            svg_content = f.read()

        return svg_content

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
