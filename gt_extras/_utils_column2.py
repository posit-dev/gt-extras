from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from great_tables._gt_data import GTData
from great_tables._styles import FromColumn
from great_tables._tbl_data import PlExpr, _get_cell, eval_transform, n_rows

if TYPE_CHECKING:
    import polars as pl

    PlExpr = pl.Expr


@dataclass
class ColumnExtractor:
    data: GTData
    attr: str | FromColumn | PlExpr | Callable

    def _check_attr(self):
        attr = self.attr
        if not isinstance(attr, (str, FromColumn, PlExpr)) and not callable(attr):
            raise TypeError(
                f"{attr=} must be one of: str, FromColumn, PlExpr, or a callable"
            )

    def _eval_exprs_to_get_values(self) -> list[Any]:
        attr, data = self.attr, self.data
        n_row = n_rows(data)

        if isinstance(attr, str):
            vals = [attr for _ in range(n_row)]
        elif isinstance(attr, FromColumn):
            vals = []
            for row in range(n_row):
                val = _get_cell(data, row, attr.column)
                if attr.fn is not None:
                    vals.append(attr.fn(val))
                else:
                    vals.append(val)
        else:
            vals = eval_transform(data, attr)
        return vals

    def resolve(self) -> list[Any]:
        self._check_attr()
        return self._eval_exprs_to_get_values()
