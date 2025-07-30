from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Literal

from great_tables import GT, html
from great_tables._data_color.base import (
    _html_color,
    _ideal_fgnd_color,
)
from great_tables._locations import resolve_cols_c
from great_tables._tbl_data import SelectExpr, is_na
from scipy.stats import sem, t, tmean
from svg import SVG, Circle, Length, Line, Rect, Text

from gt_extras import gt_duplicate_column
from gt_extras._utils_color import _get_discrete_colors_from_palette
from gt_extras._utils_column import (
    _scale_numeric_column,
    _validate_and_get_single_column,
)

__all__ = [
    "gt_plt_bar",
    "gt_plt_bar_pct",
    "gt_plt_bar_stack",
    "gt_plt_bullet",
    "gt_plt_conf_int",
    "gt_plt_dot",
    "gt_plt_dumbbell",
    "gt_plt_winloss",
]

# TODO: default font for labels?

# TODO: how to handle negative values? Plots can't really have negative length


def gt_plt_bar(
    gt: GT,
    columns: SelectExpr = None,
    fill: str = "purple",
    bar_height: float = 20,
    height: float = 30,
    width: float = 60,
    stroke_color: str | None = "black",
    show_labels: bool = False,
    label_color: str = "white",
    domain: list[int] | list[float] | None = None,
    keep_columns: bool = False,
) -> GT:
    """
    Create horizontal bar plots in `GT` cells.

    The `gt_plt_bar()` function takes an existing `GT` object and adds horizontal bar charts to
    specified columns. Each cell value is represented as a horizontal bar with length proportional
    to the cell's numeric value relative to the column's maximum value.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    columns
        The columns to target. Can be a single column or a list of columns (by name or index).
        If `None`, the bar plot is applied to all numeric columns.

    fill
        The fill color for the bars.

    bar_height
        The height of each individual bar in pixels.

    height
        The height of the bar plot in pixels. In practice, this allows for the bar to appear
        less stout, the larger the difference between `height` and `bar_height`.

    width
        The width of the maximum bar in pixels. Not all bars will have this width.

    stroke_color
        The color of the vertical axis on the left side of the bar. The default is black, but if
        `None` is passed, no stroke will be drawn.

    show_labels
        Whether or not to show labels on the bars.

    label_color
        The color of text labels on the bars (when `show_labels` is `True`).

    keep_columns
        Whether to keep the original column values. If this flag is `True`, the plotted values will
        be duplicated into a new column with the string " plot" appended to the end of the column
        name. See [`gt_duplicate_column()`](https://posit-dev.github.io/gt-extras/reference/gt_duplicate_column)
        for more details.


    Returns
    -------
    GT
        A `GT` object with horizontal bar plots added to the specified columns.

    Examples
    --------

    ```{python}
    from great_tables import GT
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars.loc[
        9:17,
        ["model", "mfr", "year", "hp", "hp_rpm", "trq", "trq_rpm", "mpg_c", "mpg_h"]
    ]

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label="Car")
        .cols_align("center")
        .cols_align("left", columns="mfr")
    )

    gt.pipe(
        gte.gt_plt_bar,
        columns= ["hp", "hp_rpm", "trq", "trq_rpm", "mpg_c", "mpg_h"]
    )
    ```

    Note
    --------
    Each column's bars are scaled independently based on that column's min/max values.
    """
    if bar_height > height:
        bar_height = height
        warnings.warn(
            f"Bar_height must be less than or equal to the plot height. Adjusting bar_height to {bar_height}.",
            category=UserWarning,
        )

    if bar_height < 0:
        bar_height = 0
        warnings.warn(
            f"Bar_height cannot be negative. Adjusting bar_height to {bar_height}.",
            category=UserWarning,
        )

    # Allow the user to hide the vertical stroke
    if stroke_color is None:
        stroke_color = "transparent"

    def _make_bar(scaled_val: float, original_val: int | float) -> str:
        svg = _make_bar_svg(
            scaled_val=scaled_val,
            original_val=original_val,
            fill=fill,
            bar_height=bar_height,
            height=height,
            width=width,
            stroke_color=stroke_color,
            show_labels=show_labels,
            label_color=label_color,
        )

        return f'<div style="display: flex;">{svg.as_str()}</div>'

    # Get names of columns
    columns_resolved = resolve_cols_c(data=gt, expr=columns)

    res = gt
    for column in columns_resolved:
        # Validate this is a single column and get values
        col_name, col_vals = _validate_and_get_single_column(
            gt,
            column,
        )

        scaled_vals = _scale_numeric_column(
            res._tbl_data,
            col_name,
            col_vals,
            domain,
        )

        # The location of the plot column will be right after the original column
        if keep_columns:
            res = gt_duplicate_column(
                res,
                col_name,
                after=col_name,
                append_text=" plot",
            )
            col_name = col_name + " plot"

        # Apply the scaled value for each row, so the bar is proportional
        for i, scaled_val in enumerate(scaled_vals):
            res = res.fmt(
                lambda original_val, scaled_val=scaled_val: _make_bar(
                    original_val=original_val,
                    scaled_val=scaled_val,
                ),
                columns=col_name,
                rows=[i],
            )

    return res


