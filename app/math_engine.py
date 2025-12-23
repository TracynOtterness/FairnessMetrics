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
            - threshold: Classification threshold
            - pop_a_mu_pos, pop_a_sigma_pos: Population A positive distribution
            - pop_a_mu_neg, pop_a_sigma_neg: Population A negative distribution
            - pop_a_prevalence: Population A base rate
            - pop_b_mu_pos, pop_b_sigma_pos: Population B positive distribution
            - pop_b_mu_neg, pop_b_sigma_neg: Population B negative distribution
            - pop_b_prevalence: Population B base rate

    Returns:
        Dictionary with complete metrics for both populations
    """
    threshold = params["threshold"]

    # Population A
    rates_a = compute_rates(
        params["pop_a_mu_pos"],
        params["pop_a_sigma_pos"],
        params["pop_a_mu_neg"],
        params["pop_a_sigma_neg"],
        threshold,
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
        threshold,
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

    return {
        "threshold": threshold,
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
        "comparison": {
            "ppv_diff": abs(pv_a["ppv"] - pv_b["ppv"]),
            "npv_diff": abs(pv_a["npv"] - pv_b["npv"]),
            "fpr_diff": abs(rates_a["fpr"] - rates_b["fpr"]),
            "fnr_diff": abs(rates_a["fnr"] - rates_b["fnr"]),
            "tpr_diff": abs(rates_a["tpr"] - rates_b["tpr"]),
            "tnr_diff": abs(rates_a["tnr"] - rates_b["tnr"]),
        },
    }
