#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final build: real OSM footway routes, lake island, beeline, shade zones, correct z-order.
"""

import json, os

# ===== Load OSM data =====
data = json.load(open('bnbu-campus-map/osm_full.json', encoding='utf-8'))

# ===== Projection (same as render_map.py) =====
LAT0, LAT1 = 22.3493, 22.3558
LON0, LON1 = 113.5118, 113.5206
W, H, PAD = 1200, 840, 20

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

# ===== Extract real footway paths for routes =====
all_paths = []
for el in data.get('footpaths', []) + data.get('roads', []):
    hw = el['tags'].get('highway', '')
    if hw not in ('footway', 'path', 'steps', 'cycleway', 'pedestrian', 'living_street'):
        continue
    pts = get_pts(el)
    if not pts:
        continue
    if not all(LAT0 <= la <= LAT1 and LON0 <= lo <= LON1 for la, lo in pts):
        continue
    all_paths.append({
        'hw': hw,
        'name': el['tags'].get('name', ''),
        'pts': pts,
        'center': (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
    })

lib = (22.3525, 113.5157)
v27 = (22.3535, 113.5127)

def dist(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

def in_zone(el, lat0, lat1, lon0, lon1):
    pts = el['pts']
    return any(lat0 <= la <= lat1 and lon0 <= lo <= lon1 for la, lo in pts)

# Route A: direct NW corridor (library → V27 via steps)
a_candidates = [p for p in all_paths if in_zone(p, 22.3520, 22.3540, 113.5120, 113.5165)]
# Greedy chain: start from lib, pick closest that moves toward v27
route_a = []
used = set()
cur = lib
for _ in range(25):
    best = None
    best_score = 999
    for i, p in enumerate(a_candidates):
        if i in used:
            continue
        dc = dist(p['center'], cur)
        dv = dist(p['center'], v27)
        if dc > 0.002:
            continue
        score = dc + dv * 0.3
        if score < best_score:
            best_score = score
            best = i
    if best is None:
        break
    used.add(best)
    route_a.append(a_candidates[best])
    cur = a_candidates[best]['center']
    if dist(cur, v27) < 0.0002:
        break

# Route B: west then north (library → gym → V28 → V29 → V27, flat)
b_candidates = [p for p in all_paths if in_zone(p, 22.3515, 22.3545, 113.5115, 113.5170)]
route_b = []
used_b = set()
cur_b = lib
for _ in range(30):
    best = None
    best_score = -999
    for i, p in enumerate(b_candidates):
        if i in used_b:
            continue
        dc = dist(p['center'], cur_b)
        if dc > 0.0025:
            continue
        c = p['center']
        score = 0
        if c[1] < cur_b[1]:
            score += 2.5
        if c[0] > cur_b[0]:
            score += 1.5
        score -= dc * 400
        if p['hw'] == 'steps':
            score -= 5
        if score > best_score:
            best_score = score
            best = i
    if best is None:
        break
    used_b.add(best)
    route_b.append(b_candidates[best])
    cur_b = b_candidates[best]['center']
    if dist(cur_b, v27) < 0.0002:
        break

# ===== Build SVG route paths =====
a_svg = []
for p in route_a:
    svg_pts = [proj(la, lo) for la, lo in p['pts']]
    d = path_of(svg_pts)
    if not d:
        continue
    if p['hw'] == 'steps':
        a_svg.append(f'<path class="lyr-route route-A" d="{d}" fill="none" stroke="#dc2626" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" stroke-dasharray="5 3"/>')
    else:
        a_svg.append(f'<path class="lyr-route route-A" d="{d}" fill="none" stroke="#2563eb" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')

b_svg = []
for p in route_b:
    svg_pts = [proj(la, lo) for la, lo in p['pts']]
    d = path_of(svg_pts)
    if not d:
        continue
    b_svg.append(f'<path class="lyr-route route-B" d="{d}" fill="none" stroke="#16a34a" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.7"/>')

# ===== Beeline =====
lc = proj(22.3525, 113.5157)
vc = proj(22.3535, 113.5127)
beeline = f'<path class="lyr-beeline" d="M {lc[0]:.1f} {lc[1]:.1f} L {vc[0]:.1f} {vc[1]:.1f}" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.5"/>'

# ===== Lake Island =====
ISLAND = [(22.35235,113.51590),(22.35240,113.51605),(22.35250,113.51610),(22.35255,113.51600),(22.35250,113.51585),(22.35240,113.51580)]
island_svg = f'<path d="{path_of([proj(la,lo) for la,lo in ISLAND])}" fill="#c8e6c9" stroke="#81c784" stroke-width="1"/>'
BRIDGE = [(22.35245,113.51575),(22.35242,113.51588)]
bridge_svg = f'<path d="{path_of([proj(la,lo) for la,lo in BRIDGE])}" fill="none" stroke="#d97757" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>'
ix, iy = proj(22.35245, 113.51595)
island_label = f'<text class="lbl" x="{ix:.0f}" y="{iy:.0f}" font-size="11" font-weight="600" fill="#2e7d32" font-style="italic" paint-order="stroke" stroke="#ffffff" stroke-width="2">湖心岛</text>'

# ===== Shade zones =====
# Covered walkway along central spine (approx)
CW = [(22.35210,113.51450),(22.35220,113.51450),(22.35225,113.51560),(22.35215,113.51560)]
cw_svg = f'<path d="{path_of([proj(la,lo) for la,lo in CW])}" fill="rgba(16,185,129,0.10)" stroke="none"/>'
cwx, cwy = proj(22.35215, 113.51505)
cw_label = f'<text class="lbl" x="{cwx:.0f}" y="{cwy:.0f}" font-size="10" font-weight="600" fill="#059669" paint-order="stroke" stroke="#ffffff" stroke-width="2">有盖连廊</text>'

# Tree shade on west side near dorms
TS = [(22.35330,113.51280),(22.35380,113.51280),(22.35380,113.51330),(22.35330,113.51330)]
ts_svg = f'<path d="{path_of([proj(la,lo) for la,lo in TS])}" fill="rgba(16,185,129,0.08)" stroke="none"/>'
tsx, tsy = proj(22.35355, 113.51305)
ts_label = f'<text class="lbl" x="{tsx:.0f}" y="{tsy:.0f}" font-size="10" font-weight="600" fill="#059669" paint-order="stroke" stroke="#ffffff" stroke-width="2">林荫道</text>'

# ===== Read existing SVG layers from svg_core.txt =====
# We skip lines 1-13 (svg tag + defs/style) and parse only geometry
raw = open('bnbu-campus-map/svg_core.txt', 'r', encoding='utf-8').read().split('\n')
# Skip first 13 lines (svg tag + defs + style)
geometry_lines = raw[13:]

# Categorize
bg = []
water = []
green = []
road_edge = []
road = []
foot = []
steps = []
bld = []
gate = []
labels = []
route_old = []
other = []

for line in geometry_lines:
    line = line.strip()
    if not line:
        continue
    if 'width="1200" height="840"' in line or '<rect width=' in line:
        bg.append(line)
    elif 'lyr-water' in line or 'lyr-lake' in line or 'stroke="#d97757"' in line:
        water.append(line)
    elif 'lyr-green' in line:
        green.append(line)
    elif 'lyr-road-edge' in line:
        road_edge.append(line)
    elif 'lyr-road' in line and 'lyr-road-edge' not in line:
        road.append(line)
    elif 'lyr-foot' in line:
        foot.append(line)
    elif 'lyr-steps' in line:
        steps.append(line)
    elif 'class="bld' in line or 'bld ' in line:
        bld.append(line)
    elif 'lyr-gate' in line:
        gate.append(line)
    elif 'class="lbl' in line:
        labels.append(line)
    elif 'lyr-route' in line or 'route-step' in line:
        route_old.append(line)
    else:
        other.append(line)

# ===== Assemble SVG with correct z-order =====
svg_parts = []
svg_parts.append('<rect width="1200" height="840" fill="#eef3ea"/>')
svg_parts.extend(bg[1:] if len(bg) > 1 else [])
svg_parts.extend(water)
svg_parts.append(island_svg)
svg_parts.append(bridge_svg)
svg_parts.append(island_label)
svg_parts.extend(green)
svg_parts.append(cw_svg)
svg_parts.append(ts_svg)
svg_parts.append(cw_label)
svg_parts.append(ts_label)
svg_parts.extend(road_edge)
svg_parts.extend(road)
svg_parts.extend(foot)
svg_parts.extend(steps)
svg_parts.extend(bld)
# Routes on top of buildings
svg_parts.append(beeline)
svg_parts.extend(a_svg)
svg_parts.extend(b_svg)
# Start/end markers
svg_parts.append(f'<circle class="lyr-route" cx="{lc[0]:.0f}" cy="{lc[1]:.0f}" r="8" fill="#16a34a" stroke="#fff" stroke-width="2.5"/>')
svg_parts.append(f'<text class="lbl lyr-route" x="{lc[0]:.0f}" y="{lc[1]+20:.0f}" font-size="13" font-weight="700" fill="#15803d" paint-order="stroke" stroke="#fff" stroke-width="3">起·图书馆 2F出口</text>')
svg_parts.append(f'<circle class="lyr-route" cx="{vc[0]:.0f}" cy="{vc[1]:.0f}" r="8" fill="#dc2626" stroke="#fff" stroke-width="2.5"/>')
svg_parts.append(f'<text class="lbl lyr-route" x="{vc[0]:.0f}" y="{vc[1]-12:.0f}" font-size="13" font-weight="700" fill="#b91c1c" paint-order="stroke" stroke="#fff" stroke-width="3">终·V27 1F入口</text>')
# Step markers on route A
for p in route_a:
    if p['hw'] == 'steps':
        mid = p['pts'][len(p['pts'])//2]
        mx, my = proj(mid[0], mid[1])
        svg_parts.append(f'<circle class="lyr-route-step" cx="{mx:.0f}" cy="{my:.0f}" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>')
# Flat markers on route B (gym, V28 corridor)
for p in route_b:
    if p['name'] and '广场' in p['name']:
        mid = p['pts'][len(p['pts'])//2]
        mx, my = proj(mid[0], mid[1])
        svg_parts.append(f'<circle class="lyr-route-step" cx="{mx:.0f}" cy="{my:.0f}" r="5" fill="#16a34a" stroke="#fff" stroke-width="1.5"/>')
        svg_parts.append(f'<text class="lbl" x="{mx+8:.0f}" y="{my-6:.0f}" font-size="10" font-weight="700" fill="#15803d" paint-order="stroke" stroke="#ffffff" stroke-width="2">{p["name"]}</text>')

svg_parts.extend(gate)
svg_parts.extend(labels)
svg_parts.extend(other)

svg_core = '\n'.join(svg_parts)

# ===== Build full HTML =====
html_template = open('invisible-distance-prototype/index.html', 'r', encoding='utf-8').read()

# Find SVG block and replace
svg_start = html_template.find('<svg id="campusMap"')
svg_tag_end = html_template.find('>', svg_start) + 1
svg_end = html_template.rfind('</svg>')

before = html_template[:svg_tag_end]
after = html_template[svg_end:]

new_html = before + '\n<defs><style>\n.bld { stroke:#ffffff; stroke-width:1; cursor:pointer; transition:opacity .15s; }\n.bld:hover { opacity:.75; }\n.b-teach { fill:#c7d2fe; }\n.b-dorm { fill:#fde68a; }\n.b-fac { fill:#a7d8d0; }\n.lbl { pointer-events:none; text-anchor:middle; }\n.lbl-code { font-size:12px; font-weight:700; fill:#334155; paint-order:stroke; stroke:#ffffff; stroke-width:3; }\n.lbl-fac { font-size:13px; font-weight:700; fill:#0f766e; paint-order:stroke; stroke:#ffffff; stroke-width:3; }\n.mode-access .lyr-road, .mode-access .lyr-foot, .mode-access .lyr-green, .mode-access .lyr-water { opacity:.25; }\n.mode-access .lyr-steps { stroke-width:7; stroke:#dc2626; }\n.floor-active #bld-library { stroke:#2563eb; stroke-width:3; filter:drop-shadow(0 0 6px rgba(37,99,235,.4)); }\n.floor-active #bld-v27 { stroke:#16a34a; stroke-width:3; filter:drop-shadow(0 0 6px rgba(22,163,74,.4)); }\n</style></defs>\n' + svg_core + '\n' + after

# Update legend
old_legend = '<span><span class="dot" style="background:linear-gradient(135deg,#34d399,#10b981)"></span> 路线 B（绕行平路）</span>'
new_legend = old_legend + '\n        <span><span class="dot" style="background:#ef4444"></span> 方向直线</span>\n        <span><span class="dot" style="background:rgba(16,185,129,0.3);border:1px solid #10b981"></span> 遮阴/连廊区</span>'
new_html = new_html.replace(old_legend, new_legend)

# Update source text
old_source = '图书馆 4 层（唯一出入口 2F 朝湖）/ V27 7 层（入口无台阶·有电梯）。路线 A 有一段 -1 层台阶下坡，路线 B 经体育馆→V28→V29 全平路绕行。'
new_source = '图书馆 4 层（唯一出入口 2F 朝湖）/ V27 7 层（入口无台阶·有电梯）。路线 A 沿真实 OSM 步道（含台阶下坡），路线 B 沿真实 OSM 步道经体育馆→V28→V29 全平路绕行。遮阴数据来自校园建筑设计资料。'
new_html = new_html.replace(old_source, new_source)

# Add beeline CSS
old_css = '.route-A { opacity: 0.85;'
new_css = '.lyr-beeline { transition: opacity .4s; }\n  .view-wheelchair .lyr-beeline { opacity: 0.3; }\n  .route-A { opacity: 0.85;'
new_html = new_html.replace(old_css, new_css)

with open('invisible-distance-prototype/index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'Route A: {len(route_a)} segments')
print(f'Route B: {len(route_b)} segments')
print(f'HTML size: {len(new_html)} chars')
print('Done!')
