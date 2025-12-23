/**
 * Main Application Entry Point
 * Orchestrates fetching data and updating visualizations
 */

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Visualizations
  const bellCurveViz = new BellCurveViz("bell-curves-canvas");

  const confusionViz = new ConfusionMatrixViz(
    "confusion-matrix-a",
    "confusion-matrix-b",
    "metrics-a",
    "metrics-b"
  );

  const impossibilityViz = new ImpossibilityViz("impossibility-viz");

  // Main Update Function
  async function updateDashboard(params) {
    try {
      // Construct query string
      const queryString = new URLSearchParams(params).toString();

      const response = await fetch(`/api/calculate?${queryString}`);
      if (!response.ok) throw new Error("Calculation failed");

      const data = await response.json();

      // Update all visualizations
      bellCurveViz.update(data);
      confusionViz.update(data);
      impossibilityViz.update(data);
    } catch (error) {
      console.error("Error updating dashboard:", error);
    }
  }

  // Initialize Controls
  const controls = new Controls((params) => {
    // Use requestAnimationFrame to prevent UI blocking on rapid changes
    requestAnimationFrame(() => updateDashboard(params));
  });

  // Initial Load
  controls.triggerUpdate();
});
