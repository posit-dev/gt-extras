from __future__ import annotations

import re
import tempfile
import webbrowser
from pathlib import Path
from typing import Literal

import pandas as pd
import polars as pl
from great_tables import GT
from great_tables._export import _create_temp_file_server
from great_tables._gt_data import Boxhead, ColInfo
from great_tables._tbl_data import SelectExpr, copy_frame, is_na

from gt_extras._utils_column import _validate_and_get_single_column

__all__ = ["fmt_pct_extra", "gt_duplicate_column", "gt_two_column_layout"]


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
    new_data_table = copy_frame(res._tbl_data)
    new_body = res._body.copy()

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

    # A little clunky, but I dont have any other solutions
    if isinstance(new_data_table, pd.DataFrame):
        new_data_table[new_col_name] = new_data_table[original_name]
        new_body.body[new_col_name] = new_body.body[original_name]

    elif isinstance(new_data_table, pl.DataFrame):
        new_data_table = new_data_table.with_columns(
            new_data_table[original_name].alias(new_col_name)
        )
        new_body.body = new_body.body.with_columns(
            new_body.body[original_name].alias(new_col_name)
        )

    else:
        raise TypeError(
            """Unsupported type.
            This function will only work if the underlying data is a Polars or Pandas dataframe."""
        )

    new_boxhead_list = list(res._boxhead._d) + [new_col_info]
    new_boxhead = Boxhead(new_boxhead_list)

    res = res._replace(_tbl_data=new_data_table, _boxhead=new_boxhead, _body=new_body)

    if after is None:
        res = res.cols_move_to_end(new_col_name)
    else:
        res = res.cols_move(new_col_name, after=after)

    return res


def gt_two_column_layout(
    gt1: GT,
    gt2: GT,
    table_header_from: Literal[1, 2] | None = None,
    target: Literal["save", "notebook", "browser"] = "browser",
) -> str:
    # TODO docstring
    """
    Returns
    --------
    The html layout is returned
    """

    def extract_tab_header_and_style(gt: GT) -> dict:
        """
        Extract the title, subtitle, and full style block from a GT object's HTML.
        """
        html = gt.as_raw_html()

        title = gt._heading.title if gt._heading.title else ""
        subtitle = gt._heading.subtitle if gt._heading.subtitle else ""

        # Extract the original table ID
        id_match = re.search(r'<div id="([^"]*)"', html)
        original_id = id_match.group(1) if id_match else ""

        # Extract the entire style block
        style_match = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
        style_content = style_match.group(1) if style_match else ""

        # Replace the original ID with "mycombinedtable" in the CSS
        if original_id:
            style_content = style_content.replace(f"#{original_id}", "#mycombinedtable")
            style_content = style_content.replace(
                "mycombinedtable table", "mycombinedtable div"
            )

        # Extract title and subtitle class/style information
        title_pattern = (
            r'<td[^>]*class="([^"]*gt_title[^"]*)"[^>]*(?:style="([^"]*)")?[^>]*>'
            + re.escape(title)
            + r"</td>"
        )
        title_match = re.search(title_pattern, html)
        if title_match:
            title_class = f"gt_table {title_match.group(1)}"
            title_inline_style = title_match.group(2) or ""
        else:
            title_class = ""
            title_inline_style = ""

        subtitle_pattern = (
            r'<td[^>]*class="([^"]*gt_subtitle[^"]*)"[^>]*(?:style="([^"]*)")?[^>]*>'
            + re.escape(subtitle)
            + r"</td>"
        )
        subtitle_match = re.search(subtitle_pattern, html)
        if subtitle_match:
            subtitle_class = f"gt_table {subtitle_match.group(1)}"
            subtitle_inline_style = subtitle_match.group(2) or ""
        else:
            subtitle_class = ""
            subtitle_inline_style = ""

        return {
            "title": title,
            "subtitle": subtitle,
            "title_class": title_class,
            "subtitle_class": subtitle_class,
            "title_style": title_inline_style,
            "subtitle_style": subtitle_inline_style,
            "style": style_content,
        }

    # Extract header data if specified
    if table_header_from == 1:
        header_data = extract_tab_header_and_style(gt1)
    elif table_header_from == 2:
        header_data = extract_tab_header_and_style(gt2)
    else:
        header_data = None

    # Build the header HTML if header data is available
    if header_data and (header_data["title"] or header_data["subtitle"]):
        header_html = f"""
        <style>
        {header_data["style"]}
        </style>
        """

        # Add title if it exists
        if header_data["title"]:
            header_html += f"""
            <div class="{header_data["title_class"]}"
                style="width:100%; {header_data["title_style"]}"
            >
                {header_data["title"]}
            </div>
            """

        # Add subtitle if it exists
        if header_data["subtitle"]:
            header_html += f"""
            <div class="{header_data["subtitle_class"]}"
                style="width:100%; {header_data["subtitle_style"]}">
                {header_data["subtitle"]}
            </div>
            """

        # Remove headers from the two tables
        gt1_no_header = gt1.tab_header(title=None, subtitle=None)
        table_1_html = gt1_no_header.as_raw_html()
        gt2_no_header = gt2.tab_header(title=None, subtitle=None)
        table_2_html = gt2_no_header.as_raw_html()

    else:
        header_html = ""
        table_1_html = gt1.as_raw_html()
        table_2_html = gt2.as_raw_html()

    # make the table html
    double_table_html = f"""
    <div id="mycombinedtable" style="display: inline-block; width: auto;">
        {header_html}
        <div style="overflow: auto; white-space: nowrap;">
            <div style="display: inline-block; margin-right: 1em;">
                {table_1_html}
            </div>
            <div style="display: inline-block;">
                {table_2_html}
            </div>
        </div>
    </div>
    """

    # do a show or save
    # based on code from great_tables `GT.show()`
    if target == "notebook":
        from IPython.core.display import display_html

        # https://github.com/ipython/ipython/pull/10962
        display_html(  # pyright: ignore[reportUnknownVariableType]
            double_table_html, raw=True, metadata={"text/html": {"isolated": True}}
        )
    elif target == "browser":
        with tempfile.TemporaryDirectory() as tmp_dir:
            f_path = Path(tmp_dir) / "index.html"
            f_path.write_text(double_table_html, encoding="utf-8")

            # create a server that closes after 1 request ----
            server = _create_temp_file_server(f_path)
            webbrowser.open(f"http://127.0.0.1:{server.server_port}/{f_path.name}")
            server.handle_request()
    elif target == "save":
        # TODO save
        pass
    else:
        raise Exception(f"Unknown target display: {target}")

    return double_table_html