def gt_plt_bullet(
    gt: GT,
    data_column: SelectExpr,
    target_column: SelectExpr,
    # target_value: int | None = None, # if this, let target_column be none?
    fill: str = "purple",
    bar_height: float = 20,
    height: float = 30,
    width: float = 60,
    target_color: str = "darkgrey",
    stroke_color: str | None = "black",
    # show_labels: bool = False, # Maybe include in later version of fn, to label target or data?
    # label_color: str = "white",
    keep_data_column: bool = False,
) -> GT:
    """
    Create bullet chart plots in `GT` cells.

    The `gt_plt_bullet()` function takes an existing `GT` object and adds bullet chart
    visualizations to compare actual values against target values. Each bullet chart consists
    of a horizontal bar representing the actual value and a vertical line indicating the target
    value, making it easy to assess performance against goals or benchmarks.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    data_column
        The column containing the actual values to be plotted as horizontal bars.

    target_column
        The column containing the target values to be displayed as vertical reference lines.
        This column will be automatically hidden from the returned table.

    fill
        The fill color for the horizontal bars representing actual values.

    bar_height
        The height of each horizontal bar in pixels.

    height
        The height of the bullet chart plot in pixels. This allows for spacing around
        the bar and target line.

    width
        The width of the maximum bar in pixels. Bars are scaled proportionally to this width.

    target_color
        The color of the vertical target line.

    stroke_color
        The color of the vertical axis on the left side of the chart. The default is black, but if
        `None` is passed, no stroke will be drawn.

    keep_data_column
        Whether to keep the original data column values. If this flag is `True`, the plotted values
        will be duplicated into a new column with the string " plot" appended to the end of the
        column name. See [`gt_duplicate_column()`](https://posit-dev.github.io/gt-extras/reference/gt_duplicate_column)
        for more details.

    Returns
    -------
    GT
        A `GT` object with bullet chart plots added to the specified data column. The target
        column is automatically hidden from the table.

    Examples
    --------
    ```{python}
    import polars as pl
    from great_tables import GT
    from great_tables.data import airquality
    import gt_extras as gte

    air_bullet = (
        pl.from_pandas(airquality)
        .with_columns(pl.col("Temp").mean().over("Month").alias("target_temp"))
        .group_by("Month", maintain_order=True)
        .head(2)
        .with_columns(
            (pl.col("Month").cast(pl.Utf8) + "/" + pl.col("Day").cast(pl.Utf8)).alias(
                "Date"
            )
        )
        .select(["Date", "Temp", "target_temp"])
        .with_columns(pl.col(["Temp", "target_temp"]).round(1))
    )

    (
        GT(air_bullet, rowname_col="Date")
        .tab_header(title="Daily Temp vs Monthly Average")
        .tab_source_note("Target line shows monthly average temperature")

        ## Call gt_plt_bullet
        .pipe(
            gte.gt_plt_bullet,
            data_column="Temp",
            target_column="target_temp",
            width=200,
            fill="tomato",
            target_color="darkblue",
            keep_data_column=True,
        )
        .cols_move_to_end("Temp")
        .cols_align("left", "Temp plot")
    )
    ```

    Note
    ----
    Both data and target values are scaled to a common domain for consistent visualization.
    The scaling domain is automatically determined as `[0, max(data_values, target_values)]`.
    """
    if bar_height > height:
        bar_height = height
        warnings.warn(
            f"Bar_height must be less than or equal to the plot height. Adjusting bar_height to {bar_height}.",
            category=UserWarning,
        )

    if bar_height < 0:
        bar_height = 0
        warnings.warn(
            f"Bar_height cannot be negative. Adjusting bar_height to {bar_height}.",
            category=UserWarning,
        )

    # Allow the user to hide the vertical stroke
    if stroke_color is None:
        stroke_color = "transparent"

    def _make_bullet_plot_svg(
        scaled_val: float,
        original_val: int | float,
        target_val: float,
        original_target_val: float | int | None,
    ) -> str:
        svg = _make_bar_svg(
            scaled_val=scaled_val,
            original_val=original_val,
            fill=fill,
            bar_height=bar_height,
            height=height,
            width=width,
            stroke_color=stroke_color,
            show_labels=False,
            label_color="black",  # placeholder
        )

        # this should never be reached, but is needed for the type checker
        if TYPE_CHECKING:
            if svg.elements is None:
                raise ValueError(
                    "Unreachable code: svg.elements should never be None here."
                )

        if not is_na(res._tbl_data, original_target_val):
            _stroke_width = height / 10
            _x_location = max(_stroke_width, width * target_val - _stroke_width / 2)

            svg.elements.append(
                Line(
                    x1=Length(_x_location, "px"),
                    x2=Length(_x_location, "px"),
                    y1=0,
                    y2=Length(height, "px"),
                    stroke_width=Length(_stroke_width, "px"),
                    stroke=target_color,
                ),
            )

        return f'<div style="display: flex;">{svg.as_str()}</div>'

    res = gt

    data_col_name, data_col_vals = _validate_and_get_single_column(
        gt,
        data_column,
    )
    target_col_name, target_col_vals = _validate_and_get_single_column(
        gt,
        target_column,
    )

    # Only consider numeric values for scaling domain
    domain = None
    numeric_data_vals = [v for v in data_col_vals if isinstance(v, (int, float))]
    numeric_target_vals = [v for v in target_col_vals if isinstance(v, (int, float))]
    if numeric_data_vals or numeric_target_vals:
        domain = [0, max([*numeric_data_vals, *numeric_target_vals])]

    scaled_data_vals = _scale_numeric_column(
        res._tbl_data,
        data_col_name,
        data_col_vals,
        domain,
    )

    scaled_target_vals = _scale_numeric_column(
        res._tbl_data,
        target_col_name,
        target_col_vals,
        domain,
    )

    if keep_data_column:
        res = gt_duplicate_column(
            res,
            data_col_name,
            after=data_col_name,
            append_text=" plot",
        )
        data_col_name = data_col_name + " plot"

    # Apply the scaled value for each row, so the bar is proportional
    for i, scaled_val in enumerate(scaled_data_vals):
        target_val = scaled_target_vals[i]
        original_target_val = target_col_vals[i]

        res = res.fmt(
            lambda original_val,
            scaled_val=scaled_val,
            target_val=target_val,
            original_target_val=original_target_val: _make_bullet_plot_svg(
                original_val=original_val,
                scaled_val=scaled_val,
                target_val=target_val,
                original_target_val=original_target_val,
            ),
            columns=data_col_name,
            rows=[i],
        )

    res = res.cols_hide(target_col_name)

    return res


