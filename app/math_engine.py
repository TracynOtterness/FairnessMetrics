"""Mathematical engine for fairness metrics calculations.

This module provides functions to compute classification metrics (TPR, FPR, TNR, FNR)
and predictive values (PPV, NPV) for normal distributions, enabling visualization of
the Impossibility Theorem of Fairness.
"""

import numpy as np
from scipy import stats


def compute_rates(
    mu_pos: float, sigma_pos: float, mu_neg: float, sigma_neg: float, threshold: float
) -> dict:
    """
    Compute classification rates for a given threshold.

    Args:
        mu_pos: Mean of the positive (truly positive) distribution
        sigma_pos: Standard deviation of the positive distribution
        mu_neg: Mean of the negative (truly negative) distribution
        sigma_neg: Standard deviation of the negative distribution
        threshold: Classification threshold (scores above this are classified positive)

    Returns:
        Dictionary with TPR, FPR, TNR, FNR
    """
    # TPR = P(score > threshold | truly positive) = 1 - CDF(threshold)
    tpr = 1 - stats.norm.cdf(threshold, loc=mu_pos, scale=sigma_pos)

    # FPR = P(score > threshold | truly negative) = 1 - CDF(threshold)
    fpr = 1 - stats.norm.cdf(threshold, loc=mu_neg, scale=sigma_neg)

    # TNR = 1 - FPR
    tnr = 1 - fpr

    # FNR = 1 - TPR
    fnr = 1 - tpr

    return {"tpr": float(tpr), "fpr": float(fpr), "tnr": float(tnr), "fnr": float(fnr)}


def compute_predictive_values(
    tpr: float, fpr: float, tnr: float, fnr: float, prevalence: float
) -> dict:
    """
    Compute positive and negative predictive values.

    Args:
        tpr: True positive rate (sensitivity)
        fpr: False positive rate
        tnr: True negative rate (specificity)
        fnr: False negative rate
        prevalence: Base rate of positive cases in the population (0-1)

    Returns:
        Dictionary with PPV and NPV
    """
    # Handle edge cases
    if prevalence <= 0:
        return {"ppv": 0.0, "npv": 1.0}
    if prevalence >= 1:
        return {"ppv": 1.0, "npv": 0.0}

    # PPV = (TPR × prevalence) / (TPR × prevalence + FPR × (1 - prevalence))
    ppv_numerator = tpr * prevalence
    ppv_denominator = tpr * prevalence + fpr * (1 - prevalence)
    ppv = ppv_numerator / ppv_denominator if ppv_denominator > 0 else 0.0

    # NPV = (TNR × (1 - prevalence)) / (TNR × (1 - prevalence) + FNR × prevalence)
    npv_numerator = tnr * (1 - prevalence)
    npv_denominator = tnr * (1 - prevalence) + fnr * prevalence
    npv = npv_numerator / npv_denominator if npv_denominator > 0 else 0.0

    return {"ppv": float(ppv), "npv": float(npv)}


def compute_confusion_matrix(
    tpr: float, fpr: float, tnr: float, fnr: float, prevalence: float, population_size: int = 1000
) -> dict:
    """
    Compute confusion matrix counts for a given population.

    Args:
        tpr, fpr, tnr, fnr: Classification rates
        prevalence: Base rate of positive cases
        population_size: Total population size for count calculations

    Returns:
        Dictionary with TP, FP, TN, FN counts and rates
    """
    n_positive = int(population_size * prevalence)
    n_negative = population_size - n_positive

    tp = int(round(n_positive * tpr))
    fn = n_positive - tp
    fp = int(round(n_negative * fpr))
    tn = n_negative - fp

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "n_positive": n_positive,
        "n_negative": n_negative,
        "population_size": population_size,
    }


def generate_distribution_points(
    mu: float, sigma: float, x_min: float = 0, x_max: float = 100, num_points: int = 200
) -> dict:
    """
    Generate x,y points for plotting a normal distribution curve.

    Args:
        mu: Mean of the distribution
        sigma: Standard deviation
        x_min: Minimum x value
        x_max: Maximum x value
        num_points: Number of points to generate

    Returns:
        Dictionary with 'x' and 'y' arrays
    """
    x = np.linspace(x_min, x_max, num_points)
    y = stats.norm.pdf(x, loc=mu, scale=sigma)

    return {"x": x.tolist(), "y": y.tolist()}


