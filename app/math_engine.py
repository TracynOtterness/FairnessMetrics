"""Mathematical engine for fairness metrics calculations.

This module provides functions to compute classification metrics (TPR, FPR, TNR, FNR)
and predictive values (PPV, NPV) for normal distributions, enabling visualization of
the Impossibility Theorem of Fairness.
"""

import numpy as np
from scipy import stats
from scipy.integrate import cumulative_trapezoid
import json
import os

EMPIRICAL_DATA = None

def load_empirical_data():
    global EMPIRICAL_DATA
    if EMPIRICAL_DATA is None:
        path = os.path.join(os.path.dirname(__file__), "compas_empirical.json")
        with open(path, "r") as f:
            EMPIRICAL_DATA = json.load(f)
    return EMPIRICAL_DATA

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


def compute_empirical_rates(hist: dict, threshold: float) -> float:
    """
    Compute rate (prob > threshold) by calculating the area under the 
    linearly interpolated empirical continuous curve, matching the visualization.
    """
    # 1. Get the exact same x and y points as the visual curve
    curve = generate_empirical_distribution_points(hist)
    x_points = np.array(curve["x"])
    y_points = np.array(curve["y"])
    
    # 2. Normalize so total area in the [0, 100] range is exactly 1.0
    total_area = np.trapezoid(y_points, x_points)
    
    if total_area <= 0:
        return 0.0
        
    y_points_norm = y_points / total_area
    
    # 3. Find area exactly above the threshold
    mask = x_points >= threshold
    if not np.any(mask):
        return 0.0
        
    x_above = x_points[mask]
    y_above = y_points_norm[mask]
    
    # Start integration exactly AT the threshold by interpolating the boundary
    if x_above[0] > threshold:
        y_thresh = np.interp(threshold, x_points, y_points_norm)
        x_above = np.insert(x_above, 0, threshold)
        y_above = np.insert(y_above, 0, y_thresh)
        
    area_above = np.trapezoid(y_above, x_above)
    
    return float(np.clip(area_above, 0.0, 1.0))