def gt_plt_dot(
    gt: GT,
    category_col: SelectExpr,
    data_col: SelectExpr,
    width: int = 120,
    height: int = 30,
    font_size: int = 16,
    domain: list[int] | list[float] | None = None,
    palette: list[str] | str | None = None,
) -> GT:
    """
    Create dot plots with thin horizontal bars in `GT` cells.

    The `gt_plt_dot()` function takes an existing `GT` object and adds dot plots with horizontal
    bar charts to a specified category column. Each cell displays a colored dot according to the
    value in the assigned category column and a horizontal bar representing the corresponding
    numeric value from the data column.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    category_col
        The column containing category labels that will be displayed next to colored dots. The
        coloring of the dots are determined by this column.

    data_col
        The column containing numeric values that will determine the length of the horizontal bars.

    width
        The width of the SVG plot in pixels. You may need to increase this if your category labels
        are long.

    height
        The height of the SVG plot in pixels.

    font_size
        The font size for the category label text and dot.

    domain
        The domain of values to use for the color scheme. This can be a list of floats or integers.
        If `None`, the domain is automatically set to `[0, max(data_col)]`.

    palette
        The color palette to use. This should be a list of colors
        (e.g., `["#FF0000"`, `"#00FF00"`, `"#0000FF"` `]`). A ColorBrewer palette could also be used,
        just supply the name (see [`GT.data_color()`](https://posit-dev.github.io/great-tables/reference/GT.data_color) for additional reference).
        If `None`, then a default palette will be used.

    Returns
    -------
    GT
        A `GT` object with dot plots and horizontal bars added to the specified category column.

    Examples
    --------
    ```{python}
    from great_tables import GT
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars.loc[8:20, ["model", "mfr", "hp"]]

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label="Car")
    )

    gt.pipe(gte.gt_plt_dot, category_col="mfr", data_col="hp")
    ```

    Note
    -------
    If your category label text is cut off or does not fit, you likely need to increase the `width`
    parameter to allow more space for the text and plot.
    """
    # Get the underlying Dataframe
    data_table = gt._tbl_data

    def _make_dot_and_bar_svg(
        bar_val: float,
        fill: str,
        dot_category_label: str,
        svg_width: float,
        svg_height: float,
        font_size: float,
    ) -> str:
        if is_na(data_table, bar_val) or is_na(data_table, dot_category_label):
            return "<div></div>"

        # Layout parameters
        dot_radius = font_size / 2.75
        dot_x = dot_radius
        dot_y = svg_height / 2

        # Text positioning
        text_x = dot_x + dot_radius * 1.5
        text_y = dot_y

        # Bar positioning
        bar_y = text_y + (font_size / 2) * 1.2  # 1.2 for padding
        bar_height = svg_height / 8
        bar_start_x = 0
        bar_width = svg_width * bar_val

        elements = [
            # Dot
            Circle(
                cx=dot_x,
                cy=dot_y,
                r=dot_radius,
                fill=fill,
            ),
            # Category label text
            Text(
                text=dot_category_label,
                x=text_x,
                y=text_y,
                fill="black",
                font_size=font_size,
                dominant_baseline="central",
                text_anchor="start",
            ),
            # Bar
            Rect(
                x=bar_start_x,
                y=bar_y,
                width=bar_width,
                height=bar_height,
                fill=fill,
                rx=2,
            ),
        ]

        svg = SVG(width=svg_width, height=svg_height, elements=elements)
        return f'<div style="display: flex;">{svg.as_str()}</div>'

    # Validate and get data column
    data_col_name, data_col_vals = _validate_and_get_single_column(
        gt,
        data_col,
    )

    # Process numeric data column
    scaled_data_vals = _scale_numeric_column(
        data_table,
        data_col_name,
        data_col_vals,
        domain,
    )

    # Validate and get category column
    _, category_col_vals = _validate_and_get_single_column(
        gt,
        category_col,
    )

    color_vals = _get_discrete_colors_from_palette(
        palette=palette, data=category_col_vals, data_table=data_table
    )

    # Apply gt.fmt() to each row individually, so we can access the data_value for that row
    res = gt
    for i in range(len(data_table)):
        data_val = scaled_data_vals[i]
        color_val = color_vals[i]

        res = res.fmt(
            lambda x, data=data_val, fill=color_val: _make_dot_and_bar_svg(
                dot_category_label=x,
                fill=fill,
                bar_val=data,
                svg_height=height,
                svg_width=width,
                font_size=font_size,
            ),
            columns=category_col,
            rows=[i],
        )

    return res


