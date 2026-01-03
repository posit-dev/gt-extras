"""Native Python implementations of statistical functions.

This module provides pure Python implementations of statistical functions
previously provided by scipy, specifically for computing confidence intervals.
"""

from __future__ import annotations

import math


def mean(values: list[float | int]) -> float:
    """Compute the arithmetic mean of a list of values."""
    if not values:
        raise ValueError("Cannot compute mean of empty list")
    return sum(values) / len(values)


def std(values: list[float | int], ddof: int = 1) -> float:
    """Compute the sample standard deviation.

    Parameters
    ----------
    values
        List of numeric values.
    ddof
        Delta degrees of freedom. Default is 1 for sample std.

    Returns
    -------
    float
        The sample standard deviation.
    """
    n = len(values)
    if n <= ddof:
        raise ValueError(
            f"Need at least {ddof + 1} values to compute std with ddof={ddof}"
        )
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (n - ddof)
    return math.sqrt(variance)


def sem(values: list[float | int]) -> float:
    """Compute the standard error of the mean.

    Parameters
    ----------
    values
        List of numeric values.

    Returns
    -------
    float
        The standard error of the mean (std / sqrt(n)).
    """
    n = len(values)
    if n < 2:
        raise ValueError("Need at least 2 values to compute sem")
    return std(values, ddof=1) / math.sqrt(n)


def _norm_ppf(p: float) -> float:
    """Approximate the inverse of the standard normal CDF (probit function).

    Uses the Abramowitz and Stegun approximation (formula 26.2.23).
    Accurate to about 4.5 decimal places.

    Parameters
    ----------
    p
        Probability value between 0 and 1.

    Returns
    -------
    float
        The z-score corresponding to the probability p.
    """
    if p <= 0 or p >= 1:
        if p == 0:
            return float("-inf")
        if p == 1:
            return float("inf")
        raise ValueError("p must be between 0 and 1")

    # Constants for approximation
    a0 = 2.515517
    a1 = 0.802853
    a2 = 0.010328
    b1 = 1.432788
    b2 = 0.189269
    b3 = 0.001308

    if p < 0.5:
        sign = -1
        p_work = p
    else:
        sign = 1
        p_work = 1 - p

    if p_work < 1e-300:
        return sign * 38.0  # Approximate for extreme values

    t = math.sqrt(-2 * math.log(p_work))
    numerator = a0 + a1 * t + a2 * t * t
    denominator = 1 + b1 * t + b2 * t * t + b3 * t * t * t
    result = t - numerator / denominator

    return sign * result


def _t_ppf(p: float, df: float) -> float:
    """Approximate the inverse of the Student's t-distribution CDF.

    Uses Hill's approximation for the t-distribution quantile function,
    which provides good accuracy for most practical purposes.

    Parameters
    ----------
    p
        Probability value between 0 and 1.
    df
        Degrees of freedom.

    Returns
    -------
    float
        The t-value corresponding to probability p.
    """
    if df <= 0:
        raise ValueError("Degrees of freedom must be positive")

    # For very large df, use normal approximation
    if df > 1e6:
        return _norm_ppf(p)

    # Get the corresponding normal quantile
    z = _norm_ppf(p)

    # For df=1 (Cauchy), use tan approximation
    if df == 1:
        return math.tan(math.pi * (p - 0.5))

    # For df=2, there's an exact formula
    if df == 2:
        alpha = 2 * p - 1
        if abs(alpha) >= 1:
            return float("inf") if alpha > 0 else float("-inf")
        return alpha / math.sqrt(2 * (1 - alpha * alpha))

    # Hill's approximation for general df
    # Cornish-Fisher expansion
    g1 = (z**3 + z) / 4
    g2 = (5 * z**5 + 16 * z**3 + 3 * z) / 96
    g3 = (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / 384
    g4 = (79 * z**9 + 776 * z**7 + 1482 * z**5 - 1920 * z**3 - 945 * z) / 92160

    inv_df = 1 / df
    t = z + g1 * inv_df + g2 * inv_df**2 + g3 * inv_df**3 + g4 * inv_df**4

    return t


def t_interval(
    confidence: float,
    df: int,
    loc: float = 0.0,
    scale: float = 1.0,
) -> tuple[float, float]:
    """Compute the confidence interval for a t-distribution.

    This is equivalent to scipy.stats.t.interval().

    Parameters
    ----------
    confidence
        The confidence level (e.g., 0.95 for 95% CI).
    df
        Degrees of freedom.
    loc
        Location parameter (mean). Default is 0.
    scale
        Scale parameter (standard error). Default is 1.

    Returns
    -------
    tuple[float, float]
        A tuple (lower, upper) representing the confidence interval bounds.
    """
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1")
    if df < 1:
        raise ValueError("Degrees of freedom must be at least 1")

    alpha = 1 - confidence
    lower_tail = alpha / 2
    upper_tail = 1 - alpha / 2

    t_lower = _t_ppf(lower_tail, df)
    t_upper = _t_ppf(upper_tail, df)

    lower = loc + scale * t_lower
    upper = loc + scale * t_upper

    return (lower, upper)
