/**
 * Impossibility Theorem Visualization
 * Shows the trade-off between calibration (PPV) and error rate balance (FPR/FNR)
 */

class ImpossibilityViz {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
  }

  update(data) {
    this.container.innerHTML = "";

    const metrics = [
      {
        label: "PPV",
        valA: data.population_a.predictive_values.ppv * 100,
        valB: data.population_b.predictive_values.ppv * 100,
        desc: "Calibration",
      },
      {
        label: "NPV",
        valA: data.population_a.predictive_values.npv * 100,
        valB: data.population_b.predictive_values.npv * 100,
        desc: "Calibration",
      },
      {
        label: "FPR",
        valA: data.population_a.rates.fpr * 100,
        valB: data.population_b.rates.fpr * 100,
        desc: "Error Balance",
      },
      {
        label: "FNR",
        valA: data.population_a.rates.fnr * 100,
        valB: data.population_b.rates.fnr * 100,
        desc: "Error Balance",
      },
    ];

    metrics.forEach((metric) => {
      const row = document.createElement("div");
      row.style.marginBottom = "1.5rem";

      // Header
      const header = document.createElement("div");
      header.style.display = "flex";
      header.style.justifyContent = "space-between";
      header.style.marginBottom = "0.5rem";
      header.innerHTML = `
                <span style="font-weight: 600; color: var(--text-primary)">${metric.label}</span>
                <span style="color: var(--text-secondary); font-size: 0.8rem">${metric.desc}</span>
            `;
      row.appendChild(header);

      // Bars container
      const bars = document.createElement("div");
      bars.style.display = "flex";
      bars.style.gap = "10px";
      bars.style.height = "24px";
      bars.style.alignItems = "center";

      // Bar A
      const barA = this.createBar(metric.valA, "var(--pop-a-primary)");
      // Bar B
      const barB = this.createBar(metric.valB, "var(--pop-b-primary)");

      // Diff Value
      const diff = Math.abs(metric.valA - metric.valB).toFixed(1);
      const diffTag = document.createElement("div");
      diffTag.style.marginLeft = "auto";
      diffTag.style.fontSize = "0.85rem";
      diffTag.style.color = diff < 1 ? "#4cc9f0" : "#e0e0e0"; // Highlight if balanced
      diffTag.innerHTML = `Δ ${diff}%`;

      bars.appendChild(barA);
      bars.appendChild(barB);
      bars.appendChild(diffTag);

      row.appendChild(bars);
      this.container.appendChild(row);
    });
  }

  createBar(percentage, color) {
    const wrapper = document.createElement("div");
    wrapper.style.flex = "1";
    wrapper.style.background = "rgba(255,255,255,0.1)";
    wrapper.style.borderRadius = "4px";
    wrapper.style.height = "100%";
    wrapper.style.position = "relative";
    wrapper.style.overflow = "hidden";

    const fill = document.createElement("div");
    fill.style.width = `${percentage}%`;
    fill.style.height = "100%";
    fill.style.background = color;
    fill.style.transition = "width 0.3s ease";

    // Label inside bar for precise value
    const label = document.createElement("span");
    label.innerText = percentage.toFixed(1);
    label.style.position = "absolute";
    label.style.left = "5px";
    label.style.top = "50%";
    label.style.transform = "translateY(-50%)";
    label.style.fontSize = "0.75rem";
    label.style.color = "#fff";
    label.style.textShadow = "0 1px 2px rgba(0,0,0,0.5)";

    wrapper.appendChild(fill);
    wrapper.appendChild(label);
    return wrapper;
  }
}