def gt_plt_conf_int(
    gt: GT,
    column: SelectExpr,
    ci_columns: SelectExpr = None,
    ci: float = 0.95,
    width: float = 100,
    height: float = 30,
    dot_color: str = "red",
    dot_border_color: str = "red",
    line_color: str = "royalblue",
    text_color: str = "black",
    font_size: int = 10,
    num_decimals: int = 1,
    # TODO: "none" vs None in text_size
) -> GT:
    """
    Create confidence interval plots in `GT` cells.

    The `gt_plt_conf_int()` function takes an existing `GT` object and adds horizontal confidence
    interval plots to a specified column. Each cell displays a horizontal bar representing the
    confidence interval, with a dot indicating the mean value. Optionally, the lower and upper
    confidence interval bounds can be provided directly, or the function can compute them.

    If `ci_columns` is not provided, the function assumes each cell in `column` contains a list of
    values and computes the confidence interval using a t-distribution.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    column
        The column that contains the mean of the sample. This can either be a single number per row,
        if you have calculated the values ahead of time, or a list of values if you want to
        calculate the confidence intervals.

    ci_columns
        Optional columns representing the left/right confidence intervals of your sample. If `None`,
        the confidence interval will be computed from the data in `column` using a t-distribution.

    ci
        The confidence level to use when computing the interval (if `ci_columns` is `None`).

    width
        The width of the confidence interval plot in pixels. Note that if the width is too narrow,
        some label text may overlap.

    height
        The width of the confidence interval plot in pixels.

    dot_color
        The color of the mean dot.

    dot_border_color
        The color of the border around the mean dot.

    line_color
        The color of the confidence interval bar.

    text_color
        The color of the confidence interval labels.

    font_size
        The size of the text for the confidence interval labels.
        A value of 0 will result in hiding the text.

    num_decimals
        The number of decimals to display when rounding the value of the
        confidence interval labels.

    Returns
    -------
    GT
        A `GT` object with confidence interval plots added to the specified column.

    Examples
    --------
    ```{python}
    import pandas as pd
    from great_tables import GT
    import gt_extras as gte

    df = pd.DataFrame({
        'group': ['A', 'B', 'C'],
        'mean': [5.2, 7.8, 3.4],
        'ci_lower': [3.1, 6.1, 1.8],
        'ci_upper': [7.3, 9.7, 5.0],
        'ci': [5.2, 7.8, 3.4],
    })

    gt = GT(df)
    gt.pipe(
        gte.gt_plt_conf_int,
        column='ci',
        ci_columns=['ci_lower', 'ci_upper'],
        width=120,
    )
    ```

    Alternatively we can pass in a column of lists, and the function will compute the CI's for us.

    ```{python}
    import numpy as np
    np.random.seed(37)

    n_per_group = 50
    groups = ["A", "B", "C"]
    means = [20, 22, 25]
    sds = [10, 16, 10]

    # Create the data
    data = []
    for i, (grp, mean, sd) in enumerate(zip(groups, means, sds)):
        values = np.random.normal(mean, sd, n_per_group)
        data.extend([{"grp": grp, "values": val} for val in values])

    df_raw = pd.DataFrame(data)
    df_summary = (
        df_raw
        .groupby("grp")
        .agg({"values": ["count", "mean", "std", list]})
        .round(3)
    )
    df_summary.columns = ["n", "avg", "sd", "ci"]

    gt = GT(df_summary)
    gt.pipe(
        gte.gt_plt_conf_int,
        column="ci",
        width = 160,
    )
    ```

    Note
    ----
    All confidence intervals are scaled to a common range for visual alignment.
    """

    def _make_conf_int_svg(
        mean: float,
        c1: float,
        c2: float,
        font_size: float,
        min_val: float,
        max_val: float,
        width: float,
        height: float,
        dot_border_color: str,
        line_color: str,
        dot_color: str,
        text_color: str,
        num_decimals: int,
    ) -> str:
        if (
            is_na(gt._tbl_data, mean)
            or is_na(gt._tbl_data, c1)
            or is_na(gt._tbl_data, c2)
        ):
            return f'<div style="display: flex;"><div style="width:{width}px; height:{height}px;"></div></div>'

        span = max_val - min_val

        # Normalize positions to [0, 1] based on global min/max, then scale to width
        c1_pos = ((c1 - min_val) / span) * width
        c2_pos = ((c2 - min_val) / span) * width
        mean_pos = ((mean - min_val) / span) * width

        bar_height = height / 10
        bar_y = height / 2 - bar_height / 2 + font_size / 2

        # Text positioning - place labels above the bar
        label_y = bar_y - (font_size / 2) * 1.2  # 1.2 for padding

        # Dot positioning
        dot_size = height / 5
        dot_y = bar_y - dot_size / 4
        dot_border = height / 20

        # Format the label text
        c1_text = f"{c1:.{num_decimals}f}".rstrip("0").rstrip(".")
        c2_text = f"{c2:.{num_decimals}f}".rstrip("0").rstrip(".")

        elements = [
            # Confidence interval bar
            Rect(
                x=c1_pos,
                y=bar_y,
                width=c2_pos - c1_pos,
                height=bar_height,
                fill=line_color,
                rx=2,
            ),
            # Mean dot
            Circle(
                cx=mean_pos,
                cy=dot_y + dot_size / 2,
                r=dot_size / 2,
                fill=dot_color,
                stroke=dot_border_color,
                stroke_width=dot_border,
            ),
            # Lower bound label
            Text(
                text=c1_text,
                x=c1_pos,
                y=label_y,
                fill=text_color,
                font_size=font_size,
                text_anchor="start",
                dominant_baseline="central",
            ),
            # Upper bound label
            Text(
                text=c2_text,
                x=c2_pos,
                y=label_y,
                fill=text_color,
                font_size=font_size,
                text_anchor="end",
                dominant_baseline="central",
            ),
        ]

        svg = SVG(width=width, height=height, elements=elements)
        return f'<div style="display: flex;">{svg.as_str()}</div>'

    data_col_name, data_vals = _validate_and_get_single_column(gt, column)

    # must compute the ci ourselves
    if ci_columns is None:
        # Check that all entries are lists or None
        if any(val is not None and not isinstance(val, list) for val in data_vals):
            raise ValueError(
                f"Expected entries in {data_col_name} to be lists or None,"
                "since ci_columns were not given."
            )

        def _compute_mean_and_conf_int(val):
            if val is None or not isinstance(val, list) or len(val) == 0:
                return (None, None, None)
            mean = tmean(val)
            conf_int = t.interval(
                ci,
                len(val) - 1,
                loc=mean,
                scale=sem(val),
            )
            return (mean, conf_int[0], conf_int[1])

        stats = list(map(_compute_mean_and_conf_int, data_vals))
        means, c1_vals, c2_vals = zip(*stats) if stats else ([], [], [])

    # we were given the ci already computed
    else:
        ci_columns_resolved = resolve_cols_c(data=gt, expr=ci_columns)
        if len(ci_columns_resolved) != 2:
            raise ValueError(
                f"Expected 2 ci_columns, instead received {len(ci_columns_resolved)}."
            )

        _, c1_vals = _validate_and_get_single_column(
            gt,
            ci_columns_resolved[0],
        )
        _, c2_vals = _validate_and_get_single_column(
            gt,
            ci_columns_resolved[1],
        )
        means = data_vals

        if any(val is not None and not isinstance(val, (int, float)) for val in means):
            raise ValueError(
                f"Expected all entries in {data_col_name} to be numeric or None,"
                "since ci_columns were given."
            )

    # Compute a global range to ensure conf int bars align
    all_values = [val for val in [*means, *c1_vals, *c2_vals] if val is not None]
    data_min = min(all_values)
    data_max = max(all_values)
    data_range = data_max - data_min

    # Add 10% padding on each side
    padding = data_range * 0.1
    global_min = data_min - padding
    global_max = data_max + padding

    res = gt
    for i in range(len(gt._tbl_data)):
        c1 = c1_vals[i]
        c2 = c2_vals[i]
        mean = means[i]

        res = res.fmt(
            lambda _, c1=c1, c2=c2, mean=mean: _make_conf_int_svg(
                mean=mean,
                c1=c1,
                c2=c2,
                font_size=font_size,
                min_val=global_min,
                max_val=global_max,
                width=width,
                height=height,
                dot_border_color=dot_border_color,
                line_color=line_color,
                dot_color=dot_color,
                text_color=text_color,
                num_decimals=num_decimals,
            ),
            columns=data_col_name,
            rows=[i],
        )

    return res


