from __future__ import annotations
from typing import Literal

import fontawesome as fa


def fa_icon_repeat(
    name: str = "star",
    repeats: int = 1,
    fill: str = "", # todo color
    fill_opacity: int = 1,
    stroke: str = "", # todo color
    stroke_width: int = 1,
    stroke_opacity: int = 1,
    height: str | None = None,
    width: str | None = None,
    margin_left: int | None = None,
    margin_right: int | None = None,
    position: Literal["relative"] | None = None, # todo opts
    title:  str | None = None,
    a11y: Literal["deco", "sem"] | None = None,
) -> str:
    res = fa.icons['thumbs-up']
    print(fa.icons[name])

    return res