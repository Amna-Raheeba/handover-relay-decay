"""Survival-curve metrics: half-life fitting and curve summaries."""

import math


def fit_half_life(curve):
    """Fit an exponential decay to a survival curve.

    Least squares on log(survival) against relay index, using relays
    where survival is positive. Returns the fitted half-life in relays,
    or None when the curve does not decay (slope >= 0) or has fewer
    than two usable points.
    """
    xs = []
    ys = []
    for relay, value in enumerate(curve):
        if value > 0.0:
            xs.append(float(relay))
            ys.append(math.log(value))
    if len(xs) < 2:
        return None
    n = float(len(xs))
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)
    if den == 0.0:
        return None
    slope = num / den
    if slope >= 0.0:
        return None
    return -math.log(2.0) / slope


def empirical_half_life(curve):
    """First relay at which survival falls to 0.5, linearly interpolated.

    Returns None when the curve never reaches 0.5 inside the observed
    window (the half-life is then longer than the window).
    """
    for relay in range(1, len(curve)):
        if curve[relay] <= 0.5:
            prev = curve[relay - 1]
            cur = curve[relay]
            if prev == cur:
                return float(relay)
            frac = (prev - 0.5) / (prev - cur)
            return float(relay - 1) + frac
    return None


def curve_auc(curve):
    """Trapezoidal area under a survival curve, per relay (mean survival)."""
    if len(curve) < 2:
        return 0.0
    total = 0.0
    for i in range(1, len(curve)):
        total += 0.5 * (curve[i - 1] + curve[i])
    return total / (len(curve) - 1)


def survival_at(curve, relay):
    if relay < 0 or relay >= len(curve):
        raise ValueError("relay %d outside curve" % relay)
    return curve[relay]


def summarise_run(run):
    """Headline summary of one simulate_census run."""
    critical = run["critical_survival"]
    total = run["total_survival"]
    return {
        "policy": run["policy"],
        "critical_survival_relay_1": survival_at(critical, 1),
        "critical_survival_relay_4": survival_at(critical, 4),
        "critical_survival_relay_8": survival_at(critical, 8),
        "total_survival_relay_4": survival_at(total, 4),
        "total_survival_relay_8": survival_at(total, 8),
        "critical_half_life_fitted": fit_half_life(critical),
        "critical_half_life_empirical": empirical_half_life(critical),
        "critical_curve_auc": curve_auc(critical),
    }