def gt_plt_dumbbell(
    gt: GT,
    col1: SelectExpr,  # exactly 1 col
    col2: SelectExpr,  # exactly 1 col
    label: str | None = None,
    width: float = 100,
    height: float = 30,
    col1_color: str = "purple",
    col2_color: str = "green",
    bar_color: str = "grey",
    dot_border_color="white",
    font_size: int = 10,
    num_decimals: int = 1,
) -> GT:
    """
    Create dumbbell plots in `GT` cells.

    The `gt_plt_dumbbell()` function takes an existing `GT` object and adds dumbbell plots to
    visualize the difference between two numeric values. Each dumbbell consists of two dots
    (representing values from `col1` and `col2`) connected by a horizontal bar, allowing for
    easy visual comparison between paired values.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    col1
        The column containing the first set of values to plot.

    col2
        The column containing the second set of values to plot.

    label
        Optional label to replace the column name of `col1` in the output table. If `None`, the
        original column name is retained.

    width
        The width of the dumbbell plot in pixels. Note that if the width is too narrow,
        some plot label text may overlap.

    height
        The height of the dumbbell plot in pixels.

    col1_color
        The color of the dots representing values from `col1`.

    col2_color
        The color of the dots representing values from `col2`.

    bar_color
        The color of the horizontal bar connecting the two dots.

    dot_border_color
        The color of the borders around the two dots.

    font_size
        The font size for the value labels displayed above each dot.

    num_decimals
        The number of decimal places to display in the value labels.

    Returns
    -------
    GT
        A `GT` object with dumbbell plots added to the specified columns. The `col2` column is
        hidden from the final table display.

    Examples
    -------
    ```{python}
    import pandas as pd
    from great_tables import GT, html, style, loc
    from great_tables.data import sp500
    import gt_extras as gte

    # Trim the data to December 2008
    df = sp500[["date", "open", "close"]].copy()
    df["date"] = pd.to_datetime(df["date"], errors='coerce')

    dec_2008 = df[
        (df["date"].dt.month == 12) &
        (df["date"].dt.year == 2008)
    ]
    dec_2008 = dec_2008.iloc[::-1].iloc[2:11]

    # Make the Great Table
    gt = (
        GT(dec_2008)
        .tab_source_note(html("Purple: Open<br>Green: Close"))
        .tab_style(
            style=style.text(align="right"),
            locations=[loc.source_notes()]
        )
    )

    gt.pipe(
        gte.gt_plt_dumbbell,
        col1='open',
        col2='close',
        label = "Open to Close ($)",
        num_decimals=0,
        width = 250,
    )

    ```

    Note
    -------
    All dumbbells are scaled to a common range for visual alignment across rows.
    The `col2` column is automatically hidden from the final table display.
    """

    def _make_dumbbell_svg(
        value_1: float,
        value_2: float,
        width: float,
        height: float,
        value_1_color: str,
        value_2_color: str,
        bar_color: str,
        dot_border_color: str,
        max_val: float,
        min_val: float,
        font_size: int,
        num_decimals: int,
    ) -> str:
        if is_na(gt._tbl_data, value_1) or is_na(gt._tbl_data, value_2):
            return f'<div style="display: flex;"><div style="width:{width}px; height:{height}px;"></div></div>'

        # Normalize positions based on global min/max, then scale to width
        span = max_val - min_val
        span = span if span != 0 else 1  # span == 0 is forbidden, causes divide by 0
        pos_1 = ((value_1 - min_val) / span) * width
        pos_2 = ((value_2 - min_val) / span) * width

        # Compute the location of the bar
        bar_left = min(pos_1, pos_2)
        bar_width = abs(pos_2 - pos_1)
        bar_height = height / 10
        bar_y = height / 2 - bar_height / 2 + font_size / 2

        # Compute the locations of the two dots
        dot_radius = bar_height * 1.25
        dot_border = bar_height / 2
        dot_y = bar_y + bar_height / 2

        # Text positioning - labels above dots
        label_y = dot_y - dot_radius - dot_border * 1.2  # 1.2 for padding

        # Format the label text
        value_1_text = (
            f"{value_1:.{num_decimals}f}"
            if num_decimals == 0
            else f"{value_1:.{num_decimals}f}".rstrip("0").rstrip(".")
        )
        value_2_text = (
            f"{value_2:.{num_decimals}f}"
            if num_decimals == 0
            else f"{value_2:.{num_decimals}f}".rstrip("0").rstrip(".")
        )

        elements = [
            # Connecting bar
            Rect(
                x=bar_left,
                y=bar_y,
                width=bar_width,
                height=bar_height,
                fill=bar_color,
                rx=2,
            ),
            # Value 1 dot
            Circle(
                cx=pos_1,
                cy=dot_y,
                r=dot_radius,
                fill=value_1_color,
                stroke=dot_border_color,
                stroke_width=dot_border,
            ),
            # Value 2 dot
            Circle(
                cx=pos_2,
                cy=dot_y,
                r=dot_radius,
                fill=value_2_color,
                stroke=dot_border_color,
                stroke_width=dot_border,
            ),
            # Value 1 label
            Text(
                text=value_1_text,
                x=pos_1,
                y=label_y,
                fill=value_1_color,
                font_size=font_size,
                font_weight="bold",
                text_anchor="middle",
                dominant_baseline="lower",
            ),
            # Value 2 label
            Text(
                text=value_2_text,
                x=pos_2,
                y=label_y,
                fill=value_2_color,
                font_size=font_size,
                font_weight="bold",
                text_anchor="middle",
                dominant_baseline="lower",
            ),
        ]

        svg = SVG(width=width, height=height, elements=elements)
        return f'<div style="display: flex;">{svg.as_str()}</div>'

    col1_name, col1_vals = _validate_and_get_single_column(
        gt,
        col1,
    )
    col2_name, col2_vals = _validate_and_get_single_column(
        gt,
        col2,
    )

    # Check for bad input
    all_values = [val for val in [*col1_vals, *col2_vals] if val is not None]
    if any(val is not None and not isinstance(val, (int, float)) for val in all_values):
        raise ValueError("Expected all entries to be numeric or None.")

    # Compute the global bounds for the column.
    data_min = min(all_values)
    data_max = max(all_values)
    data_range = data_max - data_min

    padding = data_range * 0.1  # Add 10% padding on each side
    global_min = data_min - padding
    global_max = data_max + padding

    res = gt

    for i in range(len(gt._tbl_data)):
        col1_value = col1_vals[i]
        col2_value = col2_vals[i]

        res = res.fmt(
            lambda _, value_1=col1_value, value_2=col2_value: _make_dumbbell_svg(
                value_1=value_1,
                value_2=value_2,
                width=width,
                height=height,
                value_1_color=col1_color,
                value_2_color=col2_color,
                bar_color=bar_color,
                dot_border_color=dot_border_color,
                max_val=global_max,
                min_val=global_min,
                font_size=font_size,
                num_decimals=num_decimals,
            ),
            columns=col1_name,
            rows=[i],
        )

    res = res.cols_hide(col2_name)
    if label is not None:
        res = res.cols_label({col1_name: label})

    return res


