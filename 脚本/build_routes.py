#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract real footway paths for routes A/B, add lake island, beeline, shade marks,
and rebuild the prototype with correct z-order.
"""

import json, os, re

# Load OSM data
data = json.load(open('bnbu-campus-map/osm_full.json', encoding='utf-8'))

# Projection constants (same as render_map.py)
LAT0, LAT1 = 22.3493, 22.3558
LON0, LON1 = 113.5118, 113.5206
W, H, PAD = 1200, 840, 20
KX = 111320 * 0.9146  # cos(22.35°)

def proj(lat, lon):
    y = H - PAD - ((lat - LAT0) / (LAT1 - LAT0)) * (H - 2 * PAD)
    x = PAD + ((lon - LON0) / (LON1 - LON0)) * (W - 2 * PAD)
    return (x, y)

def path_of(pts):
    if not pts:
        return ''
    return 'M ' + ' L '.join(f'{p[0]:.1f} {p[1]:.1f}' for p in pts)

def get_pts(el):
    geom = el.get('geometry', [])
    if geom:
        return [(p['lat'], p['lon']) for p in geom]
    c = el.get('center')
    if c:
        if isinstance(c, dict):
            return [(c['lat'], c['lon'])]
        elif isinstance(c, (list, tuple)) and len(c) >= 2:
            return [(c[0], c[1])]
    return []

# ===== Route A: Library → V27 via steps (shorter, with steps) =====
# Pick footways that form a connected path from library area to V27 area
# Library ~22.3525, 113.5157; V27 ~22.3535, 113.5127
# Route A: library 2F exit → footway northwest → steps down → footway → V27
# Based on OSM data, pick segments in order

route_a_segments = []
route_b_segments = []

# Helper: find segments by bbox overlap
def in_corridor(el, lat0, lat1, lon0, lon1):
    pts = get_pts(el)
    if not pts:
        return False
    return any(lat0 <= la <= lat1 and lon0 <= lo <= lon1 for la, lo in pts)

# Collect all footway/steps/path/cycleway in the corridor
all_paths = []
for el in data.get('footpaths', []) + data.get('roads', []):
    hw = el['tags'].get('highway', '')
    if hw not in ('footway', 'path', 'steps', 'cycleway', 'pedestrian', 'living_street'):
        continue
    pts = get_pts(el)
    if not pts:
        continue
    # Must be in general campus area
    if not all(LAT0 <= la <= LAT1 and LON0 <= lo <= LON1 for la, lo in pts):
        continue
    all_paths.append({
        'hw': hw,
        'name': el['tags'].get('name', ''),
        'pts': pts,
        'center': (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
    })

# Route A: library → T3 north → steps → V27 direction (northwest corridor)
# Filter paths in the direct corridor: lat 22.3522-22.3538, lon 113.5125-113.5160
a_paths = [p for p in all_paths if in_corridor(p, 22.3522, 22.3538, 113.5125, 113.5160)]
# Sort by distance from library (22.3525, 113.5157) to path center
lib = (22.3525, 113.5157)
v27 = (22.3535, 113.5127)

def dist(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

a_paths.sort(key=lambda p: dist(p['center'], lib))

# For route A, pick the most direct northwest paths (steps + footways going NW)
# We want paths that go from library area toward V27 area
# Pick top paths that are progressively closer to V27
route_a_chosen = []
used = set()
current = lib
for _ in range(15):
    best = None
    best_score = 999
    for i, p in enumerate(a_paths):
        if i in used:
            continue
        d_to_current = dist(p['center'], current)
        d_to_v27 = dist(p['center'], v27)
        # Prefer paths closer to current, and moving toward V27
        score = d_to_current + d_to_v27 * 0.5
        if score < best_score:
            best_score = score
            best = i
    if best is None:
        break
    used.add(best)
    route_a_chosen.append(a_paths[best])
    current = a_paths[best]['center']
    if dist(current, v27) < 0.0003:
        break

# Route B: library → west → gym → V28 → V29 → V27 (longer, all flat)
# This goes west first then north: lon 113.5130-113.5160, lat 22.3520-22.3540
b_paths = [p for p in all_paths if in_corridor(p, 22.3518, 22.3542, 113.5120, 113.5165)]
# We want paths that go west from library, then north to V27
# Sort by: first go west (decrease lon), then go north (increase lat)
def b_score(p):
    c = p['center']
    # Prefer westward then northward
    west_bonus = max(0, lib[1] - c[1]) * 2  # going west
    north_bonus = max(0, c[0] - lib[0]) * 1.5  # going north
    return west_bonus + north_bonus

b_paths.sort(key=b_score, reverse=True)

# Pick a connected chain going west then north
route_b_chosen = []
used_b = set()
current_b = lib
for _ in range(20):
    best = None
    best_score = -999
    for i, p in enumerate(b_paths):
        if i in used_b:
            continue
        d = dist(p['center'], current_b)
        if d > 0.002:  # too far
            continue
        c = p['center']
        score = 0
        if c[1] < current_b[1]:  # going west
            score += 3
        if c[0] > current_b[0]:  # going north
            score += 2
        score -= d * 500
        if score > best_score:
            best_score = score
            best = i
    if best is None:
        break
    used_b.add(best)
    route_b_chosen.append(b_paths[best])
    current_b = b_paths[best]['center']
    if dist(current_b, v27) < 0.0003:
        break

# Now convert to SVG paths
# Route A: combine all chosen segments
a_svg_paths = []
for p in route_a_chosen:
    svg_pts = [proj(la, lo) for la, lo in p['pts']]
    d = path_of(svg_pts)
    if d:
        stroke = '#dc2626' if p['hw'] == 'steps' else '#2563eb'
        dash = 'stroke-dasharray="6 4"' if p['hw'] == 'steps' else ''
        width = '5' if p['hw'] == 'steps' else '4'
        a_svg_paths.append(f'<path class="lyr-route route-A" d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" {dash}/>')

# Route B: combine all chosen segments
b_svg_paths = []
for p in route_b_chosen:
    svg_pts = [proj(la, lo) for la, lo in p['pts']]
    d = path_of(svg_pts)
    if d:
        b_svg_paths.append(f'<path class="lyr-route route-B" d="{d}" fill="none" stroke="#16a34a" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.7"/>')

# ===== Beeline: Library center → V27 center (red thin dashed) =====
lib_center = proj(22.3525, 113.5157)
v27_center = proj(22.3535, 113.5127)
beeline = f'<path class="lyr-beeline" d="M {lib_center[0]:.1f} {lib_center[1]:.1f} L {v27_center[0]:.1f} {v27_center[1]:.1f}" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.6"/>'

# ===== Lake Island =====
# User confirmed there's a small island in the center lake
# Place it roughly in the center of the lake
ISLAND = [
    (22.35235, 113.51590),
    (22.35240, 113.51605),
    (22.35250, 113.51610),
    (22.35255, 113.51600),
    (22.35250, 113.51585),
    (22.35240, 113.51580),
]
island_pts = [proj(la, lo) for la, lo in ISLAND]
island_d = path_of(island_pts)
island_svg = f'<path d="{island_d}" fill="#c8e6c9" stroke="#81c784" stroke-width="1"/>'

# Bridge to island (from lake shore)
BRIDGE = [(22.35245, 113.51575), (22.35242, 113.51588)]
bridge_pts = [proj(la, lo) for la, lo in BRIDGE]
bridge_d = path_of(bridge_pts)
bridge_svg = f'<path d="{bridge_d}" fill="none" stroke="#d97757" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>'

# Label for island
ix, iy = proj(22.35245, 113.51595)
island_label = f'<text class="lbl" x="{ix:.0f}" y="{iy:.0f}" font-size="11" font-weight="600" fill="#2e7d32" font-style="italic" paint-order="stroke" stroke="#ffffff" stroke-width="2">湖心岛</text>'

# ===== Shade markers: covered walkways & tree-shaded paths =====
# Based on research: covered walkways along student street, west-side trees
# We'll mark approximate shaded areas with translucent green polygons

# Covered walkway / student street (central east-west spine, approximate)
COVERED_WALK = [
    (22.35215, 113.51420), (22.35220, 113.51420), (22.35225, 113.51580), (22.35220, 113.51580)
]
cw_pts = [proj(la, lo) for la, lo in COVERED_WALK]
cw_d = path_of(cw_pts)
covered_svg = f'<path d="{cw_d}" fill="rgba(16,185,129,0.12)" stroke="none"/>'

# Tree-shaded western paths (approximate zone near V27/west side)
TREE_SHADE = [
    (22.35320, 113.51280), (22.35380, 113.51280),
    (22.35380, 113.51330), (22.35320, 113.51330)
]
ts_pts = [proj(la, lo) for la, lo in TREE_SHADE]
ts_d = path_of(ts_pts)
tree_svg = f'<path d="{ts_d}" fill="rgba(16,185,129,0.10)" stroke="none"/>'

# Shade labels
cwx, cwy = proj(22.35218, 113.51500)
shade_labels = f'<text class="lbl" x="{cwx:.0f}" y="{cwy:.0f}" font-size="10" font-weight="600" fill="#059669" paint-order="stroke" stroke="#ffffff" stroke-width="2">有盖连廊</text>'

tsx, tsy = proj(22.35350, 113.51305)
shade_labels += f'<text class="lbl" x="{tsx:.0f}" y="{tsy:.0f}" font-size="10" font-weight="600" fill="#059669" paint-order="stroke" stroke="#ffffff" stroke-width="2">林荫道</text>'

# ===== Build new SVG core with correct z-order =====
# Read existing SVG core and split into layers
svg_core = open('bnbu-campus-map/svg_core.txt', 'r', encoding='utf-8').read()

# Parse existing elements by class
lines = svg_core.strip().split('\n')

# Categorize
bg_lines = []
water_lines = []
green_lines = []
road_edge_lines = []
road_lines = []
foot_lines = []
step_lines = []
bld_lines = []
gate_lines = []
label_lines = []
route_old_lines = []
other_lines = []

for line in lines:
    line = line.strip()
    if not line:
        continue
    if 'width="1200" height="840"' in line or '<rect width=' in line:
        bg_lines.append(line)
    elif 'lyr-water' in line or 'lyr-lake' in line:
        water_lines.append(line)
    elif 'lyr-green' in line:
        green_lines.append(line)
    elif 'lyr-road-edge' in line:
        road_edge_lines.append(line)
    elif 'lyr-road' in line and 'lyr-road-edge' not in line:
        road_lines.append(line)
    elif 'lyr-foot' in line:
        foot_lines.append(line)
    elif 'lyr-steps' in line:
        step_lines.append(line)
    elif 'class="bld' in line or 'bld ' in line:
        bld_lines.append(line)
    elif 'lyr-gate' in line:
        gate_lines.append(line)
    elif 'lyr-route' in line or 'route-step' in line or 'lyr-beeline' in line:
        route_old_lines.append(line)
    elif 'class="lbl' in line:
        label_lines.append(line)
    elif '<path d=' in line and 'fill="none" stroke="#d97757"' in line:
        # boardwalk
        water_lines.append(line)
    else:
        other_lines.append(line)

# Assemble in z-order (back to front)
new_svg_lines = []
new_svg_lines.extend(bg_lines)
new_svg_lines.extend(water_lines)
new_svg_lines.append(island_svg)
new_svg_lines.append(bridge_svg)
new_svg_lines.append(island_label)
new_svg_lines.extend(green_lines)
# Shade zones (under roads)
new_svg_lines.append(covered_svg)
new_svg_lines.append(tree_svg)
new_svg_lines.append(shade_labels)
new_svg_lines.extend(road_edge_lines)
new_svg_lines.extend(road_lines)
new_svg_lines.extend(foot_lines)
new_svg_lines.extend(step_lines)
new_svg_lines.extend(bld_lines)
# Routes on top of buildings
new_svg_lines.append(beeline)
new_svg_lines.extend(a_svg_paths)
new_svg_lines.extend(b_svg_paths)
# Start/end markers
new_svg_lines.append(f'<circle class="lyr-route" cx="{lib_center[0]:.0f}" cy="{lib_center[1]:.0f}" r="8" fill="#16a34a" stroke="#fff" stroke-width="2.5"/>')
new_svg_lines.append(f'<text class="lbl lyr-route" x="{lib_center[0]:.0f}" y="{lib_center[1]+20:.0f}" font-size="13" font-weight="700" fill="#15803d" paint-order="stroke" stroke="#fff" stroke-width="3">起·图书馆 2F出口</text>')
new_svg_lines.append(f'<circle class="lyr-route" cx="{v27_center[0]:.0f}" cy="{v27_center[1]:.0f}" r="8" fill="#dc2626" stroke="#fff" stroke-width="2.5"/>')
new_svg_lines.append(f'<text class="lbl lyr-route" x="{v27_center[0]:.0f}" y="{v27_center[1]-12:.0f}" font-size="13" font-weight="700" fill="#b91c1c" paint-order="stroke" stroke="#fff" stroke-width="3">终·V27 1F入口</text>')
# Steps markers on route A (find steps segments)
for p in route_a_chosen:
    if p['hw'] == 'steps':
        mid = p['pts'][len(p['pts'])//2]
        mx, my = proj(mid[0], mid[1])
        new_svg_lines.append(f'<circle class="lyr-route-step" cx="{mx:.0f}" cy="{my:.0f}" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>')
# Gate and other labels
new_svg_lines.extend(gate_lines)
new_svg_lines.extend(label_lines)
new_svg_lines.extend(other_lines)

new_svg_core = '\n'.join(new_svg_lines)

# Write new svg core
with open('bnbu-campus-map/svg_core_v2.txt', 'w', encoding='utf-8') as f:
    f.write(new_svg_core)

print(f'Route A: {len(route_a_chosen)} segments, {len(a_svg_paths)} svg paths')
print(f'Route B: {len(route_b_chosen)} segments, {len(b_svg_paths)} svg paths')
print(f'Beeline: {beeline[:60]}...')
print(f'SVG core written: {len(new_svg_core)} chars')

# Now rebuild the HTML using the pretty builder pattern
# Read the pretty HTML template
html = open('invisible-distance-prototype/index.html', 'r', encoding='utf-8').read()

# Find and replace the SVG content
# The SVG starts after <svg id="campusMap" ...> and ends before </div> (map-panel)
# Find the SVG block
svg_start = html.find('<svg id="campusMap"')
svg_end_marker = '</svg>'
svg_end = html.find(svg_end_marker, svg_start)
if svg_start > 0 and svg_end > 0:
    # Find the actual end of SVG tag
    svg_tag_end = html.find('>', svg_start) + 1
    before = html[:svg_tag_end]
    after = html[svg_end:]
    new_html = before + '\n' + new_svg_core + '\n' + after
    
    # Update legend to include shade and beeline
    legend_old = '<span><span class="dot" style="background:linear-gradient(135deg,#34d399,#10b981)"></span> 路线 B（绕行平路）</span>'
    legend_new = legend_old + '\n        <span><span class="dot" style="background:#ef4444"></span> 方向直线</span>\n        <span><span class="dot" style="background:rgba(16,185,129,0.3);border:1px solid #10b981"></span> 遮阴/连廊区</span>'
    new_html = new_html.replace(legend_old, legend_new)
    
    # Add shade zone CSS
    css_insert = '.lyr-beeline { transition: opacity .4s; }\n  .view-wheelchair .lyr-beeline { opacity: 0.3; }'
    new_html = new_html.replace('.route-A { opacity: 0.85;', css_insert + '\n  .route-A { opacity: 0.85;')
    
    with open('invisible-distance-prototype/index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print('Prototype rebuilt successfully')
else:
    print('Could not find SVG block in HTML')
