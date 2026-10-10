"""
Generates a stunning, interactive 3D WebGL Force Graph for the graphify knowledge base.
Uses 3d-force-graph (Three.js WebGL) with particle animations, 3D camera controls,
glowing community clusters, and a cyberpunk HUD inspector.
"""

import os
import re
import json

GRAPHIFY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "graphify-out"))
GRAPH_2D_FILE = os.path.join(GRAPHIFY_DIR, "graph.html")
GRAPH_3D_FILE = os.path.join(GRAPHIFY_DIR, "graph_3d.html")


def extract_data_from_graph_html():
    if not os.path.exists(GRAPH_2D_FILE):
        raise FileNotFoundError(f"{GRAPH_2D_FILE} not found!")

    with open(GRAPH_2D_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex search for RAW_NODES, RAW_EDGES, LEGEND
    nodes_match = re.search(r"const RAW_NODES\s*=\s*(\[.*?\]);", content)
    edges_match = re.search(r"const RAW_EDGES\s*=\s*(\[.*?\]);", content)
    legend_match = re.search(r"const LEGEND\s*=\s*(\[.*?\]);", content)

    if not nodes_match or not edges_match or not legend_match:
        raise ValueError("Failed to extract RAW_NODES, RAW_EDGES, or LEGEND from graph.html")

    raw_nodes = json.loads(nodes_match.group(1))
    raw_edges = json.loads(edges_match.group(1))
    raw_legend = json.loads(legend_match.group(1))

    return raw_nodes, raw_edges, raw_legend


def generate_3d_html(raw_nodes, raw_edges, raw_legend):
    # Prepare 3D format for 3d-force-graph
    # Nodes: id, name, val (size), color, community, file_type, source_file, degree
    nodes_3d = []
    for n in raw_nodes:
        # Hex color
        col = n.get("color", {}).get("background", "#00d2d3") if isinstance(n.get("color"), dict) else "#00d2d3"
        nodes_3d.append({
            "id": n["id"],
            "name": n.get("label", n["id"]),
            "val": max(2.5, float(n.get("size", 10.0)) - 7.0),
            "color": col,
            "community": n.get("community", 0),
            "community_name": n.get("community_name", "General"),
            "file_type": n.get("file_type", "code"),
            "source_file": n.get("source_file", ""),
            "degree": n.get("degree", 1),
            "title": n.get("title", n.get("label", "")),
        })

    # Links: source, target, label, confidence, color
    links_3d = []
    for e in raw_edges:
        links_3d.append({
            "source": e["from"],
            "target": e["to"],
            "label": e.get("label", "relates"),
            "confidence": e.get("confidence", "EXTRACTED"),
            "width": 1.2 if e.get("confidence") == "EXTRACTED" else 0.6,
        })

    graph_data = {
        "nodes": nodes_3d,
        "links": links_3d,
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Graphify 3D Knowledge Graph — Multi-Model AI Arena</title>
<script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
<script src="https://unpkg.com/3d-force-graph@1.73.3/dist/3d-force-graph.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #080811;
    color: #f1f5f9;
    font-family: 'Outfit', sans-serif;
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }}
  #3d-graph {{
    width: 100vw;
    height: 100vh;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1;
  }}

  /* Cyberpunk Glassmorphic Overlay */
  .hud-header {{
    position: absolute;
    top: 20px;
    left: 24px;
    z-index: 10;
    pointer-events: auto;
    background: rgba(13, 17, 23, 0.85);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 243, 255, 0.25);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), 0 0 16px rgba(0, 243, 255, 0.15);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-width: 380px;
  }}
  .hud-title {{
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, #00f3ff, #10a37f, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .hud-subtitle {{
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.4;
  }}
  .hud-stats {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #38bdf8;
    display: flex;
    gap: 12px;
    margin-top: 4px;
  }}

  /* Search & Controls */
  .search-box {{
    margin-top: 8px;
    position: relative;
  }}
  .search-input {{
    width: 100%;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 8px;
    padding: 8px 12px;
    color: #fff;
    font-size: 12px;
    outline: none;
    transition: all 0.2s;
  }}
  .search-input:focus {{
    border-color: #00f3ff;
    box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
  }}
  .search-results {{
    position: absolute;
    top: 38px;
    left: 0;
    right: 0;
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 8px;
    max-height: 200px;
    overflow-y: auto;
    display: none;
    z-index: 20;
  }}
  .search-item {{
    padding: 7px 12px;
    font-size: 12px;
    cursor: pointer;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }}
  .search-item:hover {{
    background: rgba(0, 243, 255, 0.15);
    color: #00f3ff;
  }}

  /* Mode Toggles */
  .hud-controls {{
    display: flex;
    gap: 6px;
    margin-top: 8px;
  }}
  .hud-btn {{
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.2);
    color: #cbd5e1;
    font-size: 11px;
    font-weight: 600;
    padding: 5px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .hud-btn:hover, .hud-btn.active {{
    background: rgba(0, 243, 255, 0.2);
    border-color: #00f3ff;
    color: #00f3ff;
  }}

  /* Inspector Panel (Right) */
  .inspector-panel {{
    position: absolute;
    top: 20px;
    right: 24px;
    z-index: 10;
    pointer-events: auto;
    background: rgba(13, 17, 23, 0.88);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(168, 85, 247, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), 0 0 16px rgba(168, 85, 247, 0.15);
    border-radius: 12px;
    padding: 18px;
    width: 320px;
    max-height: calc(100vh - 40px);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  .inspector-title {{
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #c084fc;
    font-weight: 700;
  }}
  .node-name {{
    font-size: 15px;
    font-weight: 700;
    color: #fff;
    word-break: break-all;
  }}
  .info-tag {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10.5px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(56, 189, 248, 0.15);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.3);
  }}
  .prop-row {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    font-size: 11.5px;
  }}
  .prop-label {{
    color: #64748b;
    font-size: 10px;
    text-transform: uppercase;
  }}
  .prop-val {{
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    word-break: break-all;
  }}
  .neighbors-box {{
    margin-top: 6px;
    border-top: 1px solid rgba(255,255,255,0.08);
    padding-top: 8px;
  }}
  .neighbor-item {{
    padding: 4px 6px;
    border-radius: 4px;
    font-size: 11px;
    cursor: pointer;
    color: #94a3b8;
    transition: all 0.15s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .neighbor-item:hover {{
    background: rgba(168, 85, 247, 0.2);
    color: #c084fc;
  }}

  /* Instructions Bottom Bar */
  .bottom-instructions {{
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 8px 18px;
    border-radius: 20px;
    font-size: 11px;
    color: #94a3b8;
    pointer-events: none;
    letter-spacing: 0.02em;
  }}
  .bottom-instructions span {{
    color: #38bdf8;
    font-weight: 600;
  }}
</style>
</head>
<body>

<div id="3d-graph"></div>

<!-- Top Left HUD -->
<div class="hud-header">
  <div class="hud-title">
    <span>🌐</span> Graphify 3D Knowledge Universe
  </div>
  <div class="hud-subtitle">
    Spatial structural graph of AST symbols, architectural dependencies, and rationale relationships.
  </div>
  <div class="hud-stats">
    <span>Nodes: {len(nodes_3d)}</span>
    <span>Edges: {len(links_3d)}</span>
    <span>Clusters: {len(raw_legend)}</span>
  </div>

  <div class="search-box">
    <input type="text" class="search-input" id="search-input" placeholder="Search files, functions, classes..." autocomplete="off">
    <div class="search-results" id="search-results"></div>
  </div>

  <div class="hud-controls">
    <button class="hud-btn active" id="btn-rotate">Auto Rotate</button>
    <button class="hud-btn" id="btn-reset-cam">Reset View</button>
    <button class="hud-btn" id="btn-switch-2d" onclick="window.location.href='/graph'">2D View</button>
  </div>
</div>

<!-- Right Inspector -->
<div class="inspector-panel" id="inspector-panel">
  <div class="inspector-title">Active Node Telemetry</div>
  <div class="node-name" id="node-name">Select a node in 3D</div>
  <div id="node-badge"></div>
  <div class="prop-row">
    <span class="prop-label">Community Module</span>
    <span class="prop-val" id="node-comm">—</span>
  </div>
  <div class="prop-row">
    <span class="prop-label">Source File Location</span>
    <span class="prop-val" id="node-source">—</span>
  </div>
  <div class="prop-row">
    <span class="prop-label">Structural Degree</span>
    <span class="prop-val" id="node-degree">—</span>
  </div>
  <div class="neighbors-box" id="neighbors-box" style="display:none;">
    <span class="prop-label">Connected Graph Neighbors</span>
    <div id="neighbors-list"></div>
  </div>
</div>

<div class="bottom-instructions">
  <span>Left Click + Drag</span> Rotate Orbit &nbsp;|&nbsp;
  <span>Right Click + Drag</span> Pan &nbsp;|&nbsp;
  <span>Scroll</span> 3D Zoom &nbsp;|&nbsp;
  <span>Click Node</span> Focus & Inspect
</div>

<script>
const gData = {json.dumps(graph_data)};
const legend = {json.dumps(raw_legend)};

const elem = document.getElementById('3d-graph');
let autoRotate = true;

const Graph = ForceGraph3D()(elem)
  .graphData(gData)
  .backgroundColor('#080811')
  .nodeId('id')
  .nodeLabel('name')
  .nodeVal('val')
  .nodeColor(node => node.color)
  .nodeResolution(16)
  .nodeOpacity(0.92)
  .linkSource('source')
  .linkTarget('target')
  .linkLabel('label')
  .linkWidth(link => link.width || 1)
  .linkColor(() => 'rgba(56, 189, 248, 0.22)')
  .linkDirectionalParticles(2)
  .linkDirectionalParticleSpeed(0.006)
  .linkDirectionalParticleWidth(1.8)
  .linkDirectionalParticleColor(() => '#00f3ff')
  .onNodeClick(node => focusOnNode(node))
  .onBackgroundClick(() => {{
    resetInspector();
  }});

// Camera Orbit
Graph.controls().autoRotate = autoRotate;
Graph.controls().autoRotateSpeed = 0.6;

document.getElementById('btn-rotate').addEventListener('click', function() {{
  autoRotate = !autoRotate;
  Graph.controls().autoRotate = autoRotate;
  this.classList.toggle('active', autoRotate);
}});

document.getElementById('btn-reset-cam').addEventListener('click', function() {{
  Graph.cameraPosition({{ x: 0, y: 0, z: 800 }}, {{ x: 0, y: 0, z: 0 }}, 1500);
}});

function focusOnNode(node) {{
  // Aim camera at node
  const distance = 90;
  const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);

  Graph.cameraPosition(
    {{ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }},
    node,
    1500
  );

  inspectNode(node);
}}

function inspectNode(node) {{
  document.getElementById('node-name').textContent = node.name;
  document.getElementById('node-badge').innerHTML = `<span class="info-tag">${{node.file_type.toUpperCase()}}</span>`;
  document.getElementById('node-comm').textContent = `${{node.community_name}} (#${{node.community}})`;
  document.getElementById('node-source').textContent = node.source_file || 'Virtual Primitive';
  document.getElementById('node-degree').textContent = `${{node.degree}} Connections`;

  // Find neighbors
  const neighbors = gData.links
    .filter(l => (l.source.id || l.source) === node.id || (l.target.id || l.target) === node.id)
    .map(l => {{
      const nId = (l.source.id || l.source) === node.id ? (l.target.id || l.target) : (l.source.id || l.source);
      return gData.nodes.find(n => n.id === nId);
    }})
    .filter(Boolean);

  const nList = document.getElementById('neighbors-list');
  const nBox = document.getElementById('neighbors-box');
  nList.innerHTML = '';

  if (neighbors.length > 0) {{
    nBox.style.display = 'block';
    neighbors.slice(0, 15).forEach(nb => {{
      const d = document.createElement('div');
      d.className = 'neighbor-item';
      d.textContent = `• ${{nb.name}} (${{nb.community_name}})`;
      d.onclick = () => focusOnNode(nb);
      nList.appendChild(d);
    }});
  }} else {{
    nBox.style.display = 'none';
  }}
}}

function resetInspector() {{
  document.getElementById('node-name').textContent = 'Select a node in 3D';
  document.getElementById('node-badge').innerHTML = '';
  document.getElementById('node-comm').textContent = '—';
  document.getElementById('node-source').textContent = '—';
  document.getElementById('node-degree').textContent = '—';
  document.getElementById('neighbors-box').style.display = 'none';
}}

// Search Filter
const sInput = document.getElementById('search-input');
const sResults = document.getElementById('search-results');

sInput.addEventListener('input', e => {{
  const q = e.target.value.toLowerCase().trim();
  sResults.innerHTML = '';
  if (!q) {{
    sResults.style.display = 'none';
    return;
  }}

  const matches = gData.nodes.filter(n =>
    n.name.toLowerCase().includes(q) ||
    n.source_file.toLowerCase().includes(q)
  ).slice(0, 8);

  if (matches.length > 0) {{
    sResults.style.display = 'block';
    matches.forEach(m => {{
      const item = document.createElement('div');
      item.className = 'search-item';
      item.textContent = `${{m.name}} (${{m.source_file || m.community_name}})`;
      item.onclick = () => {{
        focusOnNode(m);
        sResults.style.display = 'none';
        sInput.value = m.name;
      }};
      sResults.appendChild(item);
    }});
  }} else {{
    sResults.style.display = 'none';
  }}
}});

document.addEventListener('click', e => {{
  if (!sResults.contains(e.target) && e.target !== sInput) {{
    sResults.style.display = 'none';
  }}
}});

// Initial camera position
Graph.cameraPosition({{ x: 0, y: 0, z: 900 }});
</script>
</body>
</html>
"""
    with open(GRAPH_3D_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✔ Generated 3D force graph HTML at: {GRAPH_3D_FILE} ({len(html)} bytes)")


if __name__ == "__main__":
    nodes, edges, leg = extract_data_from_graph_html()
    generate_3d_html(nodes, edges, leg)
