/**
 * Controls Module
 * Handles user input from sliders and updates the state
 */

class Controls {
  constructor(onChangeCallback) {
    this.onChange = onChangeCallback;

    // Define all input IDs
    this.inputs = [
      "threshold",
      "pop-a-prevalence",
      "pop-a-mu-pos",
      "pop-a-sigma-pos",
      "pop-a-mu-neg",
      "pop-a-sigma-neg",
      "pop-b-prevalence",
      "pop-b-mu-pos",
      "pop-b-sigma-pos",
      "pop-b-mu-neg",
      "pop-b-sigma-neg",
    ];

    this.initListeners();
  }

  initListeners() {
    this.inputs.forEach((id) => {
      const input = document.getElementById(id);
      const display = document.getElementById(`${id}-value`);

      if (input) {
        // Update display immediately on input
        input.addEventListener("input", (e) => {
          if (display) display.textContent = e.target.value;
        });

        // Trigger calculation on change (or input with debounce if preferred)
        // Using input for live updates, but could be heavy if calc is slow
        // Math is simple enough for live updates
        input.addEventListener("input", () => this.triggerUpdate());
      }
    });
  }

  triggerUpdate() {
    const params = this.getParams();
    this.onChange(params);
  }

  getParams() {
    const params = {};
    this.inputs.forEach((id) => {
      const input = document.getElementById(id);
      if (input) {
        // Convert hyphens to underscores for backend compat
        const paramName = id.replace(/-/g, "_");
        params[paramName] = parseFloat(input.value);
      }
    });
    return params;
  }
}
