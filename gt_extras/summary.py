from __future__ import annotations

import math
import statistics
from datetime import datetime, timedelta, timezone

import narwhals.stable.v1 as nw
from faicons import icon_svg
from great_tables import GT, loc, style
from narwhals.stable.v1.typing import IntoDataFrame, IntoDataFrameT
from svg import SVG, Element, G, Line, Rect, Style, Text

from gt_extras._utils_column import _format_numeric_text
from gt_extras.themes import gt_theme_espn

__all__ = ["gt_plt_summary"]

COLOR_MAPPING = {
    "string": "#4e79a7",
    "numeric": "#f18e2c",
    "datetime": "#73a657",
    "boolean": "#a65773",
    "other": "black",
}
DEFAULT_WIDTH_PX = 180  # TODO choose how to assign dimensions
DEFAULT_HEIGHT_PX = 40
PLOT_WIDTH_RATIO = 0.95
PLOT_HEIGHT_RATIO = 0.8
FONT_SIZE_RATIO = 0.2  # height_px / 5


def gt_plt_summary(
    df: IntoDataFrame,
    title: str | None = None,
    show_desc_stats: bool = True,
    add_mode: bool = False,
    interactivity: bool = True,
    new_color_mapping: dict | None = None,
) -> GT:
    """
    Create a comprehensive data summary table with visualizations.

    The `gt_plt_summary()` function takes a DataFrame and generates a summary table showing key
    statistics and visual representations for each column. Each row displays the column type,
    missing data percentage, descriptive statistics (mean, median, standard deviation), and a
    small plot overview appropriate for the data type (histograms for numeric and datetime and
    a categorical bar chart for strings).

    Inspired by the Observable team and the observablehq/SummaryTable function:
    https://observablehq.com/@observablehq/summary-table

    Parameters
    ----------
    df
        A DataFrame to summarize. Can be any DataFrame type that you would pass into a `GT`.

    title
        Optional title for the summary table. If `None`, defaults to "Summary Table".

    show_desc_stats
        Boolean that allows the hiding of the Mean, Median, and SD columns. Defaults to `False`.

    add_mode
        Boolean that allows the addition of a Mode column. Defaults to `False`.

    interactivity
        Boolean that toggles interactivity in Plot Overview column graphs. Interactivity refers to
        hovering css and tooltips code applied to the graphs.

    new_color_mapping
        A dictionary that maps data types (string, numeric, datetime, boolean, and other) to their
        corresponding color codes in hexadecimal format.

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

    And lastly, an example showing ocean swell data with changes to the default color mapping:
    ```{python}
    import polars as pl
    from great_tables import GT
    import gt_extras as gte
    from datetime import datetime

    df = pl.DataFrame({
    "Date": [
        datetime(2024, 7, 1, 6, 0),
        datetime(2024, 7, 1, 12, 0),
        datetime(2024, 7, 2, 6, 0),
        datetime(2024, 7, 2, 12, 0),
        datetime(2024, 7, 3, 6, 0),
        datetime(2024, 7, 3, 12, 0),
        datetime(2024, 7, 4, 6, 0),
        datetime(2024, 7, 4, 12, 0),
        datetime(2024, 7, 5, 6, 0),
    ],
    "Height_m": [1.2, 1.5, 2.1, 2.4, 1.8, None, 2.7, 3.0, 2.5],
    "Period_s": [10, 12, 14, 15, 11, 9, 16, None, 13],
    "Direction_deg": [210, 215, 220, 225, 205, 200, 230, 240, 235],
    "WindSpeed_kts": [5, 7, 10, 12, 6, 4, 8, 11, None],
    "Breaking": [True, True, True, False, True, False, True, True, True]
    })

    color_mapping = {
        "date": "blue",
        "numeric": "lightblue",
        "boolean": "lightgreen",
    }

    gte.gt_plt_summary(df, new_color_mapping=color_mapping)
    ```

    Note
    ---------
    The datatype (dtype) of each column in your dataframe will determine the classified type in the
    summary table. Keep in mind that sometimes pandas or polars have differing behaviors with
    datatypes, especially when null values are present.
    """
    if new_color_mapping:
        global COLOR_MAPPING
        COLOR_MAPPING.update(new_color_mapping)

    summary_df = _create_summary_df(
        df, show_desc_stats=show_desc_stats, add_mode=add_mode
    )

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
        # Add visuals
        .fmt(_make_icon_html, columns="Type")
        # Format numerics
        .fmt_percent(columns="Missing", decimals=1)
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(columns="Column"),
        )
        # add style
        .cols_align(align="center", columns="Plot Overview")
    )

    # Polars has strict column checking, so can't perform .sub_missing or .fmt_number etc on columns
    # that aren't present in a df. Therefore, we need to check if those columns are present prior to
    # handling missing and formatting.
    cols_to_check = ["Mean", "Median", "SD"] + (["Mode"] if add_mode else [])
    existing_desc_cols = [col for col in cols_to_check if col in nw_summary_df.columns]

    # Mode stays as a string object, so we don't include in here.
    columns_to_format_as_number = [
        col for col in ["Mean", "Median", "SD"] if col in nw_summary_df.columns
    ]

    if show_desc_stats:
        gt = (
            # handle missing
            gt.sub_missing(columns=existing_desc_cols).fmt_number(
                columns=columns_to_format_as_number,
                rows=numeric_cols,
            )
        )

    gt = gt_theme_espn(gt)

    for i, col_name in enumerate(nw_summary_df.get_column("Column")):
        vals = nw.from_native(df, eager_only=True)[col_name]
        vals = _clean_series(vals, vals.dtype.is_numeric())

        col_type = nw_summary_df.item(row=i, column="Type")
        gt = gt.fmt(
            lambda _,
            vals=vals,
            col_type=col_type,
            plot_id="id" + str(i): _make_summary_plot(
                nw_series=vals,
                col_type=col_type,
                plot_id=plot_id,
                interactivity=interactivity,
            ),
            columns="Plot Overview",
            rows=i,
        )
    return gt


