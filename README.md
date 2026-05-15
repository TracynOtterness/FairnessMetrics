# Fairness Metrics Visualizer

An interactive educational tool for exploring the **Impossibility Theorem of Fairness** (Chouldechova, Kleinberg) — the mathematical proof that when two populations have different base rates (prevalence), it is impossible to simultaneously equalize all fairness metrics (PPV, NPV, FPR, FNR) across them.

---

## Overview

The tool models two populations (A and B) as overlapping Gaussian risk-score distributions. You can interactively adjust thresholds, prevalences, and distribution shapes, then watch all fairness metrics and visualizations update in real time. An optimization engine can also find the cost-minimizing threshold(s) for a user-defined weighting of false-positive vs. false-negative errors.

---

## Features

### Interactive Controls (Sidebar)

| Control | Description |
|---|---|
| **Classification Thresholds** | Independent sliders for Population A and B (range 0–100, step 0.5). Clicking a displayed value opens an inline number editor for precise input. |
| **Lock Thresholds** | Checkbox that synchronizes both sliders — moving one automatically moves the other. |
| **Prevalence** | Per-population slider (0.01–0.99) controlling the base rate of truly positive cases. |
| **Distribution Parameters** | Collapsible section per population exposing μ (mean) and σ (std dev) sliders for both the positive and negative sub-distributions. |

### Threshold Optimizer

A one-click **Optimize Thresholds** button finds the thresholds that minimize a weighted cost function across both populations:

```
Cost = (fp_weight × total_FP) + (fn_weight × total_FN)
```

- **False Positive Cost** slider (0.1–10.0) — weight the cost of a false alarm.
- **False Negative Cost** slider (0.1–10.0) — weight the cost of a missed positive.
- **Enforce Equal Thresholds** checkbox — when checked, constrains both populations to share a single threshold (a common regulatory requirement); when unchecked, allows independent per-population thresholds.

The optimizer uses a vectorized NumPy/SciPy grid search over the full threshold space (0–100 at 0.5 steps), making it both accurate and fast.

### Risk Score Distributions (Bell Curves)

A Canvas-rendered chart showing all four overlapping normal distributions simultaneously:

- **Pop A – Positive** (blue) · **Pop A – Negative** (cyan)
- **Pop B – Positive** (pink) · **Pop B – Negative** (orange)

Each curve is **scaled by its sub-population weight** (prevalence or 1 − prevalence) so relative areas reflect actual group sizes. Threshold lines are drawn directly on the chart — a single white line when thresholds are equal, or two colored lines (matching each population's color) when they differ.

**Legend toggles** — clicking any legend item shows/hides that curve without losing the current data.

### Confusion Matrices

Three side-by-side confusion matrix panels, each scaled to a hypothetical population of 1,000:

| Panel | Content |
|---|---|
| **Population A** | TP, FP, TN, FN counts + TPR, FPR, TNR, FNR, PPV, NPV |
| **Population B** | Same metrics for Population B |
| **Overall (Combined)** | Aggregate counts and derived overall rates/predictive values |

### Fairness Metric Comparison (Impossibility Theorem Visualization)

A bar-chart panel showing the **absolute difference** between the two populations for each of the six key metrics:

- PPV (Positive Predictive Value)
- NPV (Negative Predictive Value)
- FPR (False Positive Rate)
- FNR (False Negative Rate)
- TPR (True Positive Rate / Sensitivity)
- TNR (True Negative Rate / Specificity)

When prevalence differs, you can observe directly how minimizing one disparity forces others to grow — a live demonstration of the Impossibility Theorem.

---

## API Endpoints

The Flask backend exposes three endpoints:

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/calculate` | Computes all metrics for both populations. Accepts distribution parameters and thresholds as query-string arguments. |
| `POST` | `/api/optimize` | Finds cost-minimizing thresholds. Accepts a JSON body with distribution params plus `fp_weight`, `fn_weight`, and `constraint_equal`. |
| `GET` | `/api/health` | Health check, returns `{"status": "healthy"}`. |

---

## Running Locally

### Using Docker (Recommended)

```bash
docker-compose up --build
```

Open [http://localhost:5000](http://localhost:5000)

### Using UV (Dev Mode)

```bash
uv run python run.py
```

Requires Python ≥ 3.11 and [uv](https://github.com/astral-sh/uv).

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python ≥ 3.11, Flask ≥ 3.0, NumPy ≥ 1.26, SciPy ≥ 1.11 |
| **Frontend** | HTML5, Vanilla CSS (glassmorphism dark theme), Vanilla JavaScript, Canvas API |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) |
| **Linting / Formatting** | [Ruff](https://docs.astral.sh/ruff/) |
| **Containerization** | Docker + Docker Compose |

---

## Project Structure

```
FairnessMetrics/
├── app/
│   ├── math_engine.py          # Core math: rates, predictive values, confusion matrices, optimizer
│   ├── routes.py               # Flask blueprints and API endpoints
│   ├── templates/
│   │   └── index.html          # Single-page application shell
│   └── static/
│       ├── css/style.css       # Glassmorphism dark-mode styles
│       └── js/
│           ├── main.js         # App entry point, orchestrates fetch + render cycle
│           ├── controls.js     # Slider/input management, threshold lock, optimizer trigger
│           └── visualizations/
│               ├── bellCurves.js      # Canvas bell-curve renderer with legend toggles
│               ├── confusionMatrix.js # Three-panel confusion matrix renderer
│               └── impossibility.js  # Fairness metric comparison bar chart
├── scripts/
│   └── fit_compas.py           # Utility: fit Gaussian params to COMPAS recidivism data
├── doc/
│   └── implementation_plan.md  # Design notes from development
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── run.py                      # Dev server entry point
```

---

## Educational Background

The **Impossibility Theorem of Fairness** (independently proven by Chouldechova 2017 and Kleinberg et al. 2016) states that when two groups have different base rates, a classifier cannot simultaneously satisfy:

- **Calibration** (equal PPV across groups), and
- **Error-rate parity** (equal FPR and FNR across groups)

…unless the classifier is perfect or the base rates are identical.

> 💡 **Try it**: set both populations to identical distributions, then change only the prevalence sliders. Watch the Fairness Metric Comparison panel show growing disparities even though the underlying risk-score model is the same for both groups.

The `scripts/fit_compas.py` utility demonstrates this concretely by fitting Gaussian parameters to the publicly reported FPR/FNR figures from the COMPAS recidivism study (ProPublica, 2016).
