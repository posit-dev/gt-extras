from __future__ import annotations

from great_tables import GT, style, loc, google_font

__all__ = ["gt_theme_538"]


def gt_theme_538(gt: GT) -> GT:
    gt_themed = (
        gt.opt_table_font(font=google_font("Cairo"), weight=400)
        .tab_style(
            style=style.text(font=google_font("Chivo"), weight=700),
            locations=loc.title(),
        )
        .tab_style(
            style=style.text(font=google_font("Chivo"), weight=300),
            locations=loc.subtitle(),
        )
        .tab_style(
            style=[
                style.borders(sides="top", color="black", weight="0px"),
                style.text(
                    font=google_font("Chivo"),
                    transform="uppercase",
                    v_align="bottom",
                    size="14px",
                    weight=200,
                ),
            ],
            locations=[loc.column_labels(), loc.stubhead()],
        )
        .tab_style(
            style=style.borders(sides="bottom", color="black", weight="1px"),
            locations=loc.row_groups(),
        )
        .tab_options(
            column_labels_background_color="white",
            data_row_padding="3px",
            heading_border_bottom_style="none",
            table_border_top_width="3px",
            table_border_top_style="none",
            table_border_bottom_style="none",
            column_labels_font_weight="normal",
            column_labels_border_top_style="none",
            column_labels_border_bottom_width="2px",
            column_labels_border_bottom_color="black",
            row_group_border_top_style="none",
            row_group_border_top_color="black",
            row_group_border_bottom_width="1px",
            row_group_border_bottom_color="white",
            stub_border_color="white",
            stub_border_width="0px",
            source_notes_font_size="12px",
            source_notes_border_lr_style="none",
            table_font_size="16px",
            heading_align="left",
        )
    )

    return gt_themed


def gt_theme_espn(gt: GT) -> GT:
    gt_themed = (
        gt.opt_all_caps()
        .opt_table_font(font=google_font("Lato"), weight=400)
        .opt_row_striping()
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.column_header()
        )
        .tab_options(
            row_striping_background_color="#fafafa",
            table_body_hlines_color="#f6f7f7",
            source_notes_font_size="12px",
            table_font_size="16px",
            heading_align="left",
            heading_title_font_size="24px",
            table_border_top_color="white",
            table_border_top_width="3px",
            data_row_padding="7px",
        )
    )

    return gt_themed
