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
        bg: "rgba(67, 97, 238, 0.2)",
      },
      popB: {
        primary: "#f72585",
        bg: "rgba(247, 37, 133, 0.2)",
      },
      text: "#a0a0b0",
      grid: "rgba(255, 255, 255, 0.05)",
      threshold: "#fff",
    };

    // Handle resizing
    this.resize();
    window.addEventListener("resize", () => this.resize());
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
    const allY = [
      ...data.population_a.curves.positive.y,
      ...data.population_a.curves.negative.y,
      ...data.population_b.curves.positive.y,
      ...data.population_b.curves.negative.y,
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

    // Population A Negative (dashed)
    this.drawCurve(
      data.population_a.curves.negative,
      this.colors.popA.primary,
      true,
      mapX,
      mapY
    );

    // Population A Positive (solid)
    this.drawCurve(
      data.population_a.curves.positive,
      this.colors.popA.primary,
      false,
      mapX,
      mapY
    );

    // Population B Negative (dashed)
    this.drawCurve(
      data.population_b.curves.negative,
      this.colors.popB.primary,
      true,
      mapX,
      mapY
    );

    // Population B Positive (solid)
    this.drawCurve(
      data.population_b.curves.positive,
      this.colors.popB.primary,
      false,
      mapX,
      mapY
    );

    // Draw Threshold Line
    const thresholdX = mapX(data.threshold);
    this.drawThreshold(thresholdX, height, padding);
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
    ctx.globalAlpha = isDashed ? 0.05 : 0.1; // Lighter fill for negative
    ctx.fill();
    ctx.globalAlpha = 1.0;
    ctx.setLineDash([]);
  }

  drawThreshold(x, height, padding) {
    const ctx = this.ctx;

    ctx.beginPath();
    ctx.strokeStyle = this.colors.threshold;
    ctx.lineWidth = 2;
    ctx.moveTo(x, padding.top);
    ctx.lineTo(x, height - padding.bottom);
    ctx.stroke();

    // Add label
    ctx.fillStyle = this.colors.threshold;
    ctx.font = "bold 12px Inter";
    ctx.textAlign = "center";
    ctx.fillText("Threshold", x, padding.top - 5);
  }
}
