from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from great_tables import GT, html
from great_tables._gt_data import FormatFns
from great_tables._helpers import px
from great_tables._tbl_data import Agnostic, DataFrameLike, PlExpr, SelectExpr, is_na
from great_tables._text import Html
from great_tables._utils import is_valid_http_schema

__all__ = ["add_text_img", "img_header", "gt_fmt_img_circle"]


def img_header(
    label: str,
    img_url: str,
    height: float = 60,
    font_size: int = 12,
    border_color: str = "black",
    text_color: str = "black",
) -> Html:
    """
    Create an HTML header with an image and a label, for a column label.

    Parameters
    ----------
    label
        The text label to display below the image.

    img_url
        The URL of the image to display. This can be a filepath or an image on the web.

    height
        The height of the image in pixels.

    font_size
        The font size of the label text.

    border_color
        The color of the border below the image.

    text_color
        The color of the label text.

    Returns
    -------
    html
        A Great Tables `html` element for the header.

    Examples
    -------
    ```{python}
    import pandas as pd
    from great_tables import GT, md
    import gt_extras as gte

    df = pd.DataFrame(
        {
            "Category": ["Points", "Rebounds", "Assists", "Blocks", "Steals"],
            "Hart": [1051, 737, 453, 27, 119],
            "Brunson": [1690, 187, 475, 8, 60],
            "Bridges": [1444, 259, 306, 43, 75],
        }
    )

    hart_header = gte.img_header(
        label="Josh Hart",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3062679.png",
    )

    brunson_header = gte.img_header(
        label="Jalen Brunson",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3934672.png",
    )

    bridges_header = gte.img_header(
        label="Mikal Bridges",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3147657.png",
    )

    (
        GT(df, rowname_col="Category")
        .tab_source_note(md("Images and data courtesy of [ESPN](https://www.espn.com)"))
        .cols_label(
            {
                "Hart": hart_header,
                "Brunson": brunson_header,
                "Bridges": bridges_header,
            }
        )
    )
    ```
    See Also
    -------
    [`add_text_img()`](https://posit-dev.github.io/gt-extras/reference/add_text_img)
    """

    img_html = f"""
    <img src="{img_url}" style="
        height:{px(height)};
        object-fit:contain;
        object-position: bottom;
        border-bottom:2px solid {border_color};"
    />
    """.strip()

    label_html = f"""
    <div style="
        font-size:{px(font_size)};
        color:{text_color};
        text-align:center;
        width:100%;
    ">
        {label}
    </div>
    """.strip()

    full_element = f"""
    <div style="text-align:center;">
        {img_html}
        {label_html}
    </div>
    """.strip()

    return html(full_element)


