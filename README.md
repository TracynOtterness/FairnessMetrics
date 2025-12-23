# Fairness Metrics Visualizer

An interactive educational tool to explore the **Impossibility Theorem of Fairness** (Chouldechova, Kleinberg) and understand the trade-offs between different algorithmic fairness metrics (PPV/NPV vs FPR/FNR).

## Features

- **Interactive Modeling**: Adjust risk score distributions and prevalence for two populations.
- **Real-time Visualization**:
  - Overlapping Bell Curves showing risk distributions.
  - Dynamic Confusion Matrices.
  - Bar charts demonstrating the Impossibility Theorem.
- **Educational Context**: Learn how equalizing one metric (like False Positive Rate) can inevitably lead to disparities in others (like Positive Predictive Value) when base rates differ.

## Running Locally

1. **Using Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```
   Open [http://localhost:5000](http://localhost:5000)

2. **Using UV (Dev Mode)**
   ```bash
   uv run python run.py
   ```

## Tech Stack

- **Backend**: Python, Flask, NumPy, SciPy
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JavaScript, Canvas API
- **Package Manager**: UV