def gt_plt_winloss(
    gt: GT,
    column: SelectExpr,
    width: float = 80,
    height: float = 30,
    win_color: str = "blue",
    loss_color: str = "red",
    tie_color: str = "grey",
    shape: Literal["pill", "square"] = "pill",
    spacing: float = 2,
) -> GT:
    """
    Create win/loss charts in `GT` cells.

    The `gt_plt_winloss()` function takes an existing `GT` object and adds win/loss sparkline
    charts to a specified column. Each cell displays a series of small vertical bars representing
    individual game outcomes, This visualization is useful for showing performance streaks and
    patterns over time. All win/loss charts are scaled to accommodate the longest sequence in the
    column, ensuring consistent bar spacing across all rows.

    Wins must be represented as `1`, ties as `0.5`, and losses as `0`.
    Invalid values (not `0`, `0.5`, or `1`) are skipped.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    column
        The column containing lists of win/loss/tie values. Each cell should contain a list where:
        `1` represents a win, `0` represents a loss, and `0.5` represents a tie.
        Values that are not listed above are skipped.

    width
        The width of the win/loss chart in pixels.

    height
        The height of the win/loss chart in pixels.

    win_color
        The color for bars representing wins.

    loss_color
        The color for bars representing losses.

    tie_color
        The color for bars representing ties.

    shape
        The shape style of the bars. Options are `"pill"` for taller bars or `"square"` for
        stockier, nearly square bars.

    spacing
        The horizontal gap, in pixels, between each bar. Note that if the spacing is too large, it
        may obstruct the bars from view.

    Returns
    -------
    GT
        A `GT` object with win/loss charts added to the specified column.

    Examples
    --------
    First, let's make a table with randomly generated data:

    ```{python}
    from great_tables import GT, md
    import gt_extras as gte
    import pandas as pd

    df = pd.DataFrame(
        {
            "Team": ["Liverpool", "Chelsea", "Man City"],
            "10 Games": [
                [1, 1, 0, 1, 0.5, 1, 0, 1, 1, 0],
                [0, 0, 1, 0, 1, 1, 1, 0, 1, 1],
                [0.5, 1, 0.5, 0, 1, 0, 1, 0.5, 1, 0],
            ],
        }
    )

    gt = GT(df)

    gt.pipe(
        gte.gt_plt_winloss,
        column="10 Games",
        win_color="green",
    )
    ```

    Let's do a more involved example using NFL season data from 2016.

    ```{python}
    #| code-fold: true
    #| code-summary: Show the setup Code

    # Load the NFL data
    df = pd.read_csv("../assets/games.csv")
    season_2016 = df[(df["season"] == 2016) & (df["game_type"] == "REG")].copy()

    def get_team_results(games_df):
        results = {}

        for _, game in games_df.iterrows():
            away_team = game["away_team"]
            home_team = game["home_team"]
            away_score = game["away_score"]
            home_score = game["home_score"]

            if away_team not in results:
                results[away_team] = []
            if home_team not in results:
                results[home_team] = []

            if away_score > home_score:
                results[away_team].append(1)
                results[home_team].append(0)
            elif home_score > away_score:
                results[home_team].append(1)
                results[away_team].append(0)
            else:
                results[away_team].append(0.5)
                results[home_team].append(0.5)

        return results

    team_results = get_team_results(season_2016)
    winloss_df = pd.DataFrame(
        [{"Team": team, "Games": results} for team, results in team_results.items()]
    )

    winloss_df = (
        winloss_df
        .sort_values("Team")
        .reset_index(drop=True)
        .head(10)
    )
    ```

    Now that we've loaded the real-world data, let's see how we can use `gt_plt_winloss()`.

    ```{python}
    gt = (
        GT(winloss_df)
        .tab_header(
            title="2016 NFL Season",
        )
        .tab_source_note(
            md(
                '<span style="float: right;">Source: [Lee Sharpe, nflverse](https://github.com/nflverse/nfldata)</span>'
            )
        )
        .cols_align("left", columns="Games")
    )

    gt.pipe(
        gte.gt_plt_winloss,
        column="Games",
    )
    ```
    """

    def _make_winloss_svg(
        values: list[float],
        max_length: int,
        width: float,
        height: float,
        win_color: str,
        loss_color: str,
        tie_color: str,
        shape: Literal["pill", "square"],
        spacing: float,
    ) -> str:
        if len(values) == 0:
            return f'<div style="display: flex;"><div style="width:{width}px; height:{height}px;"></div></div>'

        available_width = width - (max_length) * spacing
        bar_width = available_width / max_length
        win_bar_height = height * 0.2 if shape == "square" else height * 0.4

        elements = []

        for i, value in enumerate(values):
            if is_na(gt._tbl_data, value):
                continue

            if value == 1:  # Win
                color = win_color
                bar_y = height * 0.2
                bar_height = win_bar_height
            elif value == 0.5:  # Tie
                color = tie_color
                bar_y = height * 0.4
                bar_height = height * 0.2
            elif value == 0:  # Loss
                color = loss_color
                bar_y = height * 0.8 - win_bar_height
                bar_height = win_bar_height
            else:
                warnings.warn(
                    f"Invalid value '{value}' encountered in win/loss data. Skipping.",
                    category=UserWarning,
                )
                continue

            bar_x = i * (bar_width + spacing)
            border_radius = 0.5 if shape == "square" else 2

            bar_rect = Rect(
                x=bar_x,
                y=bar_y,
                width=bar_width,
                height=bar_height,
                fill=color,
                rx=border_radius,
            )
            elements.append(bar_rect)

        svg = SVG(width=width, height=height, elements=elements)
        return f'<div style="display: flex;">{svg.as_str()}</div>'

    res = gt
    _, col_vals = _validate_and_get_single_column(gt, expr=column)
    max_length = max(len(entry) for entry in col_vals)

    if spacing * max_length >= width:
        warnings.warn(
            "Spacing is too large relative to the width. No bars will be displayed.",
            category=UserWarning,
        )

    # I don't have to loop like with the others since I dont need to access other columns
    res = res.fmt(
        lambda x: _make_winloss_svg(
            x,
            max_length=max_length,
            width=width,
            height=height,
            win_color=win_color,
            loss_color=loss_color,
            tie_color=tie_color,
            shape=shape,
            spacing=spacing,
        ),
        columns=column,
    )

    return res


