# gt-extras

[![Python Versions](https://img.shields.io/pypi/pyversions/gt_extras.svg)](https://pypi.python.org/pypi/gt-extras)
[![PyPI](https://img.shields.io/pypi/v/gt-extras?logo=python&logoColor=white&color=orange)](https://pypi.org/project/gt-extras/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gt-extras)](https://pypistats.org/packages/gt-extras)
[![License](https://img.shields.io/github/license/posit-dev/gt-extras)](https://github.com/posit-dev/gt-extras/blob/main/LICENSE)

[![Tests](https://github.com/posit-dev/gt-extras/actions/workflows/ci_tests.yml/badge.svg)](https://github.com/posit-dev/gt-extras/actions/workflows/ci_tests.yml)
[![Documentation](https://img.shields.io/badge/docs-project_website-blue.svg)](https://posit-dev.github.io/gt-extras)
[![Repo Status](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![Contributors](https://img.shields.io/github/contributors/posit-dev/gt-extras)](https://github.com/posit-dev/gt-extras/graphs/contributors)

<!-- [![Codecov](https://codecov.io/gh/posit-dev/gt-extras/branch/main/graph/badge.svg)](https://codecov.io/gh/posit-dev/gt-extras) -->


> ⚠️ **gt-extras is currently in development, expect breaking changes.**


### What is [gt-extras](https://posit-dev.github.io/gt-extras)?

A collection of additional helper functions for creating beautiful tables with the [great-tables](https://posit-dev.github.io/great-tables/) package in Python.

The functions in **gt-extras** are designed to make it easier to add plots, icons, color gradients, and other enhancements to your tables. We wrap up common patterns and boilerplate so you can focus on your data and presentation. It is based on the R package [gtExtras](https://jthomasmock.github.io/gtExtras/index.html), which was designed with a similar goal in mind.

## Installation
Install the latest release from PyPI: ```pip install gt-extras```

## Example Usage

```python
from great_tables import GT
from great_tables.data import gtcars
import gt_extras as gte

gtcars_mini = gtcars.iloc[5:15].copy().reset_index(drop=True)
gtcars_mini["efficiency"] = gtcars_mini["mpg_c"] / gtcars_mini["hp"] * 100

(
    # Start with a standard GT
    GT(gtcars_mini, rowname_col="model")
    .tab_stubhead(label="Vehicle")
    .cols_hide(["drivetrain", "hp_rpm", "trq_rpm", "trim", "bdy_style", "msrp", "trsmn", "ctry_origin"])
    .cols_align("center")
    .tab_header(title="Car Performance Review", subtitle="Using gt-extras functionality")

    # Add gt-extras features using gt.pipe()
    .pipe(gte.gt_color_box, columns=["hp", "trq"], palette=["lightblue", "darkblue"])
    .pipe(gte.gt_plt_dot, category_col="mfr", data_col="efficiency", domain=[0, 0])
    .pipe(gte.gt_plt_bar, columns=["mpg_c", "mpg_h"])
    .pipe(gte.gt_fa_rating, columns="efficiency")
    .pipe(gte.gt_hulk_col_numeric, columns="year", palette="viridis")
    .pipe(gte.gt_theme_538)
)
```

<!-- TODO here!!! -->
<div align="center">
<img src="https://posit-dev.github.io/gt-extras/assets/composite_car_example.png" width="800px">
</div>

## Features

- Apply color gradients and highlights
- Add plots to table cells for visual data representation
- Embed FontAwesome icons
- Use pre-built themes for quick styling
- Utilize helper utilities for common table tasks

## Contributing
If you encounter a bug, have usage questions, or want to share ideas to make this package better, please feel free to file an [issue](https://github.com/posit-dev/gt-extras/issues).

## Code of Conduct
Please note that the **gt-extras** project is released with a [contributor code of conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).<br>By participating in this project you agree to abide by its terms.


## 📄 License

**Great Tables** is licensed under the MIT license.

© Posit Software, PBC.

## Citation
If you use **gt-extras** in your work, please cite the package:

```bibtex
@software{gt_extras,
authors = {Jules Walzer-Goldfeld, Michael Chow, and Rich Iannone},
license = {MIT},
title = {{gt-extras: Extra helpers for great-tables in Python.}},
url = {https://github.com/posit-dev/gt-extras}, version = {0.0.1}
}
```

For more information, see the [docs](https://posit-dev.github.io/gt-extras/reference) or [open an issue](https://github.com/posit-dev/gt-extras/issues) with questions or suggestions!
