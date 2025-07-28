from __future__ import annotations

import math
import statistics
from datetime import datetime, timedelta

import narwhals.stable.v1 as nw
from faicons import icon_svg
from great_tables import GT, loc, style
from great_tables._helpers import random_id
from narwhals.stable.v1.typing import IntoDataFrame, IntoDataFrameT
from svg import SVG, Element, G, Line, Rect, Style, Text

from gt_extras.themes import gt_theme_espn

__all__ = ["gt_plt_summary"]

COLOR_MAPPING = {
    "string": "#4e79a7",
    "numeric": "#f18e2c",
    "datetime": "#73a657",
    "boolean": "#A65773",
    "other": "black",
}
DEFAULT_WIDTH_PX = 180  # TODO choose how to assign dimensions
DEFAULT_HEIGHT_PX = 40
PLOT_WIDTH_RATIO = 0.95
PLOT_HEIGHT_RATIO = 0.8
FONT_SIZE_RATIO = 0.2  # height_px / 5


def gt_plt_summary(df: IntoDataFrame, title: str | None = None) -> GT:
    """
    Create a comprehensive data summary table with visualizations.

    The `gt_plt_summary()` function takes a DataFrame and generates a summary table showing key
    statistics and visual representations for each column. Each row displays the column type,
    missing data percentage, descriptive statistics (mean, median, standard deviation), and a
    small plot overview appropriate for the data type (histograms for numeric and datetime and
    a categorical bar chart for strings).

    Parameters
    ----------
    df
        A DataFrame to summarize. Can be any DataFrame type that you would pass into a `GT`.

    title
        Optional title for the summary table. If `None`, defaults to "Summary Table".

    Returns
    -------
    GT
        A `GT` object containing the summary table with columns for Type, Column name,
        Plot Overview, Missing percentage, Mean, Median, and Standard Deviation.

    Examples
    --------
    ```{python}
    import polars as pl
    from great_tables import GT
    import gt_extras as gte
    from datetime import datetime

    df = pl.DataFrame({
        "Date": [
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 7),
            datetime(2024, 1, 8),
            datetime(2024, 1, 13),
            datetime(2024, 1, 16),
            datetime(2024, 1, 20),
            datetime(2024, 1, 22),
            datetime(2024, 2, 1),
        ] * 5,
        "Value": [10, 15, 20, None, 25, 18, 22, 30, 40] * 5,
        "Category": ["A", "B", "C", "A", "B", "C", "D", None, None] * 5,
        "Boolean": [True, False, True] * 15,
        "Status": ["Active", "Inactive", None] * 15,
    })

    gte.gt_plt_summary(df)
    ```
    And an example with some satisfying numeric data:
    ```{python}
    import random

    n = 100
    random.seed(23)

    uniform = [random.uniform(0, 10) for _ in range(n)]
    for i in range(2, 10):
        uniform[i] = None

    normal = [random.gauss(5, 2) for _ in range(n)]
    normal[4] = None
    normal[10] = None

    single_tailed = [random.expovariate(1/2) for _ in range(n)]

    bimodal = [random.gauss(2, 0.5) for _ in range(n // 2)] + [random.gauss(8, 0.5) for _ in range(n - n // 2)]

    df = pl.DataFrame({
        "uniform": uniform,
        "normal": normal,
        "single_tailed": single_tailed,
        "bimodal": bimodal,
    })

    gte.gt_plt_summary(df)
    ```
    """
    summary_df = _create_summary_df(df)

    nw_df = nw.from_native(df, eager_only=True)
    dim_df = nw_df.shape

    nw_summary_df = nw.from_native(summary_df, eager_only=True)
    numeric_cols = [
        i
        for i, t in enumerate(nw_summary_df.get_column("Type").to_list())
        if t in ("numeric", "boolean")
    ]  # TODO: only assign boolean to mean

    if title is None:
        title = "Summary Table"

    subtitle = f"{dim_df[0]} rows x {dim_df[1]} cols"

    gt = (
        GT(summary_df)
        .tab_header(title=title, subtitle=subtitle)
        # handle missing
        .sub_missing(columns=["Mean", "Median", "SD"])
        # Add visuals
        .fmt(_make_icon_html, columns="Type")
        # Format numerics
        .fmt_percent(columns="Missing", decimals=1)
        .fmt_number(columns=["Mean", "Median", "SD"], rows=numeric_cols)
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(columns="Column"),
        )
        # add style
        .cols_align(align="center", columns="Plot Overview")
    )

    gt = gt_theme_espn(gt)

    for i, col_name in enumerate(nw_summary_df.get_column("Column")):
        vals = nw.from_native(df, eager_only=True).get_column(col_name)
        vals = _clean_series(vals, vals.dtype.is_numeric())

        col_type = nw_summary_df.item(row=i, column="Type")
        gt = gt.fmt(
            lambda _, vals=vals, col_type=col_type: _make_summary_plot(
                nw_series=vals,
                col_type=col_type,
            ),
            columns="Plot Overview",
            rows=i,
        )
    return gt