def gt_plt_bar_stack(
    gt: GT,
    column: SelectExpr,
    labels: list[str] | None = None,
    width: float = 100,
    height: float = 30,
    palette: list[str] | str | None = None,
    font_size: int = 10,
    spacing: float = 2,
    num_decimals: int = 0,
    scale_type: Literal["relative", "absolute"] = "relative",
) -> GT:
    """
    Create stacked horizontal bar plots in `GT` cells.

    The `gt_plt_bar_stack()` function takes an existing `GT` object and adds stacked horizontal bar
    charts to a specified column. Each cell displays a series of horizontal bars whose lengths are
    proportional to the values in the list. The scaling of the bars can be controlled using the
    `scale_type` - see below for more info.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    column
        The column containing lists of numeric values to represent as stacked horizontal bars. Each
        cell should contain a list of numeric values.

    labels
        Optional labels for the bars. If provided, these labels will be displayed in the column
        header, with each label corresponding to a color in the palette.

    width
        The total width of the stacked bar plot in pixels. If `scale_type = "absolute"`, this
        value will determine the width of the maximum length bar plot.

    height
        The height of the stacked bar plot in pixels.

    palette
        The color palette to use for the bars. This can be a list of colors
        (e.g., `["#FF0000"`, `"#00FF00"`, `"#0000FF"` `]`) or a named palette (e.g., `"viridis"`).
        If `None`, a default palette will be used.

    font_size
        The font size for the text labels displayed on the bars.

    spacing
        The horizontal gap, in pixels, between each bar. If the spacing is too large relative to
        the width, a warning will be issued, and no bars will be displayed.

    num_decimals
        The number of decimal places to display in the text labels on the bars.

    scale_type
        Determines how the bars are scaled. Options are `"relative"` (bars are scaled relative to
        the sum of the values in each cell) and `"absolute"` (bars are scaled relative to the
        maximum value across all rows).

    Returns
    -------
    GT
        A `GT` object with stacked horizontal bar plots added to the specified column.

    Examples
    --------
    ```{python}
    import pandas as pd
    from great_tables import GT
    import gt_extras as gte

    df = pd.DataFrame({
        "x": ["Example A", "Example B", "Example C"],
        "col": [
            [10, 40, 50],
            [30, 30, 40],
            [50, 20, 30],
        ],
    })

    gt = GT(df)

    gt.pipe(
        gte.gt_plt_bar_stack,
        column="col",
        palette=["red", "grey", "black"],
        labels=["Group 1", "Group 2", "Group 3"],
        width=200,
    )
    ```

    If the absolute sum of each row varies, we can treat the rows as portions of a whole.

    ```{python}
    df = pd.DataFrame({
        "x": ["Example A", "Example B", "Example C"],
        "col": [
            [10, 20, 50],
            [30, 30],
            [50, 10, 10],
        ],
    })

    gt = GT(df)

    gt.pipe(
        gte.gt_plt_bar_stack,
        column="col",
        labels=["Group 1", "Group 2", "Group 3"],
        width=200,
        scale_type="relative",
    )
    ```

    Or we can treat them as absolute values.

    ```{python}
    df = pd.DataFrame({
        "x": ["Example A", "Example B", "Example C"],
        "col": [
            [10, 20, 50],
            [30, 30],
            [50, 10, 10],
        ],
    })

    gt = GT(df)

    gt.pipe(
        gte.gt_plt_bar_stack,
        column="col",
        labels=["Group 1", "Group 2", "Group 3"],
        width=200,
        scale_type="absolute",
    )
    ```

    Note
    -------
    Values of `0` will not be displayed in the plots.
    """

    def _make_bar_stack_svg(
        values: list[float],
        max_sum: float,
        width: float,
        height: float,
        colors: list[str],
        spacing: float,
        num_decimals: int,
        font_size: int,
        scale_type: Literal["relative", "absolute"],
    ) -> str:
        if not values:
            return f'<div style="display: flex;"><div style="width:{width}px; height:{height}px;"></div></div>'

        non_na_vals = [val if not is_na(gt._tbl_data, val) else 0 for val in values]
        # Count how many values will be displayed in the chart
        len_non_zero_values = sum(1 for val in non_na_vals if val != 0)

        if scale_type == "absolute":
            total = max_sum
        else:
            total = sum(non_na_vals)

        # Avoid div by 0
        if total == 0:
            total = 1

        normalized_values = [val / total for val in non_na_vals]
        available_width = width - (len_non_zero_values - 1) * spacing
        if available_width <= 0:
            warnings.warn(
                "Spacing is too large relative to the width. No bars will be displayed.",
                category=UserWarning,
            )
            return f'<div style="display: flex;"><div style="width:{width}px; height:{height}px;"></div></div>'

        elements = []
        current_left = 0

        for i, value in enumerate(normalized_values):
            if value == 0:
                continue

            bar_width = available_width * value
            color = colors[i % len(colors)]

            # Create the bar rectangle
            bar_rect = Rect(
                x=current_left,
                y=0,
                width=bar_width,
                height=height,
                fill=color,
            )
            elements.append(bar_rect)

            # Create the label text
            label = f"{non_na_vals[i]:.{num_decimals}f}"
            label_text = Text(
                text=label,
                x=current_left + bar_width / 2,  # Center horizontally in the bar
                y=height / 2,  # Center vertically
                fill=_ideal_fgnd_color(_html_color([color])[0]),
                font_size=font_size,
                text_anchor="middle",
                dominant_baseline="central",
            )
            elements.append(label_text)

            current_left += bar_width + spacing

        svg = SVG(width=width, height=height, elements=elements)
        return f'<div style="display: flex;">{svg.as_str()}</div>'

    # Throw if `scale_type` is not one of the allowed values
    if scale_type not in ["relative", "absolute"]:
        raise ValueError("Scale_type must be either 'relative' or 'absolute'")

    col_name, col_vals = _validate_and_get_single_column(gt, expr=column)
    cleaned_col_vals = [
        [val for val in col if val is not None and not is_na(gt._tbl_data, val)]
        for col in col_vals
        if col is not None
    ]

    max_sum = max(sum(col) for col in cleaned_col_vals if col is not None)
    max_num_values = max(len(col) for col in cleaned_col_vals)

    # If user passes a list, accept those colors, otherwise use palette functionality.
    if isinstance(palette, list) and len(palette) >= max_num_values:
        color_list = palette
    else:
        color_list = _get_discrete_colors_from_palette(
            palette=palette,
            data=[i for i in range(max_num_values)],
            data_table=gt._tbl_data,
        )

    res = gt
    res = res.fmt(
        lambda x: _make_bar_stack_svg(
            x,
            max_sum=max_sum,
            width=width,
            height=height,
            colors=color_list,
            spacing=spacing,
            font_size=font_size,
            num_decimals=num_decimals,
            scale_type=scale_type,
        ),
        columns=column,
    )

    if labels is not None:
        label_html = [
            f'<span style="color:{color}">{name}</span>'
            for name, color in zip(labels, color_list)
        ]
        label_html = " | ".join(label_html)
        res = res.cols_align(columns=col_name, align="center").cols_label(
            {col_name: html(label_html)}
        )

    return res


