/**
 * Model Brain & Decision Inspector for Snake AI Arena.
 * Visualizes confidence probabilities, hazard matrix, ASCII map, and raw prompts.
 */

class ModelInspectorModal {
  constructor(overlayEl) {
    this.overlay = overlayEl;
    this.currentModelId = null;
    this.currentData = null;

    // Bind close button
    const closeBtn = this.overlay.querySelector(".btn-close");
    if (closeBtn) {
      closeBtn.onclick = () => this.hide();
    }
    this.overlay.onclick = (e) => {
      if (e.target === this.overlay) this.hide();
    };
  }

  show(modelData, lastEvent = null) {
    this.currentData = modelData;
    this.currentModelId = modelData.model_id;
    this.overlay.classList.add("active");
    this.update(modelData, lastEvent);
  }

  hide() {
    this.overlay.classList.remove("active");
  }

  update(modelData, lastEvent = null) {
    if (!this.overlay.classList.contains("active")) return;
    if (modelData.model_id !== this.currentModelId) return;

    const titleEl = this.overlay.querySelector("#inspectorModelTitle");
    const typeEl = this.overlay.querySelector("#inspectorModelType");
    if (titleEl) titleEl.textContent = modelData.name;
    if (typeEl) {
      typeEl.textContent = modelData.model_type.toUpperCase();
      typeEl.style.color = modelData.color || "#00f3ff";
    }

    const dec = lastEvent?.decision || modelData.telemetry?.last_decision || {};
    const stateRepr = lastEvent?.state_repr || {};

    // 1. Probabilities Bar Chart
    const probs = dec.probabilities || {};
    const dirs = ["UP", "DOWN", "LEFT", "RIGHT"];
    const probContainer = this.overlay.querySelector("#inspectorProbBars");
    if (probContainer) {
      probContainer.innerHTML = dirs.map(d => {
        const val = probs[d] !== undefined ? probs[d] : (dec.direction === d ? dec.confidence : 0.05);
        const pct = Math.round(val * 100);
        const isChosen = dec.direction === d;
        const color = isChosen ? (modelData.color || "#00f3ff") : "rgba(255,255,255,0.4)";
        return `
          <div class="prob-bar-row">
            <span class="prob-dir" style="color:${isChosen ? color : '#94a3b8'}">${d}</span>
            <div class="prob-bar-bg">
              <div class="prob-bar-fill" style="width:${pct}%; background:${color}"></div>
            </div>
            <span class="prob-val" style="color:${isChosen ? '#fff' : '#64748b'}">${pct}%</span>
          </div>
        `;
      }).join("");
    }

    // 2. Safe moves & criteria
    const criteriaContainer = this.overlay.querySelector("#inspectorCriteria");
    if (criteriaContainer) {
      const critMap = stateRepr.criteria || {};
      criteriaContainer.innerHTML = dirs.map(d => {
        const text = critMap[d] || (dec.direction === d ? dec.reasoning : "Pending evaluation");
        const isChosen = dec.direction === d;
        return `
          <div style="font-size:0.75rem; margin-bottom:6px; font-family:var(--font-mono); color:${isChosen ? '#38bdf8' : '#64748b'}">
            <strong>${d}:</strong> ${text}
          </div>
        `;
      }).join("");
    }

    // 3. ASCII Grid Map
    const asciiBox = this.overlay.querySelector("#inspectorAsciiGrid");
    if (asciiBox) {
      asciiBox.textContent = stateRepr.ascii_grid || "(ASCII Board will appear upon first step)";
    }

    // 4. Raw Decision JSON
    const rawBox = this.overlay.querySelector("#inspectorRawJson");
    if (rawBox) {
      rawBox.textContent = JSON.stringify({
        decision: dec,
        telemetry: modelData.telemetry,
      }, null, 2);
    }
  }
}
