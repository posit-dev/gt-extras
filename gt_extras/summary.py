from __future__ import annotations

import math
import statistics

import narwhals.stable.v1 as nw
from faicons import icon_svg
from great_tables import GT, loc, style
from great_tables._tbl_data import is_na
from narwhals.stable.v1.typing import IntoDataFrame, IntoDataFrameT
from svg import SVG, Element, Line, Rect

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
        .cols_align(align="center", columns="Values")
    )

    for i, vals in enumerate(nw_summary_df.get_column("Values")):
        col_type = nw_summary_df.item(row=i, column="Type")
        gt = gt.fmt(
            lambda _, vals=vals, col_type=col_type: _make_summary_plot(
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


def _make_summary_plot(
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


def _plot_categorical(data: list[str]) -> str:
    raise NotImplementedError


def _plot_numeric(data: list[float] | list[int]) -> str:
    # Calculate binwidth using Freedman-Diaconis rule
    quantiles = statistics.quantiles(data, method="inclusive")
    q25, median, q75 = quantiles
    iqr = q75 - q25
    bw = 2 * iqr / (len(data) ** (1 / 3))

    if bw <= 0:
        bw = (max(data) - min(data)) / 3  # Fallback

    data_min, data_max = min(data), max(data)
    data_range = data_max - data_min

    if data_range == 0:
        # TODO: handle special case
        pass

    n_bins = max(1, int(math.ceil(data_range / bw)))

    # Do we need bin edges?
    # bin_edges = [data_min + i * data_range / n_bins for i in range(n_bins + 1)]

    counts = [0.0] * n_bins
    for x in data:
        # Handle edge case where x == data_max
        if x == data_max:
            counts[-1] += 1
        else:
            # Find the bin index for x
            bin_idx = int((x - data_min) / data_range * n_bins)
            counts[bin_idx] += 1

    max_count = max(counts)
    normalized_counts = [c / max_count for c in counts] if max_count > 0 else counts
    normalized_median = (median - data_min) / data_range

    svg = _make_histogram_svg(
        width_px=180,  # TODO choose how to assign
        height_px=40,
        median=normalized_median,
        counts=normalized_counts,
        fill="#f18e2c",
    )

    return svg.as_str()


def _make_histogram_svg(
    width_px: float,
    height_px: float,
    median: float,  # Relative to min and max in range
    counts: list[float],
    fill: str,
) -> SVG:
    count = len(counts)
    max_bar_height_px = height_px * 0.9  # can change
    plot_width_px = width_px * 0.9

    gap = (plot_width_px / count) * 0.1  # set max and min as well
    bin_width_px = plot_width_px / (count)

    y_loc = height_px / 2 + max_bar_height_px / 2
    x_loc = width_px / 2 - plot_width_px / 2

    line_stroke_width = max_bar_height_px / 30  # ensure never less than 1
    median_px = median * plot_width_px + x_loc

    elements: list[Element] = [
        # Bottom line
        Line(
            x1=0,
            x2=width_px,
            y1=y_loc,
            y2=y_loc,
            stroke="black",
            stroke_width=line_stroke_width,
        ),
        # Median line
        Line(
            x1=median_px,
            x2=median_px,
            y1=y_loc - line_stroke_width / 2,
            y2=y_loc - max_bar_height_px - line_stroke_width / 2,
            stroke="black",
            stroke_width=line_stroke_width,
        ),
    ]

    for val in counts:
        bar_height = val / 1 * max_bar_height_px
        bar = Rect(
            y=y_loc - bar_height - line_stroke_width / 2,
            x=x_loc + gap / 2,
            width=bin_width_px - gap,
            height=bar_height,
            fill=fill,
        )
        # elements = [bar] + elements
        elements.insert(0, bar)
        x_loc += bin_width_px

    return SVG(height=height_px, width=width_px, elements=elements)


def _plot_datetime(data: list) -> str:
    raise NotImplementedError