def gt_plt_bar_pct(
    gt: GT,
    column: SelectExpr,
    height: int = 16,
    width: int = 100,
    fill: str = "purple",
    background: str = "#e1e1e1",
    autoscale: bool = True,
    labels: bool = False,
    label_cutoff: float = 0.4,
    decimals: int = 1,
    font_style: Literal["oblique", "italic", "normal"] = "normal",
    font_size: int = 10,
):
    """
    Create horizontal bar plots in percentage in `GT` cells.

    The `gt_plt_bar_pct()` function takes an existing `GT` object and adds
    horizontal bar plots via native HTML. By default, values are normalized
    as a percentage of the maximum value in the specified column. If the values
    already represent percentages (i.e., between 0–100), you can disable this
    behavior by setting `autoscale=False`.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    column
        The column to target.

    height
        The height of the bar plot in pixels.

    width
        The width of the maximum bar in pixels.

    fill
        The fill color for the bars.

    background
        The background filling color for the bars. Defaults to `#e1e1e1`.

    autoscale
        Indicates whether the function should automatically scale the values.
        If `True`, values will be divided by the column's maximum and multiplied by 100.
        If `False`, the values are assumed to already be scaled appropriately.

    labels
        `True`/`False` logical representing if labels should be plotted. Defaults
        to `False`, meaning that no value labels will be plotted.

    label_cutoff
        A number, 0 to 1, representing where to set the inside/outside label
        boundary. Defaults to 0.40 (40%) of the column's maximum value. If the
        value in that row is less than the cutoff, the label will be placed
        outside the bar; otherwise, it will be placed within the bar. This
        interacts with the overall width of the bar, so if you are not happy with
        the placement of the labels, you may try adjusting the `width` argument as
        well.

    decimals
        A number representing how many decimal places to be used in label
        rounding.

    font_style
        The font style for the text labels displayed on the bars. Options are
        `"oblique"`, `"italic"`, or `"normal"`.

    font_size
        The font size for the text labels displayed on the bars.

    Returns
    -------
    GT
        A `GT` object with horizontal bar plots added to the specified columns.

    Examples
    --------
    The `autoscale` parameter is perhaps the most important in the `gt_plt_bar_pct()` function.
    This example demonstrates the difference between `autoscale=True` and `autoscale=False` using column `x`:

    * **When `autoscale=True`**:
    The function scales the values relative to the maximum in the column.
    For example, `[10, 20, 30, 40]` becomes `[25%, 50%, 75%, 100%]`,
    which are used for both bar lengths and labels.

    * **When `autoscale=False`**:
    The values are assumed to already represent percentages.
    The function uses them as-is — e.g., `[10%, 20%, 30%, 40%]`,
    which are directly reflected in both the bar lengths and labels.

    ```{python}
    import polars as pl
    from great_tables import GT
    import gt_extras as gte

    df = pl.DataFrame({"x": [10, 20, 30, 40]}).with_columns(
        pl.col("x").alias("autoscale_on"),
        pl.col("x").alias("autoscale_off"),
    )

    gt = GT(df)

    (
        gt.pipe(
            gte.gt_plt_bar_pct,
            column=["autoscale_on"],
            autoscale=True,
            labels=True,
            fill="green",
        ).pipe(
            gte.gt_plt_bar_pct,
            column=["autoscale_off"],
            autoscale=False,
            labels=True,
        )
    )
    ```
    Finally, label colors are automatically adjusted based on the `fill` and `background` parameters
    to ensure optimal readability.
    """

    def _not_na(val, tbl_data) -> bool:
        return val is not None and not is_na(tbl_data, val)

    def _is_na(val, tbl_data) -> bool:
        return not _not_na(val, tbl_data)

    def _is_effective_int(val) -> bool:
        return isinstance(val, int) or (isinstance(val, float) and val.is_integer())

    if not (0 <= label_cutoff <= 1):
        raise ValueError("Label_cutoff must be a number between 0 and 1.")

    if font_style not in ["bold", "italic", "normal"]:
        raise ValueError("Font_style must be one of 'bold', 'italic', or 'normal'.")

    # Helper function to make the individual bars

    def _make_bar_pct_html(
        # original_val: int | float,
        scaled_val: int | float,
        height: int,
        width: int,
        fill: str,
        background: str,
        # autoscale: bool,
        labels: bool,
        label_cutoff: float,
        decimals: int,
        font_style: Literal["oblique", "italic", "normal"],
        font_size: int,
    ) -> str:
        elements = []
        if _is_na(scaled_val, tbl_data):
            outer_rect = Rect(
                x=0,
                y=0,
                width=Length(width, "%"),
                height=Length(height, "px"),
                fill="transparent",
            )
            elements.append(outer_rect)
        else:
            outer_rect = Rect(
                x=0,
                y=0,
                width=Length(width, "px"),
                height=Length(height, "px"),
                fill=background,
            )
            elements.append(outer_rect)

            _width = width * scaled_val * 0.01

            inner_rect = Rect(
                x=0,
                y=0,
                width=Length(_width, "px"),
                height=Length(height, "px"),
                fill=fill,
            )
            elements.append(inner_rect)

            if labels:
                padding = 5.0

                if _width < (label_cutoff * 100):
                    _x = _width + padding
                    _fill = _ideal_fgnd_color(_html_color([background])[0])
                else:
                    _x = padding
                    _fill = _ideal_fgnd_color(_html_color([fill])[0])

                _decimals = decimals
                if _is_effective_int(scaled_val):
                    _decimals = 0
                _text = f"{scaled_val:.{_decimals}f}%"

                inner_text = Text(
                    text=_text,
                    x=Length(_x, "px"),
                    y=Length(height / 2, "px"),
                    fill=_fill,
                    font_size=Length(font_size, "px"),
                    font_style=font_style,
                    text_anchor="start",
                    dominant_baseline="central",
                )
                elements.append(inner_text)

        canvas = SVG(
            width=Length(width, "px"),
            height=Length(height, "px"),
            elements=elements,
        )
        return f'<div style="display: flex;">{canvas.as_str()}</div>'

    def _make_bar_pct(scaled_val: int) -> str:
        return _make_bar_pct_html(
            # original_val=original_val,
            scaled_val=scaled_val,
            height=height,
            width=width,
            fill=fill,
            background=background,
            # autoscale=autoscale,
            labels=labels,
            label_cutoff=label_cutoff,
            decimals=decimals,
            font_style=font_style,
            font_size=font_size,
        )

    _, col_vals = _validate_and_get_single_column(gt, expr=column)
    tbl_data = gt._tbl_data
    if all(_is_na(val, tbl_data) for val in col_vals):
        raise ValueError("All values in the column are None.")

    max_x = max(val for val in col_vals if _not_na(val, tbl_data))

    scaled_vals = col_vals
    if autoscale:
        scaled_vals = [
            val if _is_na(val, tbl_data) else (val / max_x * 100) for val in col_vals
        ]

    res = gt
    # Apply the scaled value for each row, so the bar is proportional
    for i, scaled_val in enumerate(scaled_vals):
        res = res.fmt(
            lambda _, scaled_val=scaled_val: _make_bar_pct(scaled_val=scaled_val),
            columns=column,
            rows=[i],
        )
    return res


########### Helper functions that get reused across plots ###########


# Helper function to make the individual bars
def _make_bar_svg(
    scaled_val: float,
    original_val: int | float,
    fill: str,
    bar_height: float,
    height: float,
    width: float,
    stroke_color: str,
    show_labels: bool,
    label_color: str | None,
) -> SVG:
    text = ""
    if show_labels:
        text = str(original_val)

    elements = [
        Rect(
            x=0,
            y=Length((height - bar_height) / 2, "px"),
            width=Length(width * scaled_val, "px"),
            height=Length(bar_height, "px"),
            fill=fill,
            # onmouseover="this.style.fill= 'blue';",
            # onmouseout=f"this.style.fill='{fill}';",
        ),
        Text(
            text=text,
            x=Length((width * scaled_val) * 0.98, "px"),
            y=Length(height / 2, "px"),
            fill=label_color,
            font_size=bar_height * 0.6,
            text_anchor="end",
            dominant_baseline="central",
        ),
        Line(
            x1=0,
            x2=0,
            y1=0,
            y2=Length(height, "px"),
            stroke_width=Length(height / 10, "px"),
            stroke=stroke_color,
        ),
    ]

    return SVG(width=width, height=height, elements=elements)