############### Helpers for gt_plt_summary ###############


def _create_summary_df(
    df: IntoDataFrameT, show_desc_stats: bool = True, add_mode: bool = False
) -> IntoDataFrameT:
    nw_df = nw.from_native(df, eager_only=True)  # Should I be concerned about this?

    summary_data = {
        "Type": [],
        "Column": [],
        "Plot Overview": [],
        "Missing": [],
    }

    for col_name in nw_df.columns:
        col = nw_df[col_name]

        mean_val = None
        median_val = None
        std_val = None
        mode_val = None

        clean_col = _clean_series(col, col.dtype.is_numeric())

        missing_count = len(col) - len(clean_col)
        if len(col) == 0:
            missing_ratio = 1
        else:
            missing_ratio = missing_count / len(col)

        if col.dtype.is_numeric():
            col_type = "numeric"
            mean_val = clean_col.mean()
            median_val = clean_col.median()
            std_val = clean_col.std()
            mode_val = clean_col.mode()
            # If lengths are the same there's no mode, likely due to continuous data input.
            if len(mode_val) == len(clean_col):
                mode_val = "No Singular Mode"
            # Limiting the number of modes displayed to two at maximum
            elif len(mode_val) > 2:
                mode_val = "Greater than 2 Modes"
            # Converting to string, then listing together
            else:
                mode_val = ", ".join(str(i) for i in mode_val.to_list())

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
        # setdefault adds the column if it's not present
        if show_desc_stats:
            summary_data.setdefault("Mean", []).append(mean_val)
            summary_data.setdefault("Median", []).append(median_val)
            summary_data.setdefault("SD", []).append(std_val)
        if show_desc_stats and add_mode:
            summary_data.setdefault("Mode", []).append(mode_val)

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
    plot_id: str,
    interactivity: bool = True,
) -> str:
    if len(nw_series) == 0:
        return "<div></div>"

    clean_list = nw_series.to_native().to_list()

    if col_type == "string":
        return _plot_categorical(
            clean_list, plot_id=plot_id, interactivity=interactivity
        )
    elif col_type == "numeric":
        return _plot_numeric(clean_list, plot_id=plot_id, interactivity=interactivity)
    elif col_type == "datetime":
        return _plot_datetime(clean_list, plot_id=plot_id, interactivity=interactivity)
    elif col_type == "boolean":
        return _plot_boolean(clean_list, plot_id=plot_id, interactivity=interactivity)
    else:
        return "<div></div>"


def _plot_categorical(data: list[str], plot_id: str, interactivity: bool = True) -> str:
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
        plot_id=plot_id,
        proportions=proportions,
        categories=[
            category for category, _ in sorted_categories
        ],  # maybe leave combined with counts?
        counts=counts,
        interactivity=interactivity,
    )

    return svg.as_str()


def _plot_boolean(data: list[bool], plot_id: str, interactivity: bool = True) -> str:
    true_count = sum(data)
    false_count = len(data) - true_count
    total_count = len(data)

    boolean_data = []
    if true_count > 0:
        boolean_data.append(("True", true_count))
    if false_count > 0:
        boolean_data.append(("False", false_count))

    counts = [count for _, count in boolean_data]
    proportions = [count / total_count for count in counts]
    categories = [label for label, _ in boolean_data]

    # Set opacities: False is always lighter (0.2)
    if true_count == 0 and false_count > 0:
        opacities = [0.2]  # Only False present
    elif true_count > 0 and false_count > 0:
        opacities = [1.0, 0.2]
    else:
        opacities = [1.0]  # Only True present

    svg = _make_categories_bar_svg(
        width_px=DEFAULT_WIDTH_PX,
        height_px=DEFAULT_HEIGHT_PX,
        fill=COLOR_MAPPING["boolean"],
        plot_id=plot_id,
        proportions=proportions,
        categories=categories,
        counts=counts,
        opacities=opacities,
        interactivity=interactivity,
    )

    return svg.as_str()