def compute_all_metrics(params: dict) -> dict:
    """
    Compute all metrics for both populations given input parameters.

    Args:
        params: Dictionary containing:
            - threshold_a: Classification threshold for Population A
            - threshold_b: Classification threshold for Population B
            - pop_a_mu_pos, pop_a_sigma_pos: Population A positive distribution
            - pop_a_mu_neg, pop_a_sigma_neg: Population A negative distribution
            - pop_a_prevalence: Population A base rate
            - pop_b_mu_pos, pop_b_sigma_pos: Population B positive distribution
            - pop_b_mu_neg, pop_b_sigma_neg: Population B negative distribution
            - pop_b_prevalence: Population B base rate

    Returns:
        Dictionary with complete metrics for both populations
    """
    threshold_a = params["threshold_a"]
    threshold_b = params["threshold_b"]

    # Population A
    rates_a = compute_rates(
        params["pop_a_mu_pos"],
        params["pop_a_sigma_pos"],
        params["pop_a_mu_neg"],
        params["pop_a_sigma_neg"],
        threshold_a,
    )
    pv_a = compute_predictive_values(
        rates_a["tpr"], rates_a["fpr"], rates_a["tnr"], rates_a["fnr"], params["pop_a_prevalence"]
    )
    cm_a = compute_confusion_matrix(
        rates_a["tpr"], rates_a["fpr"], rates_a["tnr"], rates_a["fnr"], params["pop_a_prevalence"]
    )

    # Population B
    rates_b = compute_rates(
        params["pop_b_mu_pos"],
        params["pop_b_sigma_pos"],
        params["pop_b_mu_neg"],
        params["pop_b_sigma_neg"],
        threshold_b,
    )
    pv_b = compute_predictive_values(
        rates_b["tpr"], rates_b["fpr"], rates_b["tnr"], rates_b["fnr"], params["pop_b_prevalence"]
    )
    cm_b = compute_confusion_matrix(
        rates_b["tpr"], rates_b["fpr"], rates_b["tnr"], rates_b["fnr"], params["pop_b_prevalence"]
    )

    # Distribution curves for plotting
    curves_a = {
        "positive": generate_distribution_points(params["pop_a_mu_pos"], params["pop_a_sigma_pos"]),
        "negative": generate_distribution_points(params["pop_a_mu_neg"], params["pop_a_sigma_neg"]),
    }
    curves_b = {
        "positive": generate_distribution_points(params["pop_b_mu_pos"], params["pop_b_sigma_pos"]),
        "negative": generate_distribution_points(params["pop_b_mu_neg"], params["pop_b_sigma_neg"]),
    }

    # Overall Confusion Matrix
    cm_overall = {
        "tp": cm_a["tp"] + cm_b["tp"],
        "fn": cm_a["fn"] + cm_b["fn"],
        "fp": cm_a["fp"] + cm_b["fp"],
        "tn": cm_a["tn"] + cm_b["tn"],
        "n_positive": cm_a["n_positive"] + cm_b["n_positive"],
        "n_negative": cm_a["n_negative"] + cm_b["n_negative"],
        "population_size": cm_a["population_size"] + cm_b["population_size"],
    }

    # Calculate Overall Rates/PVs for display if needed
    overall_tpr = cm_overall["tp"] / cm_overall["n_positive"] if cm_overall["n_positive"] > 0 else 0
    overall_fpr = cm_overall["fp"] / cm_overall["n_negative"] if cm_overall["n_negative"] > 0 else 0

    # Simple overall PVs
    total_predicted_pos = cm_overall["tp"] + cm_overall["fp"]
    total_predicted_neg = cm_overall["tn"] + cm_overall["fn"]
    overall_ppv = cm_overall["tp"] / total_predicted_pos if total_predicted_pos > 0 else 0
    overall_npv = cm_overall["tn"] / total_predicted_neg if total_predicted_neg > 0 else 0

    cm_overall_metrics = {
        "rates": {
            "tpr": overall_tpr,
            "fpr": overall_fpr,
            "fnr": 1 - overall_tpr,
            "tnr": 1 - overall_fpr,
        },
        "predictive_values": {"ppv": overall_ppv, "npv": overall_npv},
        "confusion_matrix": cm_overall,
    }

    return {
        "threshold_a": threshold_a,
        "threshold_b": threshold_b,
        "population_a": {
            "rates": rates_a,
            "predictive_values": pv_a,
            "confusion_matrix": cm_a,
            "curves": curves_a,
            "prevalence": params["pop_a_prevalence"],
        },
        "population_b": {
            "rates": rates_b,
            "predictive_values": pv_b,
            "confusion_matrix": cm_b,
            "curves": curves_b,
            "prevalence": params["pop_b_prevalence"],
        },
        "overall": cm_overall_metrics,
        "comparison": {
            "ppv_diff": abs(pv_a["ppv"] - pv_b["ppv"]),
            "npv_diff": abs(pv_a["npv"] - pv_b["npv"]),
            "fpr_diff": abs(rates_a["fpr"] - rates_b["fpr"]),
            "fnr_diff": abs(rates_a["fnr"] - rates_b["fnr"]),
            "tpr_diff": abs(rates_a["tpr"] - rates_b["tpr"]),
            "tnr_diff": abs(rates_a["tnr"] - rates_b["tnr"]),
        },
    }


