from __future__ import annotations
from typing import Literal
import warnings

from great_tables import GT
from great_tables._tbl_data import SelectExpr, is_na
from great_tables._locations import resolve_cols_c

from gt_extras._utils_column import (
    _validate_and_get_single_column,
    _scale_numeric_column,
)

from great_tables._data_color.palettes import GradientPalette
from great_tables._data_color.constants import DEFAULT_PALETTE, ALL_PALETTES
from great_tables._data_color.base import (
    _html_color,
    _rescale_factor,
    _get_domain_factor,
)

from svg import SVG, Line, Rect, Text

from scipy.stats import t, sem, tmean


__all__ = ["gt_plt_bar", "gt_plt_dot", "gt_plt_conf_int", "gt_plt_dumbbell"]

# TODO: keep_columns - this is tricky because we can't copy cols in the gt object, so we will have
# to handle the underlying _tbl_data.

# TODO: default font for labels?

# TODO: how to handle negative values? Plots can't really have negative length


def gt_plt_bar(
    gt: GT,
    columns: SelectExpr = None,
    fill: str = "purple",
    bar_height: int = 20,
    height: int = 30,
    width: int = 60,
    stroke_color: str | None = "black",
    scale_type: Literal["percent", "number"] | None = None,
    scale_color: str = "white",
    domain: list[int] | list[float] | None = None,
    # keep_columns: bool = False,
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
        The columns to target. Can be a single column name or a list of column names. If `None`,
        the bar plot is applied to all numeric columns.

    fill
        The fill color for the bars.

    bar_height
        The height of each individual bar in pixels.

    height
        The height of the bar plot in pixels.

    width
        The width of the maximum bar in pixels

    stroke_color
        The color of the vertical axis on the left side of the bar. The default is black, but if
        `None` is passed no stroke will be drawn.

    scale_type
        The type of value to show on bars. Options are `"number"`, `"percent"`, or `None` for no
        labels.

    scale_color
        The color of text labels on the bars (when `scale_type` is not `None`).

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
    # A version with svg.py

    # Throw if `scale_type` is not one of the allowed values
    if scale_type not in [None, "percent", "number"]:
        raise ValueError("Scale_type must be one of `None`, 'percent', or 'number'")

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

    # Helper function to make the individual bars
    def _make_bar_html(
        scaled_val: int,
        original_val: int,
        fill: str,
        bar_height: int,
        height: int,
        width: int,
        stroke_color: str,
        scale_type: Literal["percent", "number"] | None,
        scale_color: str,
    ) -> str:
        UNITS = "px"  # TODO: let use control this?

        text = ""
        if scale_type == "percent":
            text = str(round(original_val * 100)) + "%"
        if scale_type == "number":
            text = original_val

        canvas = SVG(
            width=str(width) + UNITS,
            height=str(height) + UNITS,
            elements=[
                Rect(
                    x=0,
                    y=str((height - bar_height) / 2) + UNITS,
                    width=str(width * scaled_val) + UNITS,
                    height=str(bar_height) + UNITS,
                    fill=fill,
                    # onmouseover="this.style.fill= 'blue';",
                    # onmouseout=f"this.style.fill='{fill}';",
                ),
                Text(
                    text=text,
                    x=str((width * scaled_val) * 0.98) + UNITS,
                    y=str(height / 2) + UNITS,
                    fill=scale_color,
                    font_size=bar_height * 0.6,
                    text_anchor="end",
                    dominant_baseline="central",
                ),
                Line(
                    x1=0,
                    x2=0,
                    y1=0,
                    y2=str(height) + UNITS,
                    stroke_width=str(height / 10) + UNITS,
                    stroke=stroke_color,
                ),
            ],
        )
        return f'<div style="display: flex;">{canvas.as_str()}</div>'

    # Allow the user to hide the vertical stroke
    if stroke_color is None:
        stroke_color = "#FFFFFF00"

    def _make_bar(scaled_val: int, original_val: int) -> str:
        return _make_bar_html(
            scaled_val=scaled_val,
            original_val=original_val,
            fill=fill,
            bar_height=bar_height,
            height=height,
            width=width,
            stroke_color=stroke_color,
            scale_type=scale_type,
            scale_color=scale_color,
        )

    # Get names of columns
    columns_resolved = resolve_cols_c(data=gt, expr=columns)

    res = gt
    for column in columns_resolved:
        # Validate this is a single column and get values
        col_name, col_vals = _validate_and_get_single_column(
            gt,
            column,
        )

        scaled_vals = _scale_numeric_column(gt._tbl_data, col_name, col_vals, domain)

        # Apply the scaled value for each row, so the bar is proportional
        for i, scaled_val in enumerate(scaled_vals):
            res = res.fmt(
                lambda original_val, scaled_val=scaled_val: _make_bar(
                    original_val=original_val,
                    scaled_val=scaled_val,
                ),
                columns=column,
                rows=[i],
            )
    return res


def gt_plt_dot(
    gt: GT,
    category_col: SelectExpr,
    data_col: SelectExpr,
    domain: list[int] | list[float] | None = None,
    palette: list[str] | str | None = None,
) -> GT:
    """
    Create dot plots with thin horizontal bars in `GT` cells.

    The `gt_plt_dot()` function takes an existing `GT` object and adds dot plots with horizontal
    bar charts to a specified category column. Each cell displays a colored dot with the category
    label and a horizontal bar representing the corresponding numeric value from the data column.

    Parameters
    ----------
    gt
        A `GT` object to modify.

    category_col
        The column containing category labels that will be displayed next to colored dots.

    data_col
        The column containing numeric values that will determine the length of the horizontal bars.

    domain
        The domain of values to use for the color scheme. This can be a list of floats or integers.
        If `None`, the domain is automatically set to `[0, max(data_col)]`.

    palette
        The color palette to use. This should be a list of colors
        (e.g., `["#FF0000", "#00FF00", "#0000FF"]`). A ColorBrewer palette could also be used,
        just supply the name (see [`GT.data_color()`](https://posit-dev.github.io/great-tables/reference/GT.data_color.html#great_tables.GT.data_color) for additional reference).
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

    gtcars_mini = gtcars.loc[8:20, ["model", "mfr", "hp", "trq", "mpg_c"]]

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label="Car")
    )

    gt.pipe(gte.gt_plt_dot, category_col="mfr", data_col="hp")
    ```
    """
    # Get the underlying Dataframe
    data_table = gt._tbl_data

    def _make_bottom_bar_html(
        val: float,
        fill: str,
    ) -> str:
        scaled_value = val * 100
        inner_html = f' <div style="background:{fill}; width:{scaled_value}%; height:4px; border-radius:2px;"></div>'
        html = f'<div style="flex-grow:1; margin-left:0px;"> {inner_html} </div>'

        return html

    def _make_dot_and_bar_html(
        bar_val: float,
        fill: str,
        dot_category_label: str,
    ) -> str:
        if is_na(data_table, bar_val) or is_na(data_table, dot_category_label):
            return "<div></div>"

        label_div_style = "display:inline-block; float:left; margin-right:0px;"

        dot_style = (
            f"height:0.7em; width:0.7em; background-color:{fill};"
            "border-radius:50%; margin-top:4px; display:inline-block;"
            "float:left; margin-right:2px;"
        )

        padding_div_style = (
            "display:inline-block; float:right; line-height:20px; padding:0px 2.5px;"
        )

        bar_container_style = "position:relative; top:1.2em;"

        html = f'''
        <div>
            <div style="{label_div_style}">
                {dot_category_label}
                <div style="{dot_style}"></div>
                <div style="{padding_div_style}"></div>
            </div>
            <div style="{bar_container_style}">
                <div>{_make_bottom_bar_html(bar_val, fill=fill)}</div>
            </div>
        </div>
        '''

        return html.strip()

    # Validate and get data column
    data_col_name, data_col_vals = _validate_and_get_single_column(
        gt,
        data_col,
    )

    # Process numeric data column
    scaled_data_vals = _scale_numeric_column(
        data_table, data_col_name, data_col_vals, domain
    )

    # Validate and get category column
    category_col_name, category_col_vals = _validate_and_get_single_column(
        gt,
        category_col,
    )

    # If palette is not provided, use a default palette
    if palette is None:
        palette = DEFAULT_PALETTE

    # Otherwise get the palette from great_tables._data_color
    elif isinstance(palette, str):
        palette = ALL_PALETTES.get(palette, [palette])

    # Standardize values in `palette` to hexadecimal color values
    palette = _html_color(colors=palette)

    # Rescale the category column for the purpose of assigning colors to each dot
    category_domain = _get_domain_factor(df=data_table, vals=category_col_vals)
    scaled_category_vals = _rescale_factor(
        df=data_table, vals=category_col_vals, domain=category_domain, palette=palette
    )

    # Create a color scale function from the palette
    color_scale_fn = GradientPalette(colors=palette)

    # Call the color scale function on the scaled categoy values to get a list of colors
    color_vals = color_scale_fn(scaled_category_vals)

    # Apply gt.fmt() to each row individually, so we can access the data_value for that row
    res = gt
    for i in range(len(data_table)):
        data_val = scaled_data_vals[i]
        color_val = color_vals[i]

        res = res.fmt(
            lambda x, data=data_val, fill=color_val: _make_dot_and_bar_html(
                dot_category_label=x, fill=fill, bar_val=data
            ),
            columns=category_col,
            rows=[i],
        )

    return res


# Changed wrt R version, palette removed


def gt_plt_conf_int(
    gt: GT,
    column: SelectExpr,
    ci_columns: SelectExpr | None = None,
    ci: float = 0.95,
    # or min_width? see: https://github.com/posit-dev/gt-extras/issues/53
    width: float = 100,
    height: float = 30,
    dot_color: str = "red",
    border_color: str = "red",
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
        The width of the confidence interval plot in pixels.

    height
        The width of the confidence interval plot in pixels.

    dot_color
        The color of the mean dot.

    border_color
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
    # TODO: comments
    # TODO: refactor? It's quite a long function
    # TODO: consider including height

    def _make_conf_int_html(
        mean: float,
        c1: float,
        c2: float,
        font_size: float,
        min_val: float,
        max_val: float,
        # or min_width? see: https://github.com/posit-dev/gt-extras/issues/53
        width: float,
        height: float,
        border_color: str,
        line_color: str,
        dot_color: str,
        text_color: str,
        num_decimals: int,
    ):
        if (
            is_na(gt._tbl_data, mean)
            or is_na(gt._tbl_data, c1)
            or is_na(gt._tbl_data, c2)
        ):
            return "<div></div>"

        span = max_val - min_val

        # Normalize positions to [0, 1] based on global min/max, then scale to width
        c1_pos = ((c1 - min_val) / span) * width
        c2_pos = ((c2 - min_val) / span) * width
        mean_pos = ((mean - min_val) / span) * width

        div_midpoint = height / 2

        bar_height = height / 10
        bar_top = div_midpoint + bar_height / 2

        label_bottom = height - bar_top

        dot_size = height / 5
        dot_top = bar_top - dot_size / 4
        dot_left = mean_pos - dot_size / 2

        label_style = (
            "position:absolute;"
            "left:{pos}px;"
            f"bottom:{label_bottom}px;"
            "color:{color};"
            "font-size:{font_size}px;"
        )

        c1_label_html = (
            f'<div style="{label_style.format(pos=c1_pos, color=text_color, font_size=font_size)}">'
            f"{c1:.{num_decimals}f}".rstrip("0").rstrip(".")
            + "</div>"
        )

        c2_label_html = (
            f'<div style="{label_style.format(pos=c2_pos, color=text_color, font_size=font_size)}'
            f'transform:translateX(-100%);">'  # Move c2 to the left
            f"{c2:.{num_decimals}f}".rstrip("0").rstrip(".")
            + "</div>"
        )

        html = f"""
            <div style="position:relative; width:{width}px; height:{height}px;">
            {c1_label_html}
            {c2_label_html}
            <div style="
                position:absolute; left:{c1_pos}px;
                top:{bar_top}px; width:{c2_pos - c1_pos}px;
                height:{bar_height}px; background:{line_color}; border-radius:2px;
            "></div>
            <div style="
                position:absolute; left:{dot_left}px;
                top:{dot_top}px; width:{dot_size}px; height:{dot_size}px;
                background:{dot_color}; border-radius:50%;
                border:2px solid {border_color}; box-sizing:border-box;
            "></div>
            </div>
            """
        return html.strip()

    data_column_resolved = resolve_cols_c(data=gt, expr=column)
    if len(data_column_resolved) != 1:
        raise ValueError(
            f"Expected 1 col in the column parameter, but got {len(data_column_resolved)}"
        )
    data_column_name = data_column_resolved[0]

    # must compute the ci ourselves
    if ci_columns is None:
        _, data_vals = _validate_and_get_single_column(
            gt,
            data_column_name,
        )

        # Check that all entries are lists or None
        if any(val is not None and not isinstance(val, list) for val in data_vals):
            raise ValueError(
                f"Expected entries in {data_column_name} to be lists or None,"
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

        _, means = _validate_and_get_single_column(
            gt,
            data_column_name,
        )

        if any(val is not None and not isinstance(val, (int, float)) for val in means):
            raise ValueError(
                f"Expected all entries in {data_column_name} to be numeric or None,"
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
            lambda _, c1=c1, c2=c2, mean=mean: _make_conf_int_html(
                mean=mean,
                c1=c1,
                c2=c2,
                font_size=font_size,
                min_val=global_min,
                max_val=global_max,
                width=width,
                height=height,
                border_color=border_color,
                line_color=line_color,
                dot_color=dot_color,
                text_color=text_color,
                num_decimals=num_decimals,
            ),
            columns=data_column_name,
            rows=[i],
        )

    return res


def gt_plt_dumbbell(
    gt: GT,
    col1: SelectExpr,  # exactly 1 col
    col2: SelectExpr,  # exactly 1 col
    label: str,
    width: float | int = 70,
    col1_color: str = "purple",
    col2_color: str = "green",
    bar_color: str = "grey",
    text_size: Literal["small", "default", "large", "largest", "none"] = "default",
) -> GT:
    def _make_dumbbell_html(
        value_1: float | int,
        value_2: float | int,
        value_1_color: str,
        value_2_color: str,
        bar_color: str,
        width: float | int,
        height: float | int,
        max_val: float | int,
        min_val: float | int,
        font_size: float | int,
    ) -> str:
        if is_na(gt._tbl_data, value_1) or is_na(gt._tbl_data, value_2):
            return "<div></div>"

        # Normalize positions based on global min/max, then scale to width
        span = max_val - min_val
        pos_1 = ((value_1 - min_val) / span) * width
        pos_2 = ((value_2 - min_val) / span) * width

        # Calculate bar position and width
        bar_left = pos_1
        bar_width = pos_2 - pos_1

        # TODO: compute based on text size
        bar_top = "60%"  # 50% if no text

        label_style = (
            "position:absolute; left:{pos}px; bottom:0px;"
            f"transform:translate3d(-50%, {-height / 2}px, 0);"
            "color:{color}; font-size:{font_size}px; font-weight:bold;"
        )

        value_1_label = (
            f'<div style="{label_style.format(pos=pos_1, color=value_1_color, font_size=font_size)}">'
            f"{value_1:.1f}"
            "</div>"
        )

        value_2_label = (
            f'<div style="{label_style.format(pos=pos_2, color=value_2_color, font_size=font_size)}">'
            f"{value_2:.1f}"
            "</div>"
        )

        dot_style = (
            "position:absolute; left:{pos}px;"
            f"top:{bar_top}; width:{height / 3}px; height:{height / 3}px;"
            "transform: translate3d(-50%, -35%, 0px);"
            "background:{color}; border-radius:50%;"
            "border:2px solid white; box-sizing:border-box;"
        )

        value_1_dot = (
            f'<div style="{dot_style.format(pos=pos_1, color=value_1_color)}"></div>'
        )
        value_2_dot = (
            f'<div style="{dot_style.format(pos=pos_2, color=value_2_color)}"></div>'
        )

        html = f"""
        <div style="position: relative; width:{width}px; height:{height}px;">
            {value_1_label}
            {value_2_label}
            <div style="
                position: absolute;
                left: {bar_left}px;
                top: {bar_top};
                width: {bar_width}px;
                height: {height / 10}px;
                background: {bar_color};
                border-radius: 2px;
            "></div>
            {value_1_dot}
            {value_2_dot}
        </div>
        """
        return html.strip()

    res = gt
    return res
