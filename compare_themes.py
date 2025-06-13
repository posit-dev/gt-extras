import pandas as pd
from great_tables import GT
import gt_extras as gte
import os
import subprocess

theme_fns = [
    gte.gt_theme_538,
    gte.gt_theme_espn,
    gte.gt_theme_nytimes,
    gte.gt_theme_guardian,
    gte.gt_theme_excel,
    gte.gt_theme_dot_matrix,
    gte.gt_theme_dark,
    gte.gt_theme_pff
]

mtcars_url = "https://gist.githubusercontent.com/seankross/a412dfbd88b3db70b74b/raw/5f23f993cd87c283ce766e7ac6b329ee7cc2e1d1/mtcars.csv"
mtcars = pd.read_csv(mtcars_url)
mtcars_head = mtcars.head(6)

python_tables = []
r_tables = []

for theme_fn in theme_fns:
    theme_name = theme_fn.__name__
    ## align database to mtcars from R
    gt = GT(mtcars_head.iloc[:, 1:], rowname_col="mpg", groupname_col="carb")  

    ## make gt
    gt_with_header = gt.tab_header(title=f"Theme: {theme_name}")
    themed_tab = gt_with_header.pipe(theme_fn)

    ## save themed gt in file, then write to group file
    py_html = themed_tab.as_raw_html()
    python_tables.append((theme_name, py_html))

    ## The r-script executes the same as the python code but using gtExtras instead of this package
    r_script = f"""
library(gt)
library(dplyr)
library(gtExtras)

apply_gt_theme <- function(data, theme_fn) {{
  theme_name <- deparse(substitute(theme_fn))
  themed_tab <- data %>%
    gt(rowname_col="mpg", groupname_col="carb") %>%
    tab_header(title = paste("Theme:", theme_name)) %>%
    theme_fn()
  return(themed_tab)
}}

themed_tab <- apply_gt_theme(head(mtcars), {theme_name})
gtsave(themed_tab, "tableR_{theme_name}.html")
"""
    subprocess.run(["Rscript", "-"], input=r_script.encode("utf-8"), check=True)
    r_html_file = f"tableR_{theme_name}.html"
    with open(r_html_file) as f:
        r_tables.append((theme_name, f.read()))
    os.remove(r_html_file)

# Combine all tables into one HTML file
table_blocks = ""
for (theme_name, py_html), (_, r_html) in zip(python_tables, r_tables):
    table_blocks += f"""
    <div class="container">
        <div class="table-block">
            <h2>Python: {theme_name}</h2>
            {py_html}
        </div>
        <div class="table-block">
            <h2>R: {theme_name}</h2>
            {r_html}
        </div>
    </div>
    """

combined_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Python vs R Table Theme Comparison</title>
    <style>
        .container {{
            display: flex;
            gap: 5px;
        }}
        .table-block {{
            flex: 1;
        }}
    </style>
</head>
<body>
    <h1>Python vs R Table Theme Comparison</h1>
    {table_blocks}
</body>
</html>
"""

with open("compare_tables.html", "w") as f:
    f.write(combined_html)

os.system("open compare_tables.html")
