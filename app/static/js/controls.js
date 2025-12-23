/**
 * Controls Module
 * Handles user input from sliders and updates the state
 */

class Controls {
  constructor(onChangeCallback) {
    this.onChange = onChangeCallback;

    // Define all input IDs
    // Removed single 'threshold' in favor of 'threshold-a' and 'threshold-b'
    this.inputs = [
      "threshold-a",
      "threshold-b",
      "pop-a-prevalence",
      "pop-a-mu-pos",
      "pop-a-sigma-pos",
      "pop-a-mu-neg",
      "pop-a-sigma-neg",
      "pop-b-prevalence",
      "pop-b-mu-pos",
      "pop-b-sigma-pos",
      "pop-b-mu-neg",
      "pop-b-mu-neg",
      "pop-b-sigma-neg",
      "opt-fp-weight",
      "opt-fn-weight",
    ];

    // Track Equal Threshold constraint separately
    this.optEqualThresholds = document.getElementById("opt-equal-thresholds");
    this.btnOptimize = document.getElementById("btn-optimize");

    this.initListeners();
    this.initThresholdLock();
  }

  initListeners() {
    this.inputs.forEach((id) => {
      const input = document.getElementById(id);
      const display = document.getElementById(`${id}-value`);

      if (input) {
        // UPDATE DISPLAY on slider move
        input.addEventListener("input", (e) => {
          if (display) display.textContent = e.target.value;

          // Handle threshold locking
          if (id === "threshold-a" || id === "threshold-b") {
            this.handleThresholdSync(id, e.target.value);
          }
        });

        // TRIGGER UPDATE on input (live)
        input.addEventListener("input", () => this.triggerUpdate());

        // CLICK TO EDIT
        if (display) {
          this.makeEditable(display, input);
        }
      }
    });

    if (this.btnOptimize) {
      this.btnOptimize.addEventListener("click", () => this.handleOptimize());
    }
  }

  async handleOptimize() {
    // 1. Get Params
    const params = this.getParams();

    // 2. Add extra optimization params
    const payload = {
      ...params,
      fp_weight: parseFloat(document.getElementById("opt-fp-weight").value),
      fn_weight: parseFloat(document.getElementById("opt-fn-weight").value),
      constraint_equal: this.optEqualThresholds
        ? this.optEqualThresholds.checked
        : true,
    };

    // 3. Call API
    try {
      this.btnOptimize.textContent = "Optimizing...";
      this.btnOptimize.disabled = true;

      const response = await fetch("/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error("Optimization failed");

      const result = await response.json();

      // 4. Update Thresholds
      // Update input values
      const sliderA = document.getElementById("threshold-a");
      const sliderB = document.getElementById("threshold-b");

      if (sliderA) {
        sliderA.value = result.threshold_a;
        sliderA.dispatchEvent(new Event("input")); // Updates display & triggers cycle
      }
      if (sliderB) {
        sliderB.value = result.threshold_b;
        sliderB.dispatchEvent(new Event("input"));
      }

      console.log(`Optimization result: Cost ${result.min_cost}`);
    } catch (e) {
      console.error(e);
      alert("Optimization failed: " + e.message);
    } finally {
      this.btnOptimize.textContent = "Optimize Thresholds";
      this.btnOptimize.disabled = false;
    }
  }

  initThresholdLock() {
    const lockCheckbox = document.getElementById("threshold-lock");
    if (lockCheckbox) {
      lockCheckbox.addEventListener("change", () => {
        // If locking, sync B to A immediately
        if (lockCheckbox.checked) {
          const valA = document.getElementById("threshold-a").value;
          const sliderB = document.getElementById("threshold-b");
          sliderB.value = valA;
          // Trigger input event to update display and sync
          sliderB.dispatchEvent(new Event("input"));
        }
      });
    }
  }

  handleThresholdSync(changedId, value) {
    const lockCheckbox = document.getElementById("threshold-lock");
    if (lockCheckbox && lockCheckbox.checked) {
      const targetId =
        changedId === "threshold-a" ? "threshold-b" : "threshold-a";
      const targetSlider = document.getElementById(targetId);
      const targetDisplay = document.getElementById(`${targetId}-value`);

      if (targetSlider && targetSlider.value !== value) {
        targetSlider.value = value;
        if (targetDisplay) targetDisplay.textContent = value;
      }
    }
  }

  makeEditable(displaySpan, inputRange) {
    displaySpan.title = "Click to edit";

    displaySpan.addEventListener("click", () => {
      if (displaySpan.querySelector("input")) return; // Already editing

      const currentVal = displaySpan.textContent;
      const input = document.createElement("input");
      input.type = "number";
      input.value = currentVal;
      input.className = "editable-input";

      // Match step from range input
      if (inputRange.step) input.step = inputRange.step;
      if (inputRange.min) input.min = inputRange.min;
      if (inputRange.max) input.max = inputRange.max;

      const save = () => {
        let val = parseFloat(input.value);

        // Validate constraints
        const min = parseFloat(inputRange.min);
        const max = parseFloat(inputRange.max);
        if (val < min) val = min;
        if (val > max) val = max;
        if (isNaN(val)) val = parseFloat(inputRange.value);

        // Update UI
        displaySpan.textContent = val;
        inputRange.value = val;

        // Sync if needed (for thresholds)
        if (inputRange.id.includes("threshold")) {
          this.handleThresholdSync(inputRange.id, val);
        }

        // Trigger App Update
        this.triggerUpdate();
      };

      // Save on blur or enter
      input.addEventListener("blur", save);
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          input.blur();
        }
      });

      displaySpan.textContent = "";
      displaySpan.appendChild(input);
      input.focus();
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