def add_text_img(
    text: str,
    img_url: str,
    height: int = 30,
    gap: float = 3.0,
    left: bool = False,
    alt_text: str = "",
) -> str:
    """
    Create an HTML element with text and an image, displayed inline.

    Note that depending on where
    you are placing the output in the table, you may want to wrap it in
    [`GT.html()`](https://posit-dev.github.io/great-tables/reference/html).

    Parameters
    ----------
    text
        The text to display alongside the image.

    img_url
        The URL of the image to display. This can be a filepath or an image on the web.

    height
        The height of the image in pixels.

    gap
        The spacing between the text and the image in pixels.

    left
        If `True`, the image is displayed to the left of the text.

    alt_text
        The alternative text for the image, used for accessibility and displayed if the image
        cannot be loaded.

    Returns
    -------
    str
        A string with html content of the combined image and text. Depending on where you are
        placing the output in the table, you may want to wrap it in
        [`GT.html()`](https://posit-dev.github.io/great-tables/reference/html).

    Examples
    --------
    ```{python}
    import pandas as pd
    from great_tables import GT, md, html
    import gt_extras as gte

    df = pd.DataFrame(
        {
            "Player": ["Josh Hart", "Jalen Brunson"],
            "Points": [1051, 1690],
            "Assists": [453, 475],
        }
    )

    hart_img = gte.add_text_img(
        text="Josh Hart",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3062679.png",
    )

    brunson_img = gte.add_text_img(
        text="Jalen Brunson",
        img_url="https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/3934672.png",
    )

    df["Player"] = [hart_img, brunson_img]
    gt = (
        GT(df, rowname_col="Player")
        .tab_source_note(md("Images and data courtesy of [ESPN](https://www.espn.com)"))
    )

    gt
    ```

    We can even apply the `add_text_img()` function to content outside of body/stub cells.
    We must remember to wrap the output in [`GT.html()`](https://posit-dev.github.io/great-tables/reference/html)
    so the table renders the element properly.

    ```{python}
    points_with_img = gte.add_text_img(
        text="Points",
        img_url="../assets/hoop.png",
        left=True,
    )

    assists_with_img = gte.add_text_img(
        text="Assists",
        img_url="../assets/pass.png",
        left=True,
    )

    points_img_html = html(points_with_img)
    assists_img_html = html(assists_with_img)

    (
        gt
        .cols_label({"Points": points_img_html, "Assists": assists_img_html})
        .cols_align("center")
    )
    ```
    See Also
    --------
    [`img_header()`](https://posit-dev.github.io/gt-extras/reference/img_header)
    """

    flex_direction = "row" if left else "row-reverse"

    combined_html = f"""
    <div style='display:flex; flex-direction:{flex_direction}; align-items:center; gap:{px(gap)};'>
        <div style='flex-shrink: 0;'>
            <img src='{img_url}' alt='{alt_text}'
            style='height:{px(height)}; width:auto; object-fit:contain;'/>
        </div>
        <div style='flex-grow:1;'>
            {text}
        </div>
    </div>
    """.strip()

    return combined_html


# Copied from https://github.com/posit-dev/great-tables/pull/676
def gt_fmt_img_circle(
    gt: GT,
    columns: SelectExpr = None,
    rows: int | list[int] | None = None,
    height: str | int | None = None,
    width: str | None = None,
    border_radius: str | None = "50%",
    border_width: str | int | None = None,
    border_color: str | None = None,
    border_style: str | None = None,
    sep: str = " ",
    path: str | Path | None = None,
    file_pattern: str = "{}",
    encode: bool = True,
) -> GT:
    """Format image paths to generate circular images within table cells.
    `gt_fmt_img_circle()` is a utility function similar to [`fmt_image()`](`great_tables.fmt_image`),
    but it also accepts additional parameters for customizing the image border:
    `border_radius=`, `border_width=`, `border_color=`, and `border_style=`.

    When calling `gt_fmt_img_circle()`, **Great Tables** automatically sets `border_radius="50%"` to
    create a full circle. However, we can't assume whether you want the border to be visible.
    Therefore, you should supply at least one of the following: `border_width=`, `border_color=`,
    or `border_style=`. Based on your input, sensible defaults will be applied for any unset border
    properties.

    Parameters
    ----------
    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list.
    rows
        In conjunction with `columns=`, we can specify which of their rows should undergo
        formatting. The default is all rows, resulting in all rows in targeted columns being
        formatted. Alternatively, we can supply a list of row indices.
    height
        The height of the rendered images.
    width
        The width of the rendered images.
    border_radius
        The radius of the image border. Accepts values in pixels (`px`) or percentages (`%`).
        Defaults to `50%` to create a circular image.
    border_width
        The width of the image border.
    border_color
        The color of the image border.
    border_style
        The style of the image border (e.g., solid, dashed, dotted).
    sep
        In the output of images within a body cell, `sep=` provides the separator between each
        image.
    path
        An optional path to local image files or an HTTP/HTTPS URL.
        This is combined with the filenames to form the complete image paths.
    file_pattern
        The pattern to use for mapping input values in the body cells to the names of the graphics
        files. The string supplied should use `"{}"` in the pattern to map filename fragments to
        input strings.
    encode
        The option to always use Base64 encoding for image paths that are determined to be local. By
        default, this is `True`.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    ```{python}
    import polars as pl
    from great_tables import GT, vals, html
    import gt_extras as gte

    rich_avatar = "https://avatars.githubusercontent.com/u/5612024?v=4"
    michael_avatar = "https://avatars.githubusercontent.com/u/2574498?v=4"
    jules_avatar = "https://avatars.githubusercontent.com/u/54960783?v=4"


    df = pl.DataFrame({"@machow": [michael_avatar], "@rich-iannone": [rich_avatar], "@juleswg23": [jules_avatar]})

    (
        GT(df)
        .cols_align("center")
        .opt_stylize(color="green", style=6)
        .pipe(gte.gt_fmt_img_circle, height=80)
    )
    ```
    """
    default_border_props = {
        "border-width": "3px",
        "border-color": "#0A0A0A",
        "border-style": "solid",
    }

    border_props = {
        "border-width": border_width,
        "border-color": border_color,
        "border-style": border_style,
    }

    # This block assigns default values to `border-width`, `border-color`, and `border-style`
    # if the user specifies at least one of them but leaves others unset.
    if any(border_props.values()):
        for k, v in default_border_props.items():
            if border_props[k] is None:
                border_props[k] = v

    border_width, border_color, border_style = border_props.values()

    return _fmt_image(
        gt,
        columns=columns,
        rows=rows,
        height=height,
        width=width,
        border_radius=border_radius,
        border_width=border_width,
        border_color=border_color,
        border_style=border_style,
        sep=sep,
        path=path,
        file_pattern=file_pattern,
        encode=encode,
    )