def _make_categories_bar_svg(
    width_px: float,
    height_px: float,
    fill: str,
    plot_id: str,
    proportions: list[float],
    categories: list[str],
    counts: list[int],
    opacities: list[float] | None = None,
    interactivity: bool = True,
) -> SVG:
    plot_width_px = width_px * PLOT_WIDTH_RATIO
    plot_height_px = height_px * PLOT_HEIGHT_RATIO

    x_offset = (width_px - plot_width_px) / 2
    y_offset = (height_px - plot_height_px) / 2

    x_loc = x_offset
    font_size_px = height_px * FONT_SIZE_RATIO

    max_opacity = 1.0
    min_opacity = 0.2

    if interactivity:
        hover_css = _generate_hover_css(
            num_elements=len(proportions),
            bar_highlight_style="opacity: 0.4;",
            tooltip_class="category-tooltip",
            use_hover_areas=False,
            plot_id=plot_id,
        )

        elements: list[Element] = [Style(text=hover_css)]
    else:
        elements: list[Element] = []

    for i, (proportion, category, count) in enumerate(
        zip(proportions, categories, counts)
    ):
        section_width = proportion * plot_width_px

        if opacities is not None:
            opacity = opacities[i]

        elif len(proportions) == 1:
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

        row_label = "row" if count == 1 else "rows"
        text_top = f"{count:.0f} {row_label}"
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
        if interactivity:
            elements.append(tooltip)
        x_loc += section_width

    return SVG(height=height_px, width=width_px, elements=elements)


def _plot_numeric(
    data: list[float] | list[int], plot_id: str, interactivity: bool = True
) -> str:
    data_min, data_max = min(data), max(data)
    data_range = data_max - data_min

    if data_range == 0:
        data_min -= 1.5
        data_max += 1.5
        data_range = 3

    # after cleaning in _make_summary_plot, we know len(data) > 1
    if len(data) == 1:
        bw = 1
    # edge case when len(data) == 2 means we can't get quartiles
    elif len(data) == 2:
        bw = (max(data) - min(data)) * 0.5
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
    bin_edges = [_format_numeric_text(edge, 2) for edge in bin_edges]

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
        plot_id=plot_id,
        normalized_mean=normalized_mean,
        data_max=str(round(data_max, 2)),
        data_min=str(round(data_min, 2)),
        counts=counts,
        bin_edges=bin_edges,
        interactivity=interactivity,
    )

    return svg.as_str()


def _plot_datetime(
    dates: list[datetime], plot_id: str, interactivity: bool = True
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

    # edge case when len(data) == 2 means we can't get quartiles
    # slight duplicate in _plot_numeric
    elif len(date_timestamps) == 2:
        bw = (max(date_timestamps) - min(date_timestamps)) * 0.5

    # Calculate binwidth using Freedman-Diaconis rule
    else:
        quantiles = statistics.quantiles(date_timestamps, method="inclusive")
        q25, _, q75 = quantiles
        iqr = q75 - q25
        bw = 2 * iqr / (len(date_timestamps) ** (1 / 3))

    if bw <= 0:
        bw = data_range / 3  # Fallback

    n_bins = max(1, int(math.ceil(data_range / bw)))
    bin_edges = [data_min + i * data_range / n_bins for i in range(n_bins + 1)]
    bin_edges = [
        str(datetime.fromtimestamp(edge, tz=timezone.utc).date()) for edge in bin_edges
    ]

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
        plot_id=plot_id,
        normalized_mean=normalized_mean,
        data_max=str(datetime.fromtimestamp(data_max, tz=timezone.utc).date()),
        data_min=str(datetime.fromtimestamp(data_min, tz=timezone.utc).date()),
        counts=counts,
        bin_edges=bin_edges,
        interactivity=interactivity,
    )

    return svg.as_str()


def _make_histogram_svg(
    width_px: float,
    height_px: float,
    fill: str,
    plot_id: str,
    normalized_mean: float,
    data_min: str,
    data_max: str,
    counts: list[float],
    bin_edges: list[str],
    interactivity: bool = True,
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

    if interactivity:
        hover_css = _generate_hover_css(
            num_elements=len(counts),
            bar_highlight_style=bar_highlight_style,
            tooltip_class="tooltip",
            use_hover_areas=True,
            plot_id=plot_id,
        )
        elements.append(Style(text=hover_css))

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
        if interactivity:
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
