from __future__ import annotations

from great_tables import GT, style, loc, google_font

__all__ = ["gt_theme_538", "gt_theme_espn", "gt_theme_guardian", "gt_theme_nytimes", "gt_theme_excel"]

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
        .tab_style(style=style.text(weight="bold"), locations=loc.column_header())
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

def gt_theme_nytimes(gt: GT) -> GT:
    gt_themed = (
        gt.tab_options(
            heading_align="left",
            column_labels_border_top_style="none",
            table_border_top_style="none",
            column_labels_border_bottom_style="none",
            column_labels_border_bottom_width="1px",
            column_labels_border_bottom_color="#334422",
            table_body_border_top_style="none",
            table_body_border_bottom_color="white",
            heading_border_bottom_style="none",
            data_row_padding="7px",
            column_labels_font_size="12px",
        )
        .tab_style(
            style=style.text(
                color="darkgrey",
                font=google_font("Source Sans Pro"),
                transform="uppercase",
            ),
            locations=[loc.column_labels(), loc.stubhead()],
        )
        .tab_style(
            style=style.text(font=google_font("Libre Franklin"), weight=800),
            locations=loc.title(),
        )
        .tab_style(
            style=style.text(font=google_font("Source Sans Pro"), weight=400),
            locations=loc.body(),
        )
    )
    return gt_themed

def gt_theme_guardian(gt: GT) -> GT:
    gt_themed = (
        gt.opt_table_font(font=[google_font("Noto Sans")])
        .tab_style(
            ## style hidden or weight 0px?
            style=style.borders(sides="top", color="white", style="hidden"),
            # A place we might see a difference from R – I've tested it and it should work the same
            locations=loc.body(rows=0),
        )
        .tab_style(
            style=style.text(color="#005689", size="22px", weight=700),
            locations=loc.title(),
        )
        .tab_style(
            style=style.text(color="#005689", size="16px", weight=700),
            locations=loc.subtitle(),
        )
        .tab_options(
            row_striping_include_table_body=True,
            table_background_color="#f6f6f6",
            row_striping_background_color="#ececec",
            column_labels_background_color="#f6f6f6",
            column_labels_font_weight="bold",
            table_border_top_width="1px",
            table_border_top_color="#40c5ff",
            table_border_bottom_width="3px",
            table_border_bottom_color="white",
            source_notes_border_bottom_width="0px",
            table_body_border_bottom_width="3px",
            table_body_border_bottom_color="white",
            table_body_hlines_width="white",
            table_body_hlines_color="white",
            row_group_border_top_width="1px",
            row_group_border_top_color="grey",
            row_group_border_bottom_width="1px",
            row_group_border_bottom_color="grey",
            row_group_font_weight="bold",
            column_labels_border_top_width="1px",
            
            # Slight modification from the R version:
            column_labels_border_top_color="#ececec" if gt._heading.title else "#40c5ff",
            
            column_labels_border_bottom_width="2px",
            column_labels_border_bottom_color="#ececec",
            heading_border_bottom_width="0px",
            data_row_padding="4px",
            source_notes_font_size="12px",
            table_font_size="16px",
            heading_align="left",
        )

        # this replaces footnotes_border_bottom_width="0px", because that functionality doesn't
        # exist in the Python API
        .tab_style(style=style.borders(sides="bottom", style="hidden"), locations=loc.footer()) 
    )
    return gt_themed

def gt_theme_excel(gt: GT, color: str = "lightgrey") -> GT:
    # n_cols = len(gt._tbl_data.columns)
    # n_rows = len(gt._tbl_data.rows)

    gt_themed = (
        gt.opt_row_striping()
        .tab_style(
            style=style.borders(sides="all", weight="1px", color="black"),
            locations=loc.body(),
        )

        # .tab_style(
        #     style=style.borders(sides="left", weight="2px", color="black"),
        #     locations=[
        #         loc.body(columns=0),
        #         loc.column_labels(columns=0),
        #         loc.stub()
        #     ],
        # )

        # .tab_style(
        #     style=style.borders(sides="left", weight="1px", color="black"),
        #     locations=loc.row_groups(),
        # )

        # .tab_style(
        #     style=style.borders(sides="right", weight="2px", color="black"),
        #     locations=[
        #         loc.body(columns=n_cols - 1),
        #         loc.column_labels(columns=n_cols - 1),
        #         loc.row_groups()
        #     ],
        # )

        # .tab_style(
        #     style=style.borders(sides="bottom", weight="2px", color="black"),
        #     locations=[
        #         loc.body(rows=n_rows - 1),
        #         loc.stub(rows=n_rows - 1)
        #     ],
        # )
        .opt_table_font(font="Calibri")
        .tab_options(
            heading_align="left",
            heading_border_bottom_color="black",
            column_labels_background_color="black",
            column_labels_font_weight="bold",
            stub_background_color="white",
            stub_border_color="black",
            row_group_background_color="white",
            row_group_border_top_color="black",
            row_group_border_bottom_color="black",
            row_group_border_left_color="black",
            row_group_border_right_color="black",
            row_group_border_left_width="1px",
            row_group_border_right_width="1px",
            column_labels_font_size="85%",
            column_labels_border_top_style="none",
            column_labels_border_bottom_color="black",
            column_labels_border_bottom_width="2px",
            table_border_left_color="black",
            table_border_left_style="solid",
            table_border_right_style="solid",
            table_border_left_width="2px",
            table_border_right_width="2px",
            table_border_right_color="black",
            table_border_bottom_width="2px",
            table_border_bottom_color="black",
            table_border_top_width="2px",
            table_border_top_color="black",
            row_striping_background_color=color,
            table_body_hlines_color="black",
            table_body_vlines_color="black",
            data_row_padding="1px",
        )
    )
    return gt_themed