def generate_empirical_distribution_points(hist: dict) -> dict:
    """Generate smooth x,y points for an empirical histogram."""
    centers = [(int(k) - 0.5) * 10 for k in hist.keys()]
    probs = [hist[k] for k in hist.keys()]
    
    # Sort pairs
    sorted_pairs = sorted(zip(centers, probs))
    centers = [p[0] for p in sorted_pairs]
    probs = [p[1] for p in sorted_pairs]
    
    # Add boundary points to make curve go to 0
    centers = [-5.0] + centers + [105.0]
    probs = [0.0] + probs + [0.0]
    
    x_points = np.linspace(0, 100, 200)
    y_points = np.interp(x_points, centers, probs)
    
    return {"x": x_points.tolist(), "y": y_points.tolist()}


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
    dist_type = params.get("distribution_type", "gaussian")

    if dist_type in ("compas_general", "compas_violent"):
        data = load_empirical_data()
        subset = "general" if dist_type == "compas_general" else "violent"
        
        hist_a_pos = data[subset]["African-American"]["pos_hist"]
        hist_a_neg = data[subset]["African-American"]["neg_hist"]
        
        hist_b_pos = data[subset]["Caucasian"]["pos_hist"]
        hist_b_neg = data[subset]["Caucasian"]["neg_hist"]
        
        tpr_a = compute_empirical_rates(hist_a_pos, threshold_a)
        fpr_a = compute_empirical_rates(hist_a_neg, threshold_a)
        rates_a = {"tpr": tpr_a, "fpr": fpr_a, "tnr": 1 - fpr_a, "fnr": 1 - tpr_a}
        
        tpr_b = compute_empirical_rates(hist_b_pos, threshold_b)
        fpr_b = compute_empirical_rates(hist_b_neg, threshold_b)
        rates_b = {"tpr": tpr_b, "fpr": fpr_b, "tnr": 1 - fpr_b, "fnr": 1 - tpr_b}
        
        curves_a = {
            "positive": generate_empirical_distribution_points(hist_a_pos),
            "negative": generate_empirical_distribution_points(hist_a_neg),
        }
        curves_b = {
            "positive": generate_empirical_distribution_points(hist_b_pos),
            "negative": generate_empirical_distribution_points(hist_b_neg),
        }
    else:
        # Population A (Gaussian)
        rates_a = compute_rates(
            params["pop_a_mu_pos"],
            params["pop_a_sigma_pos"],
            params["pop_a_mu_neg"],
            params["pop_a_sigma_neg"],
            threshold_a,
        )
        # Population B (Gaussian)
        rates_b = compute_rates(
            params["pop_b_mu_pos"],
            params["pop_b_sigma_pos"],
            params["pop_b_mu_neg"],
            params["pop_b_sigma_neg"],
            threshold_b,
        )
        curves_a = {
            "positive": generate_distribution_points(params["pop_a_mu_pos"], params["pop_a_sigma_pos"]),
            "negative": generate_distribution_points(params["pop_a_mu_neg"], params["pop_a_sigma_neg"]),
        }
        curves_b = {
            "positive": generate_distribution_points(params["pop_b_mu_pos"], params["pop_b_sigma_pos"]),
            "negative": generate_distribution_points(params["pop_b_mu_neg"], params["pop_b_sigma_neg"]),
        }

    pv_a = compute_predictive_values(
        rates_a["tpr"], rates_a["fpr"], rates_a["tnr"], rates_a["fnr"], params["pop_a_prevalence"]
    )
    cm_a = compute_confusion_matrix(
        rates_a["tpr"], rates_a["fpr"], rates_a["tnr"], rates_a["fnr"], params["pop_a_prevalence"]
    )

    pv_b = compute_predictive_values(
        rates_b["tpr"], rates_b["fpr"], rates_b["tnr"], rates_b["fnr"], params["pop_b_prevalence"]
    )
    cm_b = compute_confusion_matrix(
        rates_b["tpr"], rates_b["fpr"], rates_b["tnr"], rates_b["fnr"], params["pop_b_prevalence"]
    )

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
    fp_weight = params.get("fp_weight", 1.0)
    fn_weight = params.get("fn_weight", 1.0)
    constraint_equal = params.get("constraint_equal", True)

    # Equity weights
    w_fpr = params.get("w_fpr", 0.0)
    w_fnr = params.get("w_fnr", 0.0)
    w_ppv = params.get("w_ppv", 0.0)
    w_npv = params.get("w_npv", 0.0)

    # 1. Define Search Space
    steps = np.arange(0, 100.5, 0.5)

    if constraint_equal:
        t_a_grid = steps
        t_b_grid = steps
    else:
        t_a_grid, t_b_grid = np.meshgrid(steps, steps)
        t_a_grid = t_a_grid.flatten()
        t_b_grid = t_b_grid.flatten()

    prev_a = params.get("pop_a_prevalence", 0.5)
    prev_b = params.get("pop_b_prevalence", 0.5)

    dist_type = params.get("distribution_type", "gaussian")

    if dist_type in ("compas_general", "compas_violent"):
        data = load_empirical_data()
        subset = "general" if dist_type == "compas_general" else "violent"
        
        hist_a_pos = data[subset]["African-American"]["pos_hist"]
        hist_a_neg = data[subset]["African-American"]["neg_hist"]
        hist_b_pos = data[subset]["Caucasian"]["pos_hist"]
        hist_b_neg = data[subset]["Caucasian"]["neg_hist"]

        def get_empirical_cdf(hist):
            curve = generate_empirical_distribution_points(hist)
            x = np.array(curve["x"])
            y = np.array(curve["y"])
            area = np.trapezoid(y, x)
            if area > 0:
                y = y / area
            cdf = cumulative_trapezoid(y, x, initial=0)
            return x, cdf

        x_a_pos, cdf_a_pos = get_empirical_cdf(hist_a_pos)
        x_a_neg, cdf_a_neg = get_empirical_cdf(hist_a_neg)
        x_b_pos, cdf_b_pos = get_empirical_cdf(hist_b_pos)
        x_b_neg, cdf_b_neg = get_empirical_cdf(hist_b_neg)

        fnr_a = np.interp(t_a_grid, x_a_pos, cdf_a_pos)
        fpr_a = 1 - np.interp(t_a_grid, x_a_neg, cdf_a_neg)
        fnr_b = np.interp(t_b_grid, x_b_pos, cdf_b_pos)
        fpr_b = 1 - np.interp(t_b_grid, x_b_neg, cdf_b_neg)

    else:
        # Gaussian rates
        fnr_a = stats.norm.cdf(t_a_grid, loc=params["pop_a_mu_pos"], scale=params["pop_a_sigma_pos"])
        fpr_a = 1 - stats.norm.cdf(t_a_grid, loc=params["pop_a_mu_neg"], scale=params["pop_a_sigma_neg"])
        fnr_b = stats.norm.cdf(t_b_grid, loc=params["pop_b_mu_pos"], scale=params["pop_b_sigma_pos"])
        fpr_b = 1 - stats.norm.cdf(t_b_grid, loc=params["pop_b_mu_neg"], scale=params["pop_b_sigma_neg"])

    tpr_a = 1 - fnr_a
    tpr_b = 1 - fnr_b
    tnr_a = 1 - fpr_a
    tnr_b = 1 - fpr_b

    # PPV = (TPR * prev) / (TPR * prev + FPR * (1 - prev))
    num_ppv_a = tpr_a * prev_a
    den_ppv_a = num_ppv_a + fpr_a * (1 - prev_a)
    ppv_a = np.divide(num_ppv_a, den_ppv_a, out=np.zeros_like(num_ppv_a), where=den_ppv_a!=0)

    num_ppv_b = tpr_b * prev_b
    den_ppv_b = num_ppv_b + fpr_b * (1 - prev_b)
    ppv_b = np.divide(num_ppv_b, den_ppv_b, out=np.zeros_like(num_ppv_b), where=den_ppv_b!=0)

    # NPV = (TNR * (1-prev)) / (TNR * (1-prev) + FNR * prev)
    num_npv_a = tnr_a * (1 - prev_a)
    den_npv_a = num_npv_a + fnr_a * prev_a
    npv_a = np.divide(num_npv_a, den_npv_a, out=np.zeros_like(num_npv_a), where=den_npv_a!=0)

    num_npv_b = tnr_b * (1 - prev_b)
    den_npv_b = num_npv_b + fnr_b * prev_b
    npv_b = np.divide(num_npv_b, den_npv_b, out=np.zeros_like(num_npv_b), where=den_npv_b!=0)

    # Calculate overall rates
    n_pos_a = prev_a * 1000
    n_neg_a = (1 - prev_a) * 1000
    n_pos_b = prev_b * 1000
    n_neg_b = (1 - prev_b) * 1000

    overall_fpr = (fpr_a * n_neg_a + fpr_b * n_neg_b) / (n_neg_a + n_neg_b)
    overall_fnr = (fnr_a * n_pos_a + fnr_b * n_pos_b) / (n_pos_a + n_pos_b)

    # Option 1 Math: Normalized Error + Equity Penalty
    norm_error = (fp_weight * overall_fpr) + (fn_weight * overall_fnr)

    equity_penalty = (
        (w_fpr * np.abs(fpr_a - fpr_b)) +
        (w_fnr * np.abs(fnr_a - fnr_b)) +
        (w_ppv * np.abs(ppv_a - ppv_b)) +
        (w_npv * np.abs(npv_a - npv_b))
    )

    total_cost = norm_error + equity_penalty

    min_idx = np.argmin(total_cost)

    return {
        "threshold_a": float(t_a_grid[min_idx]),
        "threshold_b": float(t_b_grid[min_idx]),
        "min_cost": float(total_cost[min_idx]),
    }