def optimize_thresholds(params: dict) -> dict:
    """
    Find thresholds that minimize weighted error cost using a vectorized grid search.

    Cost Function:
        Cost = (fp_weight * total_FP) + (fn_weight * total_FN)

    The function performs a grid search over potential thresholds (0 to 100, step 0.5).
    It uses vectorized NumPy/SciPy operations for efficiency, calculating the cost
    for all candidate thresholds simultaneously.

    Args:
        params: Dictionary containing:
            - fp_weight: Cost weight for False Positives (default 1.0)
            - fn_weight: Cost weight for False Negatives (default 1.0)
            - constraint_equal: If True, forces threshold_a == threshold_b (default True)
            - Population distribution parameters (mu, sigma, prevalence for A and B)

    Returns:
        Dictionary with optimal thresholds and the minimum cost found.
    """
    fp_weight = params.get("fp_weight", 1.0)
    fn_weight = params.get("fn_weight", 1.0)
    constraint_equal = params.get("constraint_equal", True)

    # 1. Define Search Space
    # Search from 0 to 100 with step 0.5
    steps = np.arange(0, 100.5, 0.5)

    # Create coordinate grids for threshold candidates
    if constraint_equal:
        # If constrained, thresholds must be equal (t_a = t_b)
        t_a_grid = steps
        t_b_grid = steps
    else:
        # If independent, search the full 2D space (t_a x t_b)
        # meshgrid creates 2D arrays of all possible combinations
        t_a_grid, t_b_grid = np.meshgrid(steps, steps)
        t_a_grid = t_a_grid.flatten()
        t_b_grid = t_b_grid.flatten()

    # 2. Calculate Population Sizes
    # Scale counts to a hypothetical population of 1000 for integer arithmetic
    n_pos_a = int(1000 * params["pop_a_prevalence"])
    n_neg_a = 1000 - n_pos_a

    n_pos_b = int(1000 * params["pop_b_prevalence"])
    n_neg_b = 1000 - n_pos_b

    # 3. Vectorized Rate Calculation
    # Calculate False Negative Rates (FNR) and False Positive Rates (FPR) for all candidate thresholds
    # FNR = CDF(threshold | Positive Dist) -> Portion of positives below threshold
    # FPR = 1 - CDF(threshold | Negative Dist) -> Portion of negatives above threshold

    # Population A Rates
    fnr_a = stats.norm.cdf(t_a_grid, loc=params["pop_a_mu_pos"], scale=params["pop_a_sigma_pos"])
    fpr_a = 1 - stats.norm.cdf(
        t_a_grid, loc=params["pop_a_mu_neg"], scale=params["pop_a_sigma_neg"]
    )

    # Population B Rates
    fnr_b = stats.norm.cdf(t_b_grid, loc=params["pop_b_mu_pos"], scale=params["pop_b_sigma_pos"])
    fpr_b = 1 - stats.norm.cdf(
        t_b_grid, loc=params["pop_b_mu_neg"], scale=params["pop_b_sigma_neg"]
    )

    # 4. Cost Calculation
    # Total Errors = (Count A * Rate A) + (Count B * Rate B)
    total_fn = (n_pos_a * fnr_a) + (n_pos_b * fnr_b)
    total_fp = (n_neg_a * fpr_a) + (n_neg_b * fpr_b)

    # Weighted Cost
    total_cost = (fn_weight * total_fn) + (fp_weight * total_fp)

    # 5. Find Minimum
    min_idx = np.argmin(total_cost)

    return {
        "threshold_a": float(t_a_grid[min_idx]),
        "threshold_b": float(t_b_grid[min_idx]),
        "min_cost": float(total_cost[min_idx]),
    }
