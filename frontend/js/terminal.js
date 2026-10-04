/**
 * Hacker Terminal & Telemetry Logger for Snake AI Arena.
 * Handles streaming stdout, model-based filtering, live search, and export.
 */

class HackerTerminalLogger {
  constructor(containerEl) {
    this.container = containerEl;
    this.logs = [];
    this.activeFilter = "ALL";
    this.searchQuery = "";
    this.autoScroll = true;
    this.maxLines = 500;
  }

  addEvent(event) {
    this.logs.push(event);
    if (this.logs.length > this.maxLines) {
      this.logs.shift();
    }
    this._appendLogLine(event);
  }

  setFilter(filterModelId) {
    this.activeFilter = filterModelId;
    this.refresh();
  }

  setSearchQuery(q) {
    this.searchQuery = (q || "").toLowerCase().trim();
    this.refresh();
  }

  setAutoScroll(enabled) {
    this.autoScroll = enabled;
  }

  clear() {
    this.logs = [];
    this.container.innerHTML = "";
  }

  refresh() {
    this.container.innerHTML = "";
    for (const ev of this.logs) {
      if (this._matchesFilter(ev)) {
        this._renderLineElement(ev);
      }
    }
    if (this.autoScroll) {
      this.container.scrollTop = this.container.scrollHeight;
    }
  }

  _matchesFilter(ev) {
    if (this.activeFilter !== "ALL") {
      const mId = (ev.model_id || "").toLowerCase();
      const filter = this.activeFilter.toLowerCase();
      if (!mId.includes(filter)) return false;
    }

    if (this.searchQuery) {
      const fullStr = JSON.stringify(ev).toLowerCase();
      if (!fullStr.includes(this.searchQuery)) return false;
    }
    return true;
  }

  _appendLogLine(ev) {
    if (this._matchesFilter(ev)) {
      this._renderLineElement(ev);
      if (this.autoScroll) {
        this.container.scrollTop = this.container.scrollHeight;
      }
    }
  }

  _renderLineElement(ev) {
    const line = document.createElement("div");
    line.className = "log-line";

    const d = new Date();
    const timeStr = d.toTimeString().split(" ")[0] + "." + String(d.getMilliseconds()).padStart(3, "0");

    const dec = ev.decision || {};
    const dir = dec.direction || "NONE";
    const conf = dec.confidence !== undefined ? (dec.confidence * 100).toFixed(0) + "%" : "--";
    const lat = dec.latency_ms !== undefined ? `${dec.latency_ms}ms` : "--";
    const cost = dec.cost_usd > 0 ? `$${dec.cost_usd.toFixed(6)}` : "$0";
    const reason = dec.reasoning || "";

    const badgeColor = ev.color || "#00f3ff";
    const shortName = ev.name ? ev.name.split(" ")[0].toUpperCase() : "MODEL";

    line.innerHTML = `
      <span class="log-time">[${timeStr}]</span>
      <span class="log-badge" style="background:${badgeColor}22; color:${badgeColor}; border:1px solid ${badgeColor}44">[${shortName}|T:${ev.turn}]</span>
      <span class="log-action" style="color:${dec.is_safe ? '#34d399' : '#f87171'}">${dir}</span>
      <span class="log-metrics">conf:${conf} lat:${lat}</span>
      <span class="log-msg">"${this._escapeHtml(reason)}"</span>
    `;

    this.container.appendChild(line);
  }

  _escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  exportLogsJson() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.logs, null, 2));
    const dlAnchor = document.createElement("a");
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `snake_arena_logs_${Date.now()}.json`);
    dlAnchor.click();
  }

  exportLogsCsv() {
    const headers = ["Turn", "ModelID", "ModelName", "Direction", "Confidence", "LatencyMs", "Safe", "Reasoning"];
    const rows = this.logs.map(l => [
      l.turn,
      `"${l.model_id}"`,
      `"${l.name}"`,
      `"${l.decision?.direction || ''}"`,
      l.decision?.confidence || 0,
      l.decision?.latency_ms || 0,
      l.decision?.is_safe ? 1 : 0,
      `"${(l.decision?.reasoning || '').replace(/"/g, '""')}"`,
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const dlAnchor = document.createElement("a");
    dlAnchor.setAttribute("href", encodeURI(csvContent));
    dlAnchor.setAttribute("download", `snake_arena_logs_${Date.now()}.csv`);
    dlAnchor.click();
  }
}
