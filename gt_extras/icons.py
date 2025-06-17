from __future__ import annotations
from typing import Literal

import faicons

__all__ = "fa_icon_repeat"


def fa_icon_repeat(
    name: str = "star",
    repeats: int = 1,
    fill: str | None = None,
    fill_opacity: str | None = None,
    stroke: str | None = None,
    stroke_width: str | None = None,
    stroke_opacity: str | None = None,
    height: str | None = None,
    width: str | None = None,
    margin_left: str | None = None,
    margin_right: str | None = None,
    position: str | None = None,
    title: str | None = None,
    a11y: Literal["deco", "sem"] | None = None,
) -> str:
    icon = faicons.icon_svg(
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

    repeated_icon = str(icon) * repeats

    return repeated_icon
