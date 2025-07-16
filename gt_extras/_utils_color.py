from __future__ import annotations

from great_tables._data_color.base import (
    _get_domain_factor,
    _html_color,
    _rescale_factor,
)
from great_tables._data_color.constants import ALL_PALETTES, DEFAULT_PALETTE
from great_tables._data_color.palettes import GradientPalette
from great_tables._tbl_data import TblData

__all__ = ["_get_discrete_colors_from_palette"]


def _get_discrete_colors_from_palette(
    palette: list[str] | str | None, data: list, data_table: TblData
) -> list[str | None]:
    # If palette is not provided, use a default palette
    if palette is None:
        palette = DEFAULT_PALETTE

    # Otherwise get the palette from great_tables._data_color
    elif isinstance(palette, str):
        palette = ALL_PALETTES.get(palette, [palette])

    # Standardize values in `palette` to hexadecimal color values
    palette = _html_color(colors=palette)

    # Rescale the category column for the purpose of assigning colors to each dot
    domain_factor = _get_domain_factor(df=data_table, vals=data)
    scaled_vals = _rescale_factor(
        df=data_table,
        vals=data,
        domain=domain_factor,  # type: ignore
        palette=palette,
    )

    # Create a color scale function from the palette
    color_scale_fn = GradientPalette(colors=palette)

    # Call the color scale function on the scaled categoy values to get a list of colors
    color_vals = color_scale_fn(scaled_vals)

    return color_vals
