/**
 * Bell Curve Visualization Module
 * Renders overlapping normal distributions for two populations
 */

class BellCurveViz {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    this.colors = {
      popA: {
        primary: "#4361ee",
        neg: "#4cc9f0", // Cyan
        bg: "rgba(67, 97, 238, 0.2)",
      },
      popB: {
        primary: "#f72585",
        neg: "#faa307", // Orange
        bg: "rgba(247, 37, 133, 0.2)",
      },
      text: "#a0a0b0",
      grid: "rgba(255, 255, 255, 0.05)",
      threshold: "#fff",
    };

    // Layout State
    this.visible = {
      popAPos: true,
      popANeg: true,
      popBPos: true,
      popBNeg: true,
    };

    // Handle resizing
    this.resize();
    window.addEventListener("resize", () => this.resize());

    // Setup Toggles
    this.setupToggles();
  }

  setupToggles() {
    const toggles = {
      ".pop-a-pos": "popAPos",
      ".pop-a-neg": "popANeg",
      ".pop-b-pos": "popBPos",
      ".pop-b-neg": "popBNeg",
    };

    Object.entries(toggles).forEach(([selector, key]) => {
      const el = document.querySelector(`.legend-item ${selector}`);
      if (el && el.parentElement) {
        el.parentElement.style.cursor = "pointer";
        el.parentElement.addEventListener("click", () => {
          this.visible[key] = !this.visible[key];
          // Visual feedback (opacity)
          el.parentElement.style.opacity = this.visible[key] ? "1" : "0.5";

          if (this.lastData) this.update(this.lastData);
        });
      }
    });
  }

  resize() {
    // Get the display size
    const parent = this.canvas.parentElement;
    this.canvas.width = parent.clientWidth;
    this.canvas.height = parent.clientHeight;

    // Redraw if data exists
    if (this.lastData) {
      this.update(this.lastData);
    }
  }

  /**
   * Update the visualization with new data
   * @param {Object} data - Contains thresholds and curves for both populations
   */
  update(data) {
    this.lastData = data;
    const width = this.canvas.width;
    const height = this.canvas.height;
    const padding = { top: 20, right: 20, bottom: 30, left: 40 };

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Draw grid and axes
    this.drawAxes(width, height, padding);

    // Helper to map logic coordinates to canvas coordinates
    // Assuming x range 0-100 and y scaled to max probability density
    const xMin = 0,
      xMax = 100;
    // Find max y to scale vertically
    // Populate y values scaled by prevalence
    // We need to scale the Y values we receive from the backend by the actual prevalence
    // The backend returns PDF values which integrate to 1.
    // To show relative population sizes, we multiply by prevalence.

    // Pop A (Pos) * Prev A
    const curveAPos = this.scaleCurve(
      data.population_a.curves.positive,
      data.population_a.prevalence
    );
    // Pop A (Neg) * (1 - Prev A)
    const curveANeg = this.scaleCurve(
      data.population_a.curves.negative,
      1 - data.population_a.prevalence
    );

    // Pop B (Pos) * Prev B
    const curveBPos = this.scaleCurve(
      data.population_b.curves.positive,
      data.population_b.prevalence
    );
    // Pop B (Neg) * (1 - Prev B)
    const curveBNeg = this.scaleCurve(
      data.population_b.curves.negative,
      1 - data.population_b.prevalence
    );

    // Find max y to scale vertically (now based on scaled values)
    const allY = [
      ...curveAPos.y,
      ...curveANeg.y,
      ...curveBPos.y,
      ...curveBNeg.y,
    ];
    const yMax = Math.max(...allY) * 1.1; // Add 10% headroom

    const mapX = (x) =>
      padding.left +
      ((x - xMin) / (xMax - xMin)) * (width - padding.left - padding.right);
    const mapY = (y) =>
      height -
      padding.bottom -
      (y / yMax) * (height - padding.top - padding.bottom);

    // Draw curves
    // Order: Pop A Neg, Pop A Pos, Pop B Neg, Pop B Pos

    // Draw curves if visible
    // Order: Negatives first (background), then Positives

    // Population A Negative
    if (this.visible.popANeg) {
      this.drawCurve(curveANeg, this.colors.popA.neg, false, mapX, mapY);
    }
    // Population B Negative
    if (this.visible.popBNeg) {
      this.drawCurve(curveBNeg, this.colors.popB.neg, false, mapX, mapY);
    }

    // Population A Positive
    if (this.visible.popAPos) {
      this.drawCurve(curveAPos, this.colors.popA.primary, false, mapX, mapY);
    }
    // Population B Positive
    if (this.visible.popBPos) {
      this.drawCurve(curveBPos, this.colors.popB.primary, false, mapX, mapY);
    }

    // Draw Threshold Lines
    const thresholdAX = mapX(data.threshold_a);
    const thresholdBX = mapX(data.threshold_b);

    // If they are the same (or very close), just draw one white one
    if (Math.abs(thresholdAX - thresholdBX) < 1) {
      this.drawThreshold(
        thresholdAX,
        height,
        padding,
        this.colors.threshold,
        "Threshold"
      );
    } else {
      // Draw separate colored lines
      this.drawThreshold(
        thresholdAX,
        height,
        padding,
        this.colors.popA.primary,
        "Thresh A"
      );
      this.drawThreshold(
        thresholdBX,
        height,
        padding,
        this.colors.popB.primary,
        "Thresh B"
      );
    }
  }

  drawAxes(width, height, padding) {
    const ctx = this.ctx;
    ctx.strokeStyle = this.colors.grid;
    ctx.lineWidth = 1;

    // X-axis
    ctx.beginPath();
    ctx.moveTo(padding.left, height - padding.bottom);
    ctx.lineTo(width - padding.right, height - padding.bottom);
    ctx.stroke();

    // Y-axis
    ctx.beginPath();
    ctx.moveTo(padding.left, height - padding.bottom);
    ctx.lineTo(padding.left, padding.top);
    ctx.stroke();

    // Labels
    ctx.fillStyle = this.colors.text;
    ctx.font = "10px Inter";
    ctx.textAlign = "center";

    // X labels (0, 50, 100)
    [0, 50, 100].forEach((val) => {
      const x =
        padding.left + (val / 100) * (width - padding.left - padding.right);
      ctx.fillText(val, x, height - 10);
    });
  }

  drawCurve(curveData, color, isDashed, mapX, mapY) {
    const ctx = this.ctx;
    const height = this.canvas.height;
    const paddingBottom = 30; // Match padding.bottom

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    if (isDashed) {
      ctx.setLineDash([5, 5]);
    } else {
      ctx.setLineDash([]);
    }

    // Draw line
    for (let i = 0; i < curveData.x.length; i++) {
      const x = mapX(curveData.x[i]);
      const y = mapY(curveData.y[i]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Fill area (opacity based on type)
    ctx.lineTo(
      mapX(curveData.x[curveData.x.length - 1]),
      height - paddingBottom
    );
    ctx.lineTo(mapX(curveData.x[0]), height - paddingBottom);
    ctx.fillStyle = color;
    ctx.globalAlpha = isDashed ? 0.2 : 0.4; // Distinct colors allow higher opacity
    ctx.fill();
    ctx.globalAlpha = 1.0;
    ctx.setLineDash([]);
  }

  drawThreshold(x, height, padding, color, label) {
    const ctx = this.ctx;

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.moveTo(x, padding.top);
    ctx.lineTo(x, height - padding.bottom);
    ctx.stroke();

    // Add label
    ctx.fillStyle = color;
    ctx.font = "bold 12px Inter";
    ctx.textAlign = "center";
    ctx.fillText(label, x, padding.top - 5);
  }

  scaleCurve(curve, scalar) {
    return {
      x: curve.x,
      y: curve.y.map((val) => val * scalar),
    };
  }
}
