from great_tables._utils_render_html import (
    create_columns_component_h,
    create_body_component_h,
    create_source_notes_component_h,
    create_heading_component_h
)


def assert_rendered_source_notes(snapshot, gt):
    built = gt._build_data("html")
    source_notes = create_source_notes_component_h(built)

    assert snapshot == source_notes


def assert_rendered_heading(snapshot, gt):
    built = gt._build_data("html")
    heading = create_heading_component_h(built)

    assert snapshot == heading


def assert_rendered_columns(snapshot, gt):
    built = gt._build_data("html")
    columns = create_columns_component_h(built)

    assert snapshot == str(columns)


def assert_rendered_body(snapshot, gt):
    built = gt._build_data("html")
    body = create_body_component_h(built)

    assert snapshot == body
