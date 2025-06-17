# gt-extras 

[![Python Versions](https://img.shields.io/pypi/pyversions/great_tables.svg)](https://pypi.python.org/pypi/gt-extras)
[![PyPI](https://img.shields.io/pypi/v/gt-extras)](https://pypi.org/project/gt-extras/)
<!-- [![PyPI - Downloads](https://img.shields.io/pypi/dm/gt-extras)](https://pypistats.org/packages/gt-extras) -->
[![License](https://img.shields.io/github/license/posit-dev/gt-extras)](https://github.com/posit-dev/gt-extras/blob/main/LICENSE)


<!-- [! [CI Build](https://github.com/posit-dev/gt-extras/actions/workflows/ci-tests.yaml/badge.svg)](https://github.com/posit-dev/gt-extras/actions/workflows/ci-tests.yaml) -->
[![Codecov](https://codecov.io/gh/posit-dev/gt-extras/branch/main/graph/badge.svg)](https://codecov.io/gh/posit-dev/gt-extras)
[![Repo Status](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

[![Contributors](https://img.shields.io/github/contributors/posit-dev/gt-extras)](https://github.com/posit-dev/gt-extras/graphs/contributors)



**gt-extras** provides additional helper functions for creating beautiful tables with [great-tables](https://posit-dev.github.io/great-tables/) in Python.

The functions in **gt-extras** are designed to make it easier to add advanced styling, icons, color gradients, and other enhancements to your tables. We wrap up common patterns and boilerplate so you can focus on your data and presentation.

## Installation
Install the latest release from PyPI: ```pip install gt-extras ```

## Example Usage

```python
from great_tables import GT, exibble
from gt_extras import gt_hulk_col_numeric

mini_exibble = exibble.head(3)
mini_gt = GT(mini_exibble, id="mini_table")
styled_gt = gt_hulk_col_numeric(mini_gt, columns=["num"], palette="viridis", alpha=0.2)

styled_gt.show("browser")
```

## Features

- Color gradients for numeric columns
- Highlighting for specific columns or cells
- FontAwesome icons and icon repetition
- Pre-built themes for quick table styling
- Helper utilities for common table tasks.
<!-- See the [documentation]("") for a full function reference and more examples. -->
    
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

For more information, see the [documentation website](https://posit-dev.github.io/gt-extras/) or [open an issue](https://github.com/posit-dev/gt-extras/issues) with questions or suggestions!
