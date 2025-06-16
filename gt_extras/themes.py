from __future__ import annotations

from great_tables import GT, style, loc, google_font

#empty commit

__all__ = [
    "gt_theme_538",
    "gt_theme_espn",
    "gt_theme_guardian",
    "gt_theme_nytimes",
    "gt_theme_excel",
    "gt_theme_dot_matrix",
    "gt_theme_dark",
    "gt_theme_pff",
]


def gt_theme_538(gt: GT) -> GT:
    """Applies a FiveThirtyEight-inspired theme to a GT table.

    This function styles a `GT` object with a look inspired by the FiveThirtyEight (538) website.

    Parameters
    ----------
    gt
        An existing `GT` object.

    Returns
    ----------
    GT
        The themed `GT` object, allowing for method chaining.

    Examples
    ----------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
        .tab_header(title="Car Collection")
    )

    gt.pipe(gte.gt_theme_538)
    ```
    """
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
        # Altered wrt R package
        # .tab_style(
        #     style=style.borders(sides="bottom", color="black", weight="1px"),
        #     locations=loc.row_groups(),
        # )
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
            # row_group_border_bottom_color="white", # Altered wrt R package
            row_group_border_bottom_color="black",  # Altered wrt R package
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
    """Applies an ESPN-inspired theme to a GT table.

    This function styles a `GT` object with a look inspired by ESPN's data tables.

    Parameters
    ----------
    gt
        An existing `GT` object.

    Returns
    -------
    GT
        The themed `GT` object, allowing for method chaining.

    Examples
    ----------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
        .tab_header(title="Car Collection")
    )

    gt.pipe(gte.gt_theme_espn)
    ```
    """
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
    """Applies a New York Times-inspired theme to a GT table.

    This function styles a `GT` object with a look inspired by New York Times tables.

    Parameters
    ----------
    gt
        An existing `GT` object.

    Returns
    -------
    GT
        The themed `GT` object, allowing for method chaining.

    Examples
    ----------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
        .tab_header(title="Car Collection")
    )

    gt.pipe(gte.gt_theme_nytimes)
    ```
    """
    gt_themed = (
        gt.tab_style(
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
        .tab_options(
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
    )
    return gt_themed


def gt_theme_guardian(gt: GT) -> GT:
    """Applies a Guardian-inspired theme to a GT table.

    This function styles a `GT` object with a look inspired by The Guardian's data tables.

    Parameters
    ----------
    gt
        An existing `GT` object.

    Returns
    -------
    GT
        The themed `GT` object, allowing for method chaining.

    Examples
    ----------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
        .tab_header(title="Car Collection")
    )

    gt.pipe(gte.gt_theme_guardian)
    ```
    """
    ## Altered wrt R package to not include whitespace between lines
    gt_themed = (
        gt.opt_table_font(font=[google_font("Noto Sans")])
        ## Altered wrt R package
        # .tab_style(
        #     ## style hidden or weight 0px?
        #     style=style.borders(sides="top", color="white", style="hidden"),
        #     ## A place we might see a difference from R
        #     locations=loc.body(rows=0),
        # )
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
            table_body_hlines_width="0px",  # Raise issue in gtExtras R
            table_body_hlines_color="white",
            row_group_border_top_width="1px",
            row_group_border_top_color="grey",
            row_group_border_bottom_width="1px",
            row_group_border_bottom_color="grey",
            row_group_font_weight="bold",
            column_labels_border_top_width="1px",
            # Slight modification from the R version:
            column_labels_border_top_color="#ececec"
            if gt._heading.title
            else "#40c5ff",
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
        .tab_style(
            style=style.borders(sides="bottom", style="hidden"), locations=loc.footer()
        )
    )
    return gt_themed


def gt_theme_excel(gt: GT, color: str = "lightgrey") -> GT:
    """Applies an Excel-inspired theme to a GT table.

    This function styles a `GT` object with a look inspired by Microsoft Excel tables.

    Parameters
    ----------
    gt
        An existing `GT` object.
    color
        A string indicating the color of the row striping, defaults to a light gray.
        Accepts either named colors or hex colors.

    Returns
    -------
    GT
        The themed `GT` object, allowing for method chaining.

    Examples
    ----------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
        .tab_header(title="Car Collection")
    )

    gt.pipe(gte.gt_theme_excel)
    ```
    """
    gt_themed = (
        gt.opt_row_striping()
        .tab_style(
            style=style.borders(sides="all", weight="1px", color="black"),
            locations=loc.body(),
        )
        # This does not appear to achieve anything
        # .tab_style(
        #     style=style.borders(sides="left", weight="2px", color="black"),
        #     locations=[
        #         loc.body(columns=0),
        #         loc.column_labels(columns=0),
        #         loc.stub()
        #     ],
        # )
        # This does not appear to achieve anything
        # .tab_style(
        #     style=style.borders(sides="left", weight="1px", color="black"),
        #     locations=loc.row_groups(),
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


def gt_theme_dot_matrix(gt: GT, color: str = "#b5dbb6") -> GT:
    """Applies a dot-matrix-inspired theme to a GT table.

    This function styles a `GT` object with a look reminiscent of dot-matrix printouts.

    Parameters
    ----------
    gt
        An existing `GT` object.
    color
        A string indicating the color of the row striping, defaults to a light green.
        Accepts either named colors or hex colors.

    Returns
    -------
    GT
        The themed `GT` object, allowing for method chaining.
    
    Examples
    ----------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
        .tab_header(title="Car Collection")
    )

    gt.pipe(gte.gt_theme_dot_matrix)
    ```
    """
    gt_themed = (
        gt.opt_row_striping()
        .opt_table_font(font="Courier")
        .tab_options(
            heading_align="left",
            heading_border_bottom_color="white",
            column_labels_text_transform="lowercase",
            column_labels_font_size="85%",
            column_labels_border_top_style="none",
            column_labels_border_bottom_color="black",
            column_labels_border_bottom_width="2px",
            table_border_bottom_style="none",
            table_border_bottom_width="2px",
            table_border_bottom_color="white",
            table_border_top_style="none",
            row_striping_background_color=color,
            table_body_hlines_style="none",
            table_body_vlines_style="none",
            data_row_padding="1px",
        )
    )

    return gt_themed


def gt_theme_dark(gt: GT) -> GT:
    """Applies a dark mode theme to a GT table.

    This function styles a `GT` object with a dark background and light text.

    Parameters
    ----------
    gt
        An existing `GT` object.

    Returns
    -------
    GT
        The themed `GT` object, allowing for method chaining.
    
    Examples
    ----------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
        .tab_header(title="Car Collection")
    )

    gt.pipe(gte.gt_theme_dark)
    ```
    """
    gt_themed = (
        gt.tab_style(
            style=style.text(
                color="white",
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
        .tab_options(
            heading_align="left",
            heading_border_bottom_style="none",
            table_background_color="#333333",
            table_font_color_light="white",
            table_border_top_style="none",
            table_border_bottom_color="#333333",
            table_border_left_color="#333333",
            table_border_right_color="#333333",
            table_body_border_top_style="none",
            table_body_border_bottom_color="#333333",
            column_labels_border_top_style="none",
            column_labels_background_color="#333333",
            column_labels_border_bottom_width="3px",
            column_labels_border_bottom_color="white",
            data_row_padding="7px",
        )
    )
    return gt_themed


def gt_theme_pff(
    gt: GT,
    divider: str | None = None,
    spanners: list[str] | None = None,
    rank_col: str | None = None,
) -> GT:
    """Applies a Pro Football Focus (PFF)-inspired theme to a GT table.

    This function styles a `GT` object with a look inspired by Pro Football Focus tables,
    supporting custom spanners, dividers, and rank column highlighting.

    Parameters
    ----------
    gt
        An existing `GT` object.
    divider
        Zero or more column names to visually divide with a preceding border.
    spanners
        Optional list of spanners to style, as referenced by the `GT` spanner ids.
    rank_col
        Optional single column name to highlight as a rank column.

    Returns
    -------
    GT
        The themed `GT` object, allowing for method chaining.

    Examples
    ----------
    ```{python}
    from great_tables import GT, md
    from great_tables.data import gtcars
    import gt_extras as gte

    gtcars_mini = gtcars[["model", "year", "hp", "trq"]].head(5)

    gt = (
        GT(gtcars_mini, rowname_col="model")
        .tab_stubhead(label=md("*Car*"))
        .tab_header(title="Car Collection")
    )

    gte.gt_theme_pff(gt, rank_col="trq")
    ```
    """
    gt_themed = (
        gt.opt_row_striping()
        .opt_all_caps()
        .tab_options(
            table_body_hlines_color="transparent",
            table_border_top_width="3px",
            table_border_top_color="transparent",
            table_border_bottom_color="lightgrey",
            table_border_bottom_width="1px",
            column_labels_border_top_width="3px",
            column_labels_padding="6px",
            column_labels_border_top_color="transparent",
            column_labels_border_bottom_width="3px",
            column_labels_border_bottom_color="transparent",
            row_striping_background_color="#f5f5f5",
            data_row_padding="6px",
            heading_align="left",
            heading_title_font_size="30px",
            heading_title_font_weight="bold",
            heading_subtitle_font_size="16px",
            table_font_size="12px",
        )
        .opt_table_font(font=google_font("Roboto"))
    )

    # Handle spanners if provided
    if spanners:
        span_cols = [col for spanner in gt._spanners for col in spanner.vars]

        # Add a blank spanner
        gt_themed = (
            gt_themed.tab_spanner(
                columns=[col for col in gt._boxhead._get_column_labels() if col not in span_cols],
                label=" ",
                id="blank",
            )
            .tab_style(
                style=[
                    style.fill(color="transparent"),
                    style.text(color="transparent", size="9px", weight="bold"),
                    style.borders(sides="left", color="transparent", weight="3px"),
                    style.borders(sides="top", color="transparent", weight="3px"),
                ],
                locations=loc.spanner_labels(ids=["blank"]),
            )
            # Add real spanners and style
            .tab_style(
                style=[
                    style.fill(color="#f5f5f5"),
                    style.text(color="#878e94", size="10px", weight="bold"),
                    style.borders(sides="left", color="white", weight="3px"),
                    style.borders(sides="top", color="white", weight="3px"),
                ],
                locations=loc.spanner_labels(ids=spanners),
            )
        )

    # Handle divider if provided
    if divider:
        gt_themed = gt_themed.tab_style(
            style=style.borders(sides="left", color="lightgrey", weight="2px"),
            locations=loc.body(columns=divider),
        ).tab_style(
            style=style.borders(sides="left", color="#212426", weight="2px"),
            locations=loc.column_labels(columns=divider),
        )

    # Handle rank_col if provided
    if rank_col:
        gt_themed = gt_themed.tab_style(
            style=[
                style.fill(color="#e4e8ec"),
                style.borders(color="#e4e8ec"),
            ],
            locations=loc.body(columns=rank_col),
        ).cols_align("center", columns=rank_col)

    gt_themed = gt_themed.tab_style(
        style=[
            style.fill(color="#585d63"),
            style.text(color="white", size="10px", weight="bold"),
            style.borders(sides="bottom", color="#585d63", weight="2.5px"),
        ],
        locations=[loc.column_labels(), loc.stubhead()],
    )

    return gt_themed
