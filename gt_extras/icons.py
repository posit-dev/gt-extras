from __future__ import annotations
from typing import Literal

from faicons import icon_svg

__all__ = "fa_icon_repeat"


def fa_icon_repeat(
    name: str = "star",
    repeats: int = 1,
    fill: str | None = "black",
    fill_opacity: int | str | None = 1,
    stroke: str | None = None,
    stroke_width: str | None = None,
    stroke_opacity: int | str | None = None,
    height: str | None = None,
    width: str | None = None,
    margin_left: str | None = "auto",
    margin_right: str | None = "0.2em",
    position: str | None = "relative",
    title: str | None = None,
    a11y: Literal["deco", "sem"] | None = "deco",
) -> str:
    """
    Create repeated FontAwesome SVG icons as HTML.

    The `fa_icon_repeat()` function generates one or more FontAwesome SVG icons using the `faicons`
    package and returns them as a single HTML string.

    Parameters
    ----------
    name
        The name of the FontAwesome icon to use (e.g., `"star"`, `"thumbs-up"`).

    repeats
        The number of times to repeat the icon.

    fill
        The fill color for the icon (e.g., `"yellow"`, `"#ffcc00"`). If `None`, uses the default.

    fill_opacity
        The opacity of the fill color (`0.0` - `1.0`).

    stroke
        The stroke color for the icon outline.

    stroke_width
        The width of the icon outline.

    stroke_opacity
        The opacity of the outline (`0.0` - `1.0`).

    height
        The height of the icon.

    width
        The width of the icon.

    margin_left
        The left margin for the icon.

    margin_right
        The right margin for the icon.

    position
        The CSS position property for the icon (e.g., `"absolute"`, `"relative"`, etc).

    title
        The title (tooltip) for the icon.

    a11y
        Accessibility mode: `"deco"` for decorative, `"sem"` for semantic.

    Returns
    -------
    str
        An HTML string containing the repeated SVG icons. If `repeats = 0`, this string will be empty.

    Examples
    --------
    ```{python}
    import pandas as pd
    from great_tables import GT
    import gt_extras as gte

    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Carol"],
        "Stars": [
            gte.fa_icon_repeat(name="star", repeats=3, fill="gold", fill_opacity=0.66),
            gte.fa_icon_repeat(name="star", repeats=2, fill="gold", stroke="black", stroke_width="3em"),
            gte.fa_icon_repeat(name="star", repeats=1, fill="orange"),
        ]
    })

    GT(df)
    ```

    Note
    --------
    See `icon_svg()` in the `faicons` package for further implementation details.
    """
    if repeats < 0:
        raise ValueError("repeats must be >= 0")

    icon = icon_svg(
        name=name,
        fill=fill,
        fill_opacity=fill_opacity,
        stroke=stroke,
        stroke_width=stroke_width,
        stroke_opacity=stroke_opacity,
        height=height,
        width=width,
        margin_left=margin_left,
        margin_right=margin_right,
        position=position,
        title=title,
        a11y=a11y,
    )

    repeated_icon = "".join(str(icon) for _ in range(repeats))

    return repeated_icon