def _fmt_image(
    gt: GT,
    columns: SelectExpr = None,
    rows: int | list[int] | None = None,
    height: str | int | None = None,
    width: str | None = None,
    border_radius: str | None = None,
    border_width: str | int | None = None,
    border_color: str | None = None,
    border_style: str | None = None,
    sep: str = " ",
    path: str | Path | None = None,
    file_pattern: str = "{}",
    encode: bool = True,
) -> GT:
    # TODO: most parameter options should allow a polars expression (or from_column) ----
    # can other fmt functions do this kind of thing?
    expr_cols = [height, width, sep, path, file_pattern, encode]

    if any(isinstance(x, PlExpr) for x in expr_cols):
        raise NotImplementedError(
            "fmt_image currently does not support polars expressions for arguments other than"
            " columns and rows"
        )

    if height is None and width is None:
        height = "2em"

    formatter = FmtImage(
        gt._tbl_data,
        height=height,
        width=width,
        border_radius=border_radius,
        border_width=border_width,
        border_color=border_color,
        border_style=border_style,
        sep=sep,
        path=path,
        file_pattern=file_pattern,
        encode=encode,
    )
    return GT.fmt(
        gt,
        fns=FormatFns(
            html=formatter.to_html, latex=formatter.to_latex, default=formatter.to_html
        ),
        columns=columns,
        rows=rows,
    )


