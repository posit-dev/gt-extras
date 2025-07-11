# Import objects from the module
from .colors import (
    gt_color_box,
    gt_highlight_cols,
    gt_highlight_rows,
    gt_hulk_col_numeric,
)
from .formatting import fmt_pct_extra, gt_duplicate_column
from .html import gt_merge_stack, with_hyperlink, with_tooltip
from .icons import fa_icon_repeat, gt_fa_rank_change, gt_fa_rating
from .images import add_text_img, img_header
from .plotting import (
    gt_plt_bar,
    gt_plt_bar_pct,
    gt_plt_bar_stack,
    gt_plt_conf_int,
    gt_plt_dot,
    gt_plt_dumbbell,
    gt_plt_winloss,
)
from .styling import gt_add_divider
from .themes import (
    gt_theme_538,
    gt_theme_dark,
    gt_theme_dot_matrix,
    gt_theme_espn,
    gt_theme_excel,
    gt_theme_guardian,
    gt_theme_nytimes,
    gt_theme_pff,
)

__all__ = [
    "gt_theme_538",
    "gt_theme_espn",
    "gt_theme_nytimes",
    "gt_theme_guardian",
    "gt_theme_excel",
    "gt_theme_dot_matrix",
    "gt_theme_dark",
    "gt_theme_pff",
    "gt_highlight_cols",
    "gt_highlight_rows",
    "gt_hulk_col_numeric",
    "gt_color_box",
    "fa_icon_repeat",
    "gt_fa_rank_change",
    "gt_fa_rating",
    "gt_plt_bar",
    "gt_plt_bar_pct",
    "gt_plt_dot",
    "gt_plt_conf_int",
    "gt_plt_dumbbell",
    "gt_plt_winloss",
    "gt_plt_bar_stack",
    "with_hyperlink",
    "with_tooltip",
    "gt_merge_stack",
    "fmt_pct_extra",
    "gt_duplicate_column",
    "add_text_img",
    "img_header",
    "gt_add_divider",
]
