/**
 * Confusion Matrix Visualization Module
 * Renders interactive confusion matrices for both populations
 */

class ConfusionMatrixViz {
  constructor(containerIdA, containerIdB, metricsIdA, metricsIdB) {
    this.containerA = document.getElementById(containerIdA);
    this.containerB = document.getElementById(containerIdB);
    this.metricsA = document.getElementById(metricsIdA);
    this.metricsB = document.getElementById(metricsIdB);

    // Optional Overall containers (for V3)
    this.containerOverall = document.getElementById("confusion-matrix-overall");
    this.metricsOverall = document.getElementById("metrics-overall");
  }

  update(data) {
    this.renderMatrix(this.containerA, this.metricsA, data.population_a);
    this.renderMatrix(this.containerB, this.metricsB, data.population_b);

    if (this.containerOverall && data.overall) {
      this.renderMatrix(
        this.containerOverall,
        this.metricsOverall,
        data.overall
      );
    }
  }

  renderMatrix(container, metricsContainer, popData) {
    // Clear previous content
    container.innerHTML = "";

    // Define matrix structure (Headers + Cells)
    // Grid is 3x3: Top-left(empty), Pred Pos, Pred Neg, Actual Pos, TP, FN, Actual Neg, FP, TN

    const structure = [
      { type: "header", text: "" },
      { type: "header", text: "Pred. Positive" },
      { type: "header", text: "Pred. Negative" },
      { type: "header", text: "Actual Positive" },
      {
        type: "cell",
        key: "tp",
        label: "True Positive",
        rate: popData.rates.tpr,
      },
      {
        type: "cell",
        key: "fn",
        label: "False Negative",
        rate: popData.rates.fnr,
      },
      { type: "header", text: "Actual Negative" },
      {
        type: "cell",
        key: "fp",
        label: "False Positive",
        rate: popData.rates.fpr,
      },
      {
        type: "cell",
        key: "tn",
        label: "True Negative",
        rate: popData.rates.tnr,
      },
    ];

    structure.forEach((item) => {
      if (item.type === "header") {
        const div = document.createElement("div");
        div.className = "matrix-header matrix-cell";
        div.textContent = item.text;
        container.appendChild(div);
      } else {
        const div = document.createElement("div");
        div.className = "matrix-cell";
        // Calculate opacity based on rate (0-1) for visual heatmap effect
        // Using a blueish tint for positive outcomes, reddish for errors?
        // Or just simple white opacity for simplicity and cleanliness
        const opacity = 0.05 + item.rate * 0.2; // Base + dynamic
        div.style.backgroundColor = `rgba(255, 255, 255, ${opacity})`;

        div.innerHTML = `
                    <span class="cell-count">${
                      popData.confusion_matrix[item.key]
                    }</span>
                    <span class="cell-label">${item.label}</span>
                    <span class="cell-label">(${(item.rate * 100).toFixed(
                      1
                    )}%)</span>
                `;
        container.appendChild(div);
      }
    });

    // Render Metrics (PPV, NPV)
    metricsContainer.innerHTML = `
            <div class="metric-item">
                <span>PPV (Precision):</span>
                <strong>${(popData.predictive_values.ppv * 100).toFixed(
                  1
                )}%</strong>
            </div>
            <div class="metric-item">
                <span>NPV:</span>
                <strong>${(popData.predictive_values.npv * 100).toFixed(
                  1
                )}%</strong>
            </div>
            <div class="metric-item">
                <span>FPR (Fallout):</span>
                <strong>${(popData.rates.fpr * 100).toFixed(1)}%</strong>
            </div>
            <div class="metric-item">
                <span>FNR (Miss Rate):</span>
                <strong>${(popData.rates.fnr * 100).toFixed(1)}%</strong>
            </div>
        `;
  }
}
