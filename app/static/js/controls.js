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
      "opt-fpr-weight",
      "opt-fnr-weight",
      "opt-ppv-weight",
      "opt-npv-weight",
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

    // Case Studies Buttons
    const btnGeneral = document.getElementById("btn-compas-general");
    if (btnGeneral) btnGeneral.addEventListener("click", () => this.loadPreset("compas_general"));

    const btnViolent = document.getElementById("btn-compas-violent");
    if (btnViolent) btnViolent.addEventListener("click", () => this.loadPreset("compas_violent"));

    const btnReset = document.getElementById("btn-reset-gaussian");
    if (btnReset) btnReset.addEventListener("click", () => this.loadPreset("gaussian"));
  }

  loadPreset(type) {
    this.distributionType = type;
    
    const isEmpirical = type !== "gaussian";
    
    // Disable/Enable distribution sliders
    const distInputs = [
      "pop-a-mu-pos", "pop-a-sigma-pos", "pop-a-mu-neg", "pop-a-sigma-neg",
      "pop-b-mu-pos", "pop-b-sigma-pos", "pop-b-mu-neg", "pop-b-sigma-neg"
    ];
    
    distInputs.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.disabled = isEmpirical;
        if (el.parentElement) {
          el.parentElement.style.opacity = isEmpirical ? "0.5" : "1";
        }
      }
    });

    // Snap prevalence for COMPAS presets
    if (type === "compas_general") {
      this.updateSlider("pop-a-prevalence", 0.51);
      this.updateSlider("pop-b-prevalence", 0.39);
      this.updateSlider("threshold-a", 40);
      this.updateSlider("threshold-b", 40);
    } else if (type === "compas_violent") {
      this.updateSlider("pop-a-prevalence", 0.21);
      this.updateSlider("pop-b-prevalence", 0.12);
      this.updateSlider("threshold-a", 40);
      this.updateSlider("threshold-b", 40);
    }

    const labelA = isEmpirical ? "African-American" : "Population A";
    const labelB = isEmpirical ? "Caucasian" : "Population B";

    // Update Control Panel Titles
    const titleA = document.getElementById("title-pop-a");
    if (titleA) titleA.textContent = labelA;
    const titleB = document.getElementById("title-pop-b");
    if (titleB) titleB.textContent = labelB;

    // Update Confusion Matrix Titles
    const titleCmA = document.getElementById("title-cm-a");
    if (titleCmA) titleCmA.textContent = labelA;
    const titleCmB = document.getElementById("title-cm-b");
    if (titleCmB) titleCmB.textContent = labelB;

    // Update legend items
    const legAPos = document.getElementById("leg-a-pos");
    if (legAPos) legAPos.textContent = `${labelA} - Positive`;
    const legANeg = document.getElementById("leg-a-neg");
    if (legANeg) legANeg.textContent = `${labelA} - Negative`;
    const legBPos = document.getElementById("leg-b-pos");
    if (legBPos) legBPos.textContent = `${labelB} - Positive`;
    const legBNeg = document.getElementById("leg-b-neg");
    if (legBNeg) legBNeg.textContent = `${labelB} - Negative`;
    
    this.triggerUpdate();
  }

  updateSlider(id, value) {
    const el = document.getElementById(id);
    const display = document.getElementById(`${id}-value`);
    if (el) {
      el.value = value;
      if (display) display.textContent = value;
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
      w_fpr: parseFloat(document.getElementById("opt-fpr-weight").value),
      w_fnr: parseFloat(document.getElementById("opt-fnr-weight").value),
      w_ppv: parseFloat(document.getElementById("opt-ppv-weight").value),
      w_npv: parseFloat(document.getElementById("opt-npv-weight").value),
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
        const displayA = document.getElementById("threshold-a-value");
        if (displayA) displayA.textContent = Number(result.threshold_a).toFixed(1);
      }
      if (sliderB) {
        sliderB.value = result.threshold_b;
        const displayB = document.getElementById("threshold-b-value");
        if (displayB) displayB.textContent = Number(result.threshold_b).toFixed(1);
      }
      
      this.triggerUpdate();

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
    params["distribution_type"] = this.distributionType || "gaussian";
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