############### Helpers for gt_plt_summary ###############


def _create_summary_df(df: IntoDataFrameT) -> IntoDataFrameT:
    nw_df = nw.from_native(df, eager_only=True)  # Should I be concerned about this?

    summary_data = {
        "Type": [],
        "Column": [],
        "Plot Overview": [],
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

        clean_col = _clean_series(col, col.dtype.is_numeric())

        missing_count = len(col) - len(clean_col)
        missing_ratio = missing_count / len(col)

        if col.dtype.is_numeric():
            col_type = "numeric"
            mean_val = clean_col.mean()
            median_val = clean_col.median()
            std_val = clean_col.std()

        elif col.dtype == nw.String:
            col_type = "string"

        elif col.dtype == nw.Boolean:
            col_type = "boolean"
            mean_val = clean_col.mean()  # Proportion of True values

        elif col.dtype == nw.Datetime:
            col_type = "datetime"

        else:
            col_type = "other"

        summary_data["Type"].append(col_type)
        summary_data["Column"].append(col_name)
        summary_data["Plot Overview"].append(None)
        summary_data["Missing"].append(missing_ratio)
        summary_data["Mean"].append(mean_val)
        summary_data["Median"].append(median_val)
        summary_data["SD"].append(std_val)

    summary_nw_df = nw.from_dict(summary_data, backend=nw_df.implementation)
    return summary_nw_df.to_native()


def _make_icon_html(dtype: str) -> str:
    if dtype == "string":
        fa_name = "list"
        color = COLOR_MAPPING["string"]
    elif dtype == "numeric":
        fa_name = "signal"
        color = COLOR_MAPPING["numeric"]
    elif dtype == "datetime":
        fa_name = "clock"
        color = COLOR_MAPPING["datetime"]
    elif dtype == "boolean":
        fa_name = "check"
        color = COLOR_MAPPING["boolean"]
    else:
        fa_name = "question"
        color = COLOR_MAPPING["other"]

    icon = icon_svg(name=fa_name, fill=color, width=f"{20}px", a11y="sem")

    # Return HTML for Font Awesome icon
    return str(icon)


def _make_summary_plot(
    nw_series: nw.Series,
    col_type: str,
) -> str:
    if len(nw_series) == 0:
        return "<div></div>"

    clean_list = nw_series.to_native().to_list()

    # TODO: add boolean
    if col_type == "string":
        return _plot_categorical(clean_list)
    elif col_type == "numeric":
        return _plot_numeric(clean_list)
    elif col_type == "datetime":
        return _plot_datetime(clean_list)
    else:
        return "<div></div>"


def _plot_categorical(data: list[str]) -> str:
    category_counts = {}
    for item in data:
        if item in category_counts:
            category_counts[item] += 1
        else:
            category_counts[item] = 1

    # Sort by count (descending order)
    sorted_categories = sorted(
        category_counts.items(), key=lambda x: x[1], reverse=True
    )

    # Extract counts and calculate proportions
    counts = [count for _, count in sorted_categories]
    total_count = sum(counts)
    proportions = [count / total_count for count in counts]

    svg = _make_categories_bar_svg(
        width_px=DEFAULT_WIDTH_PX,
        height_px=DEFAULT_HEIGHT_PX,
        fill=COLOR_MAPPING["string"],
        proportions=proportions,
        categories=[
            category for category, _ in sorted_categories
        ],  # maybe leave combined with counts?
        counts=counts,
    )

    return svg.as_str()


def _make_categories_bar_svg(
    width_px: float,
    height_px: float,
    fill: str,
    proportions: list[float],
    categories: list[str],
    counts: list[int],
) -> SVG:
    plot_width_px = width_px * PLOT_WIDTH_RATIO
    plot_height_px = height_px * PLOT_HEIGHT_RATIO

    x_offset = (width_px - plot_width_px) / 2
    y_offset = (height_px - plot_height_px) / 2

    x_loc = x_offset
    font_size_px = height_px * FONT_SIZE_RATIO

    max_opacity = 1.0
    min_opacity = 0.2

    plot_id = random_id(10)

    hover_css = _generate_hover_css(
        num_elements=len(proportions),
        bar_highlight_style="opacity: 0.4;",
        tooltip_class="category-tooltip",
        use_hover_areas=False,
        plot_id=plot_id,
    )

    elements: list[Element] = [Style(text=hover_css)]

    for i, (proportion, category, count) in enumerate(
        zip(proportions, categories, counts)
    ):
        section_width = proportion * plot_width_px

        if len(proportions) == 1:
            opacity = max_opacity
        else:
            opacity = max_opacity - (max_opacity - min_opacity) * (
                i / (len(proportions) - 1)
            )

        # Use plot_id in element IDs and classes
        bar_id = f"{plot_id}-bar-{i}" if plot_id else f"bar-{i}"
        visual_bar_class = f"{plot_id}-visual-bar" if plot_id else "visual-bar"

        visual_bar = Rect(
            id=bar_id,
            class_=[visual_bar_class],
            x=x_loc,
            y=y_offset,
            width=section_width,
            height=plot_height_px,
            fill=fill,
            fill_opacity=opacity,
            stroke="transparent",
        )
        elements.insert(1, visual_bar)

        section_center_x = x_loc + section_width / 2

        text_top = f"{count} rows"
        text_bottom = f'"{category}"'

        # Estimate text width
        max_text_width = max(
            len(text_top) * font_size_px * 0.6,
            len(text_bottom) * font_size_px * 0.6,
        )

        tooltip_x = _calculate_text_position(
            center_x=section_center_x,
            text_width=max_text_width,
            svg_width=width_px,
            margin=5,
        )

        # Use plot_id in tooltip ID and class
        tooltip_id = f"{plot_id}-tooltip-{i}"
        tooltip_class = f"{plot_id}-category-tooltip"

        tooltip = G(
            id=tooltip_id,
            class_=[tooltip_class],
            elements=[
                Text(
                    text=text_top,
                    x=tooltip_x,
                    y=font_size_px * 1.25,
                    fill="black",
                    font_size=font_size_px,
                    dominant_baseline="hanging",
                    text_anchor="middle",
                    font_weight="bold",
                ),
                Text(
                    text=text_bottom,
                    x=tooltip_x,
                    y=font_size_px * 2.5,
                    fill="black",
                    font_size=font_size_px,
                    dominant_baseline="hanging",
                    text_anchor="middle",
                    font_weight="bold",
                ),
            ],
        )
        elements.append(tooltip)
        x_loc += section_width

    return SVG(height=height_px, width=width_px, elements=elements)


def _plot_numeric(data: list[float] | list[int]) -> str:
    data_min, data_max = min(data), max(data)
    data_range = data_max - data_min

    if data_range == 0:
        data_min -= 1.5
        data_max += 1.5
        data_range = 3

    # after cleaning in _make_summary_plot, we know len(data) > 1
    if len(data) == 1:
        bw = 1
    # Calculate binwidth using Freedman-Diaconis rule
    else:
        quantiles = statistics.quantiles(data, method="inclusive")
        q25, _, q75 = quantiles
        iqr = q75 - q25
        bw = 2 * iqr / (len(data) ** (1 / 3))

    if bw <= 0:
        bw = data_range / 3  # Fallback

    n_bins = max(1, int(math.ceil(data_range / bw)))
    bin_edges = [data_min + i * data_range / n_bins for i in range(n_bins + 1)]
    bin_edges = [f"{edge:.2f}".rstrip("0").rstrip(".") for edge in bin_edges]

    counts = [0.0] * n_bins
    for x in data:
        # Handle edge case where x == data_max
        if x == data_max:
            counts[-1] += 1
        else:
            # Find the bin index for x
            bin_idx = int((x - data_min) / data_range * n_bins)
            counts[bin_idx] += 1

    normalized_mean = (statistics.mean(data) - data_min) / data_range

    svg = _make_histogram_svg(
        width_px=DEFAULT_WIDTH_PX,
        height_px=DEFAULT_HEIGHT_PX,
        fill=COLOR_MAPPING["numeric"],
        normalized_mean=normalized_mean,
        data_max=str(round(data_max, 2)),
        data_min=str(round(data_min, 2)),
        counts=counts,
        bin_edges=bin_edges,
    )

    return svg.as_str()


def _plot_datetime(
    dates: list[datetime],
) -> str:
    date_timestamps = [x.timestamp() for x in dates]
    data_min, data_max = min(date_timestamps), max(date_timestamps)
    data_range = data_max - data_min

    if data_range == 0:
        data_min -= timedelta(days=1.5).total_seconds()
        data_max += timedelta(days=1.5).total_seconds()
        data_range = data_max - data_min

    # after cleaning in _make_summary_plot, we know len(data) > 1
    if len(date_timestamps) == 1:
        bw = timedelta(days=1).total_seconds()
    # Calculate binwidth using Freedman-Diaconis rule
    else:
        quantiles = statistics.quantiles(date_timestamps, method="inclusive")
        # q25 = datetime.fromtimestamp(quantiles[0])
        # q75 = datetime.fromtimestamp(quantiles[2])
        q25, _, q75 = quantiles
        iqr = q75 - q25
        bw = 2 * iqr / (len(date_timestamps) ** (1 / 3))

    if bw <= 0:
        bw = data_range / 3  # Fallback

    n_bins = max(1, int(math.ceil(data_range / bw)))
    bin_edges = [data_min + i * data_range / n_bins for i in range(n_bins + 1)]
    bin_edges = [str(datetime.fromtimestamp(edge).date()) for edge in bin_edges]

    counts = [0.0] * n_bins
    for x in date_timestamps:
        # Handle edge case where x == data_max
        if x == data_max:
            counts[-1] += 1
        else:
            bin_idx = int((x - data_min) / data_range * n_bins)
            counts[bin_idx] += 1

    normalized_mean = (statistics.mean(date_timestamps) - data_min) / data_range

    svg = _make_histogram_svg(
        width_px=DEFAULT_WIDTH_PX,
        height_px=DEFAULT_HEIGHT_PX,
        fill=COLOR_MAPPING["datetime"],
        normalized_mean=normalized_mean,
        data_max=str(datetime.fromtimestamp(data_max).date()),
        data_min=str(datetime.fromtimestamp(data_min).date()),
        counts=counts,
        bin_edges=bin_edges,
    )

    return svg.as_str()


def _make_histogram_svg(
    width_px: float,
    height_px: float,
    fill: str,
    normalized_mean: float,
    data_min: str,
    data_max: str,
    counts: list[float],
    bin_edges: list[str],
) -> SVG:
    max_count = max(counts)
    normalized_counts = [c / max_count for c in counts] if max_count > 0 else counts

    len_counts = len(normalized_counts)
    plot_width_px = width_px * PLOT_WIDTH_RATIO
    max_bar_height_px = height_px * PLOT_HEIGHT_RATIO

    gap = (plot_width_px / len_counts) * 0.1
    gap = max(min(gap, 10), 0.5)  # restrict to [1, 10]
    bin_width_px = plot_width_px / (len_counts)

    y_loc = max_bar_height_px
    x_loc = (width_px - plot_width_px) / 2

    line_stroke_width = max_bar_height_px / 30
    mean_px = normalized_mean * plot_width_px + x_loc

    font_size_px = height_px * FONT_SIZE_RATIO

    bar_highlight_style = (
        f"stroke: white; stroke-width: {line_stroke_width}; fill-opacity: 0.6;"
    )
    plot_id = random_id(10)

    hover_css = _generate_hover_css(
        num_elements=len(counts),
        bar_highlight_style=bar_highlight_style,
        tooltip_class="tooltip",
        use_hover_areas=True,
        plot_id=plot_id,
    )

    # Calculate text positioning to avoid overflow
    min_text_width = len(data_min) * font_size_px * 0.6
    max_text_width = len(data_max) * font_size_px * 0.6

    min_text_x = _calculate_text_position(
        center_x=x_loc + bin_width_px / 2,
        text_width=min_text_width,
        svg_width=width_px,
    )

    max_text_x = _calculate_text_position(
        center_x=width_px - (x_loc + bin_width_px / 2),
        text_width=max_text_width,
        svg_width=width_px,
    )

    elements: list[Element] = [
        Style(
            text=hover_css,
        ),
        # Bottom line
        Line(
            x1=0,
            x2=width_px,
            y1=y_loc,
            y2=y_loc,
            stroke="black",
            stroke_width=line_stroke_width,
        ),
        # Mean line
        Line(
            x1=mean_px,
            x2=mean_px,
            y1=y_loc - line_stroke_width / 2,
            y2=y_loc - max_bar_height_px - line_stroke_width / 2,
            stroke="black",
            stroke_width=line_stroke_width,
        ),
        Text(
            text=data_min,
            x=min_text_x,
            y=height_px,
            text_anchor="middle",
            font_size=font_size_px,
            dominant_baseline="text-top",
        ),
        Text(
            text=data_max,
            x=max_text_x,
            y=height_px,
            text_anchor="middle",
            font_size=font_size_px,
            dominant_baseline="text-top",
        ),
    ]

    # Make each bar, with an accompanying tooltip
    for i, (count, normalized_count) in enumerate(zip(counts, normalized_counts)):
        bar_height = normalized_count / 1 * max_bar_height_px
        y_loc_bar = y_loc - bar_height - line_stroke_width / 2

        # Use plot_id in element IDs and classes
        bar_id = f"{plot_id}-bar-{i}"
        bar_class = f"{plot_id}-bar-rect"

        bar = Rect(
            id=bar_id,
            class_=[bar_class],
            y=y_loc_bar,
            x=x_loc + gap / 2,
            width=bin_width_px - gap,
            height=bar_height,
            fill=fill,
        )

        left_edge = bin_edges[i]
        right_edge = bin_edges[i + 1]

        row_label = "row" if count == 1 else "rows"
        text_top = f"{count:.0f} {row_label}"
        text_bottom = f"[{left_edge} to {right_edge}]"

        # Estimate text width
        max_text_width = max(
            len(text_top) * font_size_px * 0.55,
            len(text_bottom) * font_size_px * 0.5,
        )

        x_loc_tooltip = _calculate_text_position(
            center_x=x_loc + bin_width_px / 2,
            text_width=max_text_width,
            svg_width=width_px,
        )

        tooltip_id = f"{plot_id}-tooltip-{i}"
        tooltip_class = f"{plot_id}-tooltip"
        hover_area_id = f"{plot_id}-hover-area-{i}"
        hover_area_class = f"{plot_id}-hover-area"

        tooltip = G(
            id=tooltip_id,
            class_=[tooltip_class],
            elements=[
                Text(
                    text=text_top,
                    x=x_loc_tooltip,
                    y=font_size_px * 0.25,
                    fill="black",
                    font_size=font_size_px,
                    dominant_baseline="hanging",
                    text_anchor="middle",
                    font_weight="bold",
                ),
                Text(
                    text=text_bottom,
                    x=x_loc_tooltip,
                    y=font_size_px * 1.5,
                    fill="black",
                    font_size=font_size_px,
                    dominant_baseline="hanging",
                    text_anchor="middle",
                    font_weight="bold",
                ),
            ],
        )

        # Add invisible hover area that covers bar + tooltip space
        hover_area = Rect(
            id=hover_area_id,
            class_=[hover_area_class],
            x=x_loc + gap / 2,
            y=0,
            width=bin_width_px - gap,
            height=y_loc_bar,
            fill="transparent",
            stroke="transparent",
        )

        # Insert bars at beginning, tooltips at end
        elements.insert(0, bar)
        elements.insert(0, hover_area)
        elements.append(tooltip)
        x_loc += bin_width_px

    return SVG(height=height_px, width=width_px, elements=elements)


def _clean_series(series: nw.Series, is_numeric: bool):
    clean_series = series.drop_nulls()
    if is_numeric:
        is_nan_mask = clean_series.is_nan()
        clean_series = clean_series.filter(~is_nan_mask)

    return clean_series


def _generate_hover_css(
    num_elements: int,
    bar_highlight_style: str,
    tooltip_class: str = "tooltip",
    use_hover_areas: bool = False,
    plot_id: str = "",
) -> str:
    """Generate CSS for hover effects with unique plot ID."""
    tooltip_class_id = f"{plot_id}-{tooltip_class}"
    bar_class_id = f"{plot_id}-bar-rect"
    visual_bar_class_id = f"{plot_id}-visual-bar"

    base_css = f"""
    .{tooltip_class_id} {{
        opacity: 0;
        transition: opacity 0.2s;
        pointer-events: none;
    }}
    .{bar_class_id}:hover, .{visual_bar_class_id}:hover {{
        {bar_highlight_style}
    }}
    """

    hover_rules = []
    for i in range(num_elements):
        bar_id = f"{plot_id}-bar-{i}" if plot_id else f"bar-{i}"
        tooltip_id = f"{plot_id}-tooltip-{i}" if plot_id else f"tooltip-{i}"

        hover_rules.append(f"#{bar_id}:hover ~ #{tooltip_id} {{ opacity: 1; }}")

        if use_hover_areas:
            hover_area_id = (
                f"{plot_id}-hover-area-{i}" if plot_id else f"hover-area-{i}"
            )
            hover_rules.append(
                f"#{hover_area_id}:hover ~ #{tooltip_id} {{ opacity: 1; }}"
            )
            hover_rules.append(
                f"#{hover_area_id}:hover ~ #{bar_id} {{ {bar_highlight_style} }}"
            )

    return base_css + "\n".join(hover_rules)


def _calculate_text_position(
    center_x: float,
    text_width: float,
    svg_width: float,
    margin: float = 0,
) -> float:
    """Calculate text position to avoid overflow."""
    if center_x - text_width / 2 < margin:
        return text_width / 2 + margin
    elif center_x + text_width / 2 > svg_width - margin:
        return svg_width - text_width / 2 - margin
    else:
        return center_x


# def _make_dot_plot_svg(
#     width_px: float,
#     height_px: float,
#     fill: str,
#     data_min: float,
#     data_max: float,
#     data_range: float,
#     bins: list[list[float]],
# ) -> SVG:
#     plot_width_px = width_px * 0.95
#     x_offset = (width_px - plot_width_px) / 2

#     # Calculate dot size and max vertical stacks
#     max_stack_height = max(len(bin_dates) for bin_dates in bins) if bins else 1
#     max_vertical_stacks = int(height_px / 8)

#     dot_radius = min(height_px / (min(max_stack_height, max_vertical_stacks) * 2.5), 3)
#     baseline_y = height_px - dot_radius * 2

#     elements: list[Element] = [
#         Line(
#             x1=x_offset,
#             x2=x_offset + plot_width_px,
#             y1=baseline_y,
#             y2=baseline_y,
#             stroke="black",
#             stroke_width=1,
#         ),
#         Text(
#             text=str(datetime.fromtimestamp(data_min).date()),
#             x=x_offset,
#             y=height_px,
#             text_anchor="start",
#             font_size=height_px / 6,
#             dominant_baseline="text-top",
#         ),
#         Text(
#             text=str(datetime.fromtimestamp(data_max).date()),
#             x=x_offset + plot_width_px,
#             y=height_px,
#             text_anchor="end",
#             font_size=height_px / 6,
#             dominant_baseline="text-top",
#         ),
#     ]

#     for bin_idx, bin_dates in enumerate(bins):
#         if not bin_dates:
#             continue

#         bin_center = data_min + (bin_idx + 0.5) * data_range / len(bins)
#         bin_x_center = x_offset + ((bin_center - data_min) / data_range) * plot_width_px
#         bin_width = plot_width_px / len(bins) * 0.8  # Use 80% of bin width for dots

#         num_dots = len(bin_dates)

#         if num_dots <= max_vertical_stacks:
#             for stack_idx, _ in enumerate(bin_dates):
#                 y_pos = baseline_y - (stack_idx + 1) * dot_radius * 2

#                 circle = Circle(
#                     cx=bin_x_center,
#                     cy=y_pos,
#                     r=dot_radius,
#                     fill=fill,
#                     opacity=0.7,
#                 )
#                 elements.append(circle)
#         else:
#             # Use both vertical stacking and horizontal spreading
#             cols_needed = math.ceil(num_dots / max_vertical_stacks)
#             col_spacing = bin_width / (cols_needed + 1) if cols_needed > 1 else 0

#             for dot_idx, _ in enumerate(bin_dates):
#                 col = dot_idx // max_vertical_stacks
#                 row = dot_idx % max_vertical_stacks

#                 if cols_needed == 1:
#                     x_pos = bin_x_center
#                 else:
#                     x_pos = bin_x_center - bin_width / 2 + (col + 1) * col_spacing

#                 # Calculate y position (stack vertically within column)
#                 y_pos = baseline_y - (row + 1) * dot_radius * 2

#                 circle = Circle(
#                     cx=x_pos,
#                     cy=y_pos,
#                     r=dot_radius,  # TODO adjust radius
#                     fill=fill,
#                     opacity=0.3,  # TODO: adjust opacity
#                 )
#                 elements.append(circle)

#     return SVG(height=height_px, width=width_px, elements=elements)
