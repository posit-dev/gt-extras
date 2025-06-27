from great_tables._utils_render_html import (
    create_columns_component_h,
    create_body_component_h,
    create_source_notes_component_h,
    create_heading_component_h,
)
from great_tables import GT, exibble

import pytest

__all__ = [
    "mini_gt",
    "assert_rendered_global_imports",
    "assert_rendered_source_notes",
    "assert_rendered_heading",
    "assert_rendered_columns",
    "assert_rendered_body",
]


@pytest.fixture(scope="module")
def mini_gt():
    mini_exibble = exibble.head(3)
    return GT(mini_exibble, id="mini_table")


def assert_rendered_global_imports(snapshot, gt: GT):
    html = gt.as_raw_html()
    global_imports = _extract_global_imports(html)
    assert snapshot == global_imports


def _extract_global_imports(html: str) -> str:
    start = html.find("<style>")
    end = html.find("</style>", start)
    if start == -1 or end == -1:
        return ""

    style_block = html[start:end]
    lines = [line.strip() for line in style_block.splitlines() if line.strip()]

    # Grab all @import lines
    import_lines = [line for line in lines if line.startswith("@import url")]

    return "\n".join(import_lines)


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