@dataclass
class FmtImage:
    dispatch_on: DataFrameLike | Agnostic = Agnostic()
    height: str | int | None = None
    width: str | None = None
    border_radius: str | None = None
    border_width: str | int | None = None
    border_color: str | None = None
    border_style: str | None = None
    sep: str = " "
    path: str | Path | None = None
    file_pattern: str = "{}"
    encode: bool = True
    SPAN_TEMPLATE: ClassVar = '<span style="white-space:nowrap;">{}</span>'

    def to_html(self, val: Any):
        # TODO: are we assuming val is a string? (or coercing?)

        # otherwise...

        if is_na(self.dispatch_on, val):
            return val

        if "," in val:
            files = re.split(r",\s*", val)
        else:
            files = [val]

        # TODO: if we allowing height and width to be set based on column values, then
        # they could end up as bespoke types like np int64, etc..
        # We should ensure we process those before hitting FmtImage
        if isinstance(self.height, (int, float)):
            height = px(self.height)
        else:
            height = self.height

        # TODO: note that only height can be numeric in the R program. Is this on purpose?
        # In any event, raising explicitly for numeric width below.
        if isinstance(self.width, (int, float)):
            raise NotImplementedError(
                "The `width=` argument must be specified as a string."
            )
        else:
            width = self.width

        if self.border_radius is not None:
            if not isinstance(self.border_radius, str):
                raise NotImplementedError(
                    "The `border_radius=` argument must be specified as a string."
                )
            if not any(self.border_radius.endswith(suffix) for suffix in {"px", "%"}):
                raise NotImplementedError(
                    'The `border_radius=` argument must end with either "px" or "%"'
                )

        border_radius = self.border_radius

        if isinstance(self.border_width, (int, float)):
            border_width = px(self.border_width)
        else:
            border_width = self.border_width

        border_color = self.border_color
        border_style = self.border_style

        full_files = self._apply_pattern(self.file_pattern, files)

        out: list[str] = []
        for file in full_files:
            # Case 1: from url via `dispatch_on`
            if self.path is None and is_valid_http_schema(file):
                uri = file.rstrip().removesuffix("/")
            # Case 2: from url via `path`
            elif self.path is not None and is_valid_http_schema(str(self.path)):
                norm_path = str(self.path).rstrip().removesuffix("/")
                uri = f"{norm_path}/{file}"
            # Case 3:
            else:
                filename = str((Path(self.path or "") / file).expanduser().absolute())

                if self.encode:
                    uri = self._get_image_uri(filename)
                else:
                    uri = filename

            # TODO: do we have a way to create tags, that is good at escaping, etc..?
            out.append(
                self._build_img_tag(
                    uri=uri,
                    height=height,
                    width=width,
                    border_radius=border_radius,
                    border_width=border_width,
                    border_color=border_color,
                    border_style=border_style,
                )
            )

        img_tags = self.sep.join(out)
        span = self.SPAN_TEMPLATE.format(img_tags)

        return span

    def to_latex(self, val: Any):
        from warnings import warn

        from ._gt_data import FormatterSkipElement

        warn("fmt_image() is not currently implemented in LaTeX output.")

        return FormatterSkipElement()

    @staticmethod
    def _apply_pattern(file_pattern: str, files: list[str]) -> list[str]:
        return [file_pattern.format(file) for file in files]

    @classmethod
    def _get_image_uri(cls, filename: str) -> str:
        import base64

        with open(filename, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        mime_type = cls._get_mime_type(filename)

        return f"data:{mime_type};base64,{encoded}"

    @staticmethod
    def _get_mime_type(filename: str) -> str:
        # note that we strip off the leading "."
        suffix = Path(filename).suffix[1:]

        if suffix == "svg":
            return "image/svg+xml"
        elif suffix == "jpg":
            return "image/jpeg"

        return f"image/{suffix}"

    @staticmethod
    def _build_img_tag(
        uri: str,
        height: str | None = None,
        width: str | None = None,
        border_radius: str | None = None,
        border_width: str | None = None,
        border_color: str | None = None,
        border_style: str | None = None,
    ) -> str:
        style_string = "".join(
            [
                f"height: {height};" if height is not None else "",
                f"width: {width};" if width is not None else "",
                f"border-radius: {border_radius};" if border_radius is not None else "",
                f"border-width: {border_width};" if border_width is not None else "",
                f"border-color: {border_color};" if border_color is not None else "",
                f"border-style: {border_style};" if border_style is not None else "",
                "vertical-align: middle;",
            ]
        )
        return f'<img src="{uri}" style="{style_string}">'
