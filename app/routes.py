"""Flask routes for the Fairness Metrics Visualizer."""

from flask import Blueprint, render_template, request, jsonify
from app.math_engine import compute_all_metrics, optimize_thresholds

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Render the main visualization page."""
    return render_template("index.html")


@main_bp.route("/api/calculate", methods=["GET"])
def calculate():
    """
    Calculate all metrics for both populations.

    Query parameters:
        threshold_a: Classification threshold A (0-100)
        threshold_b: Classification threshold B (0-100)
        pop_a_mu_pos, pop_a_sigma_pos: Pop A positive distribution params
        pop_a_mu_neg, pop_a_sigma_neg: Pop A negative distribution params
        pop_a_prevalence: Pop A base rate (0-1)
        pop_b_mu_pos, pop_b_sigma_pos: Pop B positive distribution params
        pop_b_mu_neg, pop_b_sigma_neg: Pop B negative distribution params
        pop_b_prevalence: Pop B base rate (0-1)

    Returns:
        JSON with complete metrics for both populations
    """
    try:
        params = {
            "threshold_a": float(request.args.get("threshold_a", 50)),
            "threshold_b": float(request.args.get("threshold_b", 50)),
            "pop_a_mu_pos": float(request.args.get("pop_a_mu_pos", 65)),
            "pop_a_sigma_pos": float(request.args.get("pop_a_sigma_pos", 15)),
            "pop_a_mu_neg": float(request.args.get("pop_a_mu_neg", 35)),
            "pop_a_sigma_neg": float(request.args.get("pop_a_sigma_neg", 15)),
            "pop_a_prevalence": float(request.args.get("pop_a_prevalence", 0.30)),
            "pop_b_mu_pos": float(request.args.get("pop_b_mu_pos", 60)),  # Varied slightly
            "pop_b_sigma_pos": float(request.args.get("pop_b_sigma_pos", 18)),  # Varied slightly
            "pop_b_mu_neg": float(request.args.get("pop_b_mu_neg", 40)),  # Varied slightly
            "pop_b_sigma_neg": float(request.args.get("pop_b_sigma_neg", 12)),  # Varied slightly
            "pop_b_prevalence": float(request.args.get("pop_b_prevalence", 0.50)),
            "distribution_type": request.args.get("distribution_type", "gaussian"),
        }

        # Validate ranges
        if not (0 <= params["threshold_a"] <= 100 and 0 <= params["threshold_b"] <= 100):
            return jsonify({"error": "Threshold must be between 0 and 100"}), 400
        if not (0 < params["pop_a_prevalence"] < 1):
            return jsonify({"error": "Population A prevalence must be between 0 and 1"}), 400
        if not (0 < params["pop_b_prevalence"] < 1):
            return jsonify({"error": "Population B prevalence must be between 0 and 1"}), 400

        results = compute_all_metrics(params)
        return jsonify(results)

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid parameter: {str(e)}"}), 400


@main_bp.route("/api/optimize", methods=["POST"])
def optimize():
    """
    Find optimal thresholds.
    Accepts JSON body with params (including weights).
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = optimize_thresholds(data)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@main_bp.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})
