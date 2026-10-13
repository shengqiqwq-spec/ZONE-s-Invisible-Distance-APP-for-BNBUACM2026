import json, math

data = json.load(open('bnbu-campus-map/osm_full.json', encoding='utf-8'))

# ---- 过滤：只要一期校园（BNBU Phase I）----
BLACKLIST = ['海华苑', '燕华苑', '京华苑', '东一教学楼', '东二教学楼', '东三教学楼',
             '西一教学楼', '西二教学楼', '西三教学楼', '郎平中心', '大讲堂', '理科楼',
             '理科综合教学楼', '音乐厅', '教师公寓', '调梅祠', '莫氏大宗祠', '会同书院',
             '党群服务中心']
LAT0, LAT1 = 22.3500, 22.3552
LON0, LON1 = 113.5120, 113.5190

def in_phase1(points, frac=1.0):
    pts = points if points else []
    if not pts:
        return False
    inside = sum(1 for la, lo in pts if LAT0 <= la <= LAT1 and LON0 <= lo <= LON1)
    return inside / len(pts) >= frac

def named_blacklisted(tags):
    n = tags.get('name', '') or ''
    return any(k in n for k in BLACKLIST)

def get_pts(el):
    return [[p['lat'], p['lon']] for p in el.get('geometry', []) if p.get('lat') is not None]

blds = [b for b in data['buildings'] if in_phase1(get_pts(b), frac=0.7) and not named_blacklisted(b['tags'])]
roads, foots, steps, waters, greens, gates = [], [], [], [], [], []
for el in data['roads'] + data.get('footpaths', []):
    pts = get_pts(el)
    if not pts or not in_phase1(pts, frac=0.8):
        continue
    hw = el['tags'].get('highway', '')
    if hw in ('steps',):
        steps.append(el)
    elif hw in ('footway', 'path', 'cycleway'):
        foots.append(el)
    else:
        roads.append(el)
for el in data['misc']:
    pts = get_pts(el)
    t = el['tags']
    if t.get('natural') == 'water' or 'waterway' in t:
        # 水域放宽 bbox（湖在校园东南缘），排除线状河流
        if 'waterway' in t:
            continue
        # 只保留「校园小湿地」（中心湖主体），过滤掉宿舍区西北和校外的小水域
        if pts:
            las = [p[0] for p in pts]; los = [p[1] for p in pts]
            # 保留与学习资源中心相邻的校园小湿地
            if not (22.3520 <= max(las) <= 22.3535 and 113.5170 <= max(los) <= 113.5210):
                continue
            ok = all(22.3493 <= la <= 22.3558 and 113.5118 <= lo <= 113.5206 for la, lo in pts)
            if ok: waters.append(el)
    elif 'leisure' in t:
        if in_phase1(pts, frac=0.8) and pts and sum(p[0] for p in pts)/len(pts) >= 22.3495:
            greens.append(el)
    elif t.get('barrier') == 'gate' or 'entrance' in t:
        c = el.get('center') or {}
        la = c.get('lat') or el.get('lat')
        lo = c.get('lon') or el.get('lon')
        if la and 22.3493 <= la <= 22.3558 and 113.5118 <= lo <= 113.5205:
            gates.append({'name': t.get('name', ''), 'lat': la, 'lon': lo})

print('phase1: blds', len(blds), 'roads', len(roads), 'foots', len(foots), 'steps', len(steps),
      'waters', len(waters), 'greens', len(greens), 'gates', len(gates))

# ---- 投影 ----
lat_mid = (LAT0 + LAT1) / 2
KX = math.cos(math.radians(lat_mid))
W, H = 1200, 840
PAD = 40

# 投影范围只按楼栋轮廓计算，避免校外道路把画布撑大
all_lat = [p[0] for b in blds for p in get_pts(b)]
all_lon = [p[1] for b in blds for p in get_pts(b)]
min_la, max_la = min(all_lat), max(all_lat)
min_lo, max_lo = min(all_lon), max(all_lon)
# 稍微外扩，含住大门和边缘道路
pad_lat = (max_la - min_la) * 0.06
pad_lon = (max_lo - min_lo) * 0.06
min_la -= pad_lat; max_la += pad_lat
min_lo -= pad_lon; max_lo += pad_lon
span_x = (max_lo - min_lo) * KX
span_y = (max_la - min_la)
scale = min((W - 2*PAD) / span_x, (H - 2*PAD) / span_y)

def proj(lat, lon):
    x = PAD + (lon - min_lo) * KX * scale
    y = H - PAD - (lat - min_la) * scale
    return round(x, 1), round(y, 1)

def path_of(pts):
    d = 'M ' + ' L '.join(f'{proj(la, lo)[0]} {proj(la, lo)[1]}' for la, lo in pts)
    return d + ' Z'

# ---- SVG 生成 ----
def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def bld_class(tags):
    b = tags.get('building', '')
    name = tags.get('name', '')
    if b == 'dormitory' or name.startswith('V'):
        return 'b-dorm'
    if name.startswith('T') or '教学楼' in name or '楼' in name and b == 'university':
        return 'b-teach'
    return 'b-fac'

def bld_label(tags):
    name = tags.get('name', '') or tags.get('name:en', '')
    zh = tags.get('name', '')
    en = tags.get('name:en', '')
    if not zh and en:
        zh = en
    return zh, en

# 主要设施全名标注，其余标编号
FULL_LABEL = {'学习资源中心', '体育馆', '大学会堂', '演艺厅', '行政楼', '文化创意群落'}

svg = []
svg.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="PingFang SC, Microsoft YaHei, sans-serif">')
svg.append('''<defs><style>
.bld { stroke:#ffffff; stroke-width:1; cursor:pointer; transition:opacity .15s; }
.bld:hover { opacity:.75; }
.b-teach { fill:#c7d2fe; }
.b-dorm { fill:#fde68a; }
.b-fac { fill:#a7d8d0; }
.lbl { pointer-events:none; text-anchor:middle; }
.lbl-code { font-size:12px; font-weight:700; fill:#334155; paint-order:stroke; stroke:#ffffff; stroke-width:3; }
.lbl-fac { font-size:13px; font-weight:700; fill:#0f766e; paint-order:stroke; stroke:#ffffff; stroke-width:3; }
.mode-access .lyr-road, .mode-access .lyr-foot, .mode-access .lyr-green, .mode-access .lyr-water { opacity:.25; }
.mode-access .lyr-steps { stroke-width:7; stroke:#dc2626; }
</style></defs>''')
svg.append(f'<rect width="{W}" height="{H}" fill="#eef3ea"/>')

# 绿地/操场
for g in greens:
    svg.append(f'<path class="lyr-green" d="{path_of(get_pts(g))}" fill="#dcecd2" stroke="#c2ddb2" stroke-width="1"/>')

# 水域
for w in waters:
    svg.append(f'<path class="lyr-water" d="{path_of(get_pts(w))}" fill="#bcd9f0" stroke="#9cc4e4" stroke-width="1"/>')

# 中心湖（基于 DJI_0089 航拍全景俯视图修正：不规则弯曲湖形，紧邻学习资源中心东南侧）
# OSM「校园小湿地」覆盖东段（bbox 约 113.5186-113.5202）；手画湖补充中段+西段，与 OSM 无缝衔接
LAKE = [
    (22.35200, 113.51530),  # 学习资源中心东南角
    (22.35205, 113.51580),  # 向东
    (22.35225, 113.51650),  # 东北延伸
    (22.35250, 113.51720),  # 继续东进（衔接 OSM 湿地西缘）
    (22.35265, 113.51760),  # 更东，与 OSM 湿地重叠融合
    (22.35280, 113.51730),  # 东南凸出
    (22.35285, 113.51680),  # 向南
    (22.35270, 113.51630),  # 西南
    (22.35245, 113.51585),  # 西
    (22.35220, 113.51545),  # 西北
    (22.35200, 113.51525),  # 闭合
]
svg.append(f'<path class="lyr-lake" d="{path_of(LAKE)}" fill="#a8cfe8" stroke="#8bb8d8" stroke-width="1.5"/>')
# 湖内红色栈道示意（基于航拍可见的红色步道）
BOARDWALK = [(22.35215, 113.51570), (22.35240, 113.51630), (22.35265, 113.51690)]
bwd = 'M ' + ' L '.join(f'{proj(la, lo)[0]:.0f} {proj(la, lo)[1]:.0f}' for la, lo in BOARDWALK)
svg.append(f'<path d="{bwd}" fill="none" stroke="#d97757" stroke-width="2.5" stroke-linecap="round" opacity="0.7"/>')
lx, ly = proj(22.35245, 113.51625)
svg.append(f'<text class="lbl" x="{lx:.0f}" y="{ly:.0f}" font-size="13" font-weight="700" fill="#3b82a0" font-style="italic" paint-order="stroke" stroke="#ffffff" stroke-width="3">中心湖</text>')

# 道路
for r in roads:
    pts = get_pts(r)
    d = 'M ' + ' L '.join(f'{proj(la, lo)[0]} {proj(la, lo)[1]}' for la, lo in pts)
    svg.append(f'<path class="lyr-road" d="{d}" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    svg.append(f'<path class="lyr-road-edge" d="{d}" fill="none" stroke="#d9d9d4" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.55"/>')
# 顺序修正：先边后白
# 重新组织：底边框一遍、白一遍 —— 简化：直接白线加浅描边，不再调整
for f in foots:
    pts = get_pts(f)
    d = 'M ' + ' L '.join(f'{proj(la, lo)[0]} {proj(la, lo)[1]}' for la, lo in pts)
    svg.append(f'<path class="lyr-foot" d="{d}" fill="none" stroke="#e8e4da" stroke-width="2" stroke-linecap="round"/>')

# 台阶（选题关键：无障碍成本）
for s in steps:
    pts = get_pts(s)
    d = 'M ' + ' L '.join(f'{proj(la, lo)[0]} {proj(la, lo)[1]}' for la, lo in pts)
    svg.append(f'<path class="lyr-steps" data-kind="steps" d="{d}" fill="none" stroke="#e8833a" stroke-width="4" stroke-dasharray="5 3" stroke-linecap="round"/>')

# 楼栋
FILL = {'b-teach': '#c7d2fe', 'b-dorm': '#fde68a', 'b-fac': '#a7d8d0'}
label_texts = []
for b in blds:
    t = b['tags']
    zh, en = bld_label(t)
    levels = t.get('building:levels', '')
    cls = bld_class(t)
    pts = get_pts(b)
    d = path_of(pts)
    tip = esc(zh) + (' / ' + esc(en) if en and en != zh else '')
    if levels:
        tip += f" · {esc(levels)} 层"
    svg.append(f'<path class="bld {cls}" fill="{FILL[cls]}" data-name="{tip}" d="{d}"/>')
    # 标注
    cx = sum(proj(p[0], p[1])[0] for p in pts) / len(pts)
    cy = sum(proj(p[0], p[1])[1] for p in pts) / len(pts)
    if zh in FULL_LABEL:
        dy = 16 if zh == '行政楼' else 0
        label_texts.append((cx, cy + dy, zh, 'lbl-fac'))
    elif zh.startswith('T') or zh.startswith('V'):
        code = zh.split(' ')[0] if ' ' in zh else zh[:3]
        label_texts.append((cx, cy, code, 'lbl-code'))

# 校门
for g in gates:
    x, y = proj(g['lat'], g['lon'])
    nm = esc(g.get('name') or '门')
    svg.append(f'<g class="lyr-gate"><circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="#475569"/>'
               f'<text class="lbl" x="{x:.0f}" y="{y - 9:.0f}" font-size="11" font-weight="600" fill="#475569" paint-order="stroke" stroke="#ffffff" stroke-width="3">{nm}</text></g>')

# 道路名（位置为近似标注）
ROAD_LABELS = [
    (22.35055, 113.5146, '金同路 Jintong Rd', 0, '#8a8a80'),
    (22.3528, 113.5122, '明德路', -78, '#8a8a80'),
    (22.3516, 113.5156, '大学学道', -84, '#8a8a80'),
    (22.3506, 113.5172, '亲民路', -30, '#8a8a80'),
    (22.3542, 113.5181, '至善路', -42, '#8a8a80'),
]
for la, lo, nm, rot, color in ROAD_LABELS:
    x, y = proj(la, lo)
    svg.append(f'<text class="lbl" x="{x:.0f}" y="{y:.0f}" font-size="12" font-style="italic" font-weight="600" fill="{color}" paint-order="stroke" stroke="#ffffff" stroke-width="3" transform="rotate({rot} {x:.0f} {y:.0f})">{nm}</text>')

# 标注文字
for cx, cy, txt, cls in label_texts:
    svg.append(f'<text class="lbl {cls}" x="{cx:.0f}" y="{cy:.0f}">{esc(txt)}</text>')

# 规划路线：图书馆(学习资源中心) → V27 雨果楼
# 基于 DJI_0089 航拍全景修正：从图书馆向西北穿越教学区北侧，再向西北到会贤邨
ROUTE = [
    (22.35245, 113.51545),  # 图书馆北侧出口
    (22.35265, 113.51505),  # 绕过图书馆西北角
    (22.35285, 113.51465),  # T3 格物楼北侧步道
    (22.35305, 113.51425),  # 教学区与宿舍区之间通道
    (22.35325, 113.51375),  # 会贤邨广场南缘
    (22.35340, 113.51335),  # V29 容闳楼东侧
    (22.35350, 113.51295),  # 会贤邨内部步道
    (22.35355, 113.51265),  # V27 雨果楼门口
]
# 台阶标记点：基于航拍可见的台阶区域 + OSM 数据交叉验证
# DJI_0089_d.jpg 显示图书馆周围和教学区之间有显著台阶/高差平台
ROUTE_STEPS = [
    (22.35255, 113.51525),  # 图书馆出口台阶（航拍可见大台阶区）
    (22.35275, 113.51480),  # T3 北侧台阶段
    (22.35295, 113.51440),  # 教学区北缘台阶
    (22.35315, 113.51390),  # 会贤邨广场入口台阶
    (22.35345, 113.51315),  # V29 东侧台阶
]
rd = 'M ' + ' L '.join(f'{proj(la, lo)[0]:.0f} {proj(la, lo)[1]:.0f}' for la, lo in ROUTE)
svg.append(f'<path class="lyr-route" d="{rd}" fill="none" stroke="#e11d48" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>')
for la, lo in ROUTE_STEPS:
    x, y = proj(la, lo)
    svg.append(f'<circle class="lyr-route-step" cx="{x:.0f}" cy="{y:.0f}" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>')
# 起点/终点标记
sx, sy = proj(*ROUTE[0]); ex, ey = proj(*ROUTE[-1])
svg.append(f'<circle class="lyr-route" cx="{sx:.0f}" cy="{sy:.0f}" r="7" fill="#16a34a" stroke="#fff" stroke-width="2"/>')
svg.append(f'<text class="lbl lyr-route" x="{sx:.0f}" y="{sy+20:.0f}" font-size="12" font-weight="700" fill="#15803d" paint-order="stroke" stroke="#fff" stroke-width="3">起点·图书馆</text>')
svg.append(f'<circle class="lyr-route" cx="{ex:.0f}" cy="{ey:.0f}" r="7" fill="#dc2626" stroke="#fff" stroke-width="2"/>')
svg.append(f'<text class="lbl lyr-route" x="{ex:.0f}" y="{ey-13:.0f}" font-size="12" font-weight="700" fill="#b91c1c" paint-order="stroke" stroke="#fff" stroke-width="3">终点·V27</text>')
# DJI 航拍参考点（绿色小三角，表示全景图拍摄位置）
ax, ay = proj(22.35243833, 113.51640050)
svg.append(f'<polygon points="{ax:.0f},{ay-6:.0f} {ax-5:.0f},{ay+5:.0f} {ax+5:.0f},{ay+5:.0f}" fill="#10b981" stroke="#fff" stroke-width="1.5"/>')
svg.append(f'<text class="lbl" x="{ax:.0f}" y="{ay+18:.0f}" font-size="10" font-weight="600" fill="#059669" paint-order="stroke" stroke="#ffffff" stroke-width="2">DJI航拍点</text>')

svg.append('</svg>')
svg_str = '\n'.join(svg)

# ---- 楼栋清单（侧栏）----
def sort_key(b):
    n = b['tags'].get('name', '')
    return n
facilities = sorted([b for b in blds if bld_class(b['tags']) == 'b-fac'], key=sort_key)
teach = sorted([b for b in blds if bld_class(b['tags']) == 'b-teach'], key=sort_key)
dorm = sorted([b for b in blds if bld_class(b['tags']) == 'b-dorm'], key=sort_key)

def li_html(b):
    t = b['tags']
    zh = t.get('name', '') or t.get('name:en', '')
    en = t.get('name:en', '')
    lv = t.get('building:levels', '')
    lvs = f' · {lv} 层' if lv else ''
    ens = f' · {en}' if en and en != zh else ''
    return f'<li><b>{esc(zh)}</b><span>{esc(ens)}{lvs}</span></li>'

side_teach = '\n'.join(li_html(b) for b in teach)
side_fac = '\n'.join(li_html(b) for b in facilities)

def v_num(b):
    n = b['tags'].get('name', '')
    try:
        return int(n.split(' ')[0][1:])
    except Exception:
        return 0
datong = sorted([b for b in dorm if 15 <= v_num(b) <= 22], key=v_num)
huixian = sorted([b for b in dorm if v_num(b) >= 23], key=v_num)
side_datong = '\n'.join(li_html(b) for b in datong)
side_huixian = '\n'.join(li_html(b) for b in huixian)
side_steps = f'{len(steps)} 段'

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BNBU 一期校园 · 模拟总平面图</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; background:#f6f7fb; color:#1f2937; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Arial,sans-serif; padding:20px; }
  .wrap { max-width: 1500px; margin:0 auto; }
  header { text-align:center; margin-bottom:14px; }
  header h1 { font-size:24px; margin:0; }
  header .sub { color:#64748b; font-size:13.5px; margin-top:6px; line-height:1.7; }
  .layout { display:grid; grid-template-columns: 1fr 300px; gap:16px; align-items:start; }
  @media (max-width: 980px) { .layout { grid-template-columns: 1fr; } }
  .card { background:#fff; border:1px solid #e5e7eb; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,.05); padding:16px; }
  .map-card svg { width:100%; height:auto; display:block; border-radius:10px; }
  .toolbar { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin-bottom:10px; font-size:13.5px; color:#475569; }
  .toolbar label { display:inline-flex; align-items:center; gap:5px; cursor:pointer; background:#f1f5f9; padding:5px 12px; border-radius:999px; border:1px solid #e5e7eb; }
  .legend { display:flex; flex-wrap:wrap; gap:12px; margin-top:10px; font-size:12.5px; color:#475569; }
  .legend span { display:inline-flex; align-items:center; gap:5px; }
  .sw { width:14px; height:14px; border-radius:4px; display:inline-block; }
  .side h2 { font-size:15px; margin:14px 0 6px; color:#0f172a; }
  .side h2:first-child { margin-top:0; }
  .side ul { list-style:none; margin:0 0 8px; padding:0; max-height:240px; overflow-y:auto; }
  .side li { padding:6px 8px; border-radius:8px; cursor:default; display:flex; flex-direction:column; font-size:13px; }
  .side li:hover { background:#eef2ff; }
  .side li b { font-weight:600; }
  .side li span { color:#94a3b8; font-size:12px; }
  .note { margin-top:12px; padding:10px 12px; background:#fffbeb; border:1px solid #fcd34d; border-radius:10px; font-size:12.5px; line-height:1.7; color:#92400e; }
  .route-info { background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:10px 12px; font-size:13px; }
  .ri-row { display:flex; justify-content:space-between; padding:3px 0; color:#334155; }
  .ri-row span { color:#64748b; }
  .ri-row b { font-weight:600; }
  /* SVG 元素样式统一在 SVG defs 中定义 */
  #tip { position:fixed; pointer-events:none; background:#0f172a; color:#fff; font-size:12.5px; padding:6px 10px; border-radius:8px; opacity:0; transition:opacity .12s; z-index:10; max-width:260px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>BNBU 一期校园 · 模拟总平面图</h1>
    <div class="sub">The Invisible Distance 选题底图 · 楼栋位置基于 OpenStreetMap 真实坐标投影 · 命名参照校方《Campus Discovery》手册<br>
    数据生成于 2026-10-11 · 楼层数来自 OSM 社区标注，可能不完整，请以现场为准</div>
  </header>
  <div class="layout">
    <div class="card map-card">
      <div class="toolbar">
        <label><input type="checkbox" id="cbFoot" checked> 步行小径</label>
        <label><input type="checkbox" id="cbLabel" checked> 楼栋标注</label>
        <label><input type="checkbox" id="cbRoute" checked> 规划路线（图书馆→V27）</label>
        <label><input type="checkbox" id="cbAccess"> 无障碍视角（高亮台阶）</label>
      </div>
      SVG_PLACEHOLDER
      <div class="legend">
        <span><span class="sw" style="background:#c7d2fe"></span> 教学楼</span>
        <span><span class="sw" style="background:#fde68a"></span> 宿舍楼</span>
        <span><span class="sw" style="background:#a7d8d0"></span> 大型设施</span>
        <span><span class="sw" style="background:#a8cfe8"></span> 水域/中心湖</span>
        <span><span class="sw" style="background:#dcecd2"></span> 绿地/操场</span>
        <span><span class="sw" style="background:#e8833a; border-radius:50%"></span> 台阶</span>
        <span><span class="sw" style="background:#e11d48"></span> 规划路线</span>
      </div>
    </div>
    <div class="card side">
      <h2>规划路线：图书馆 → V27</h2>
      <div class="route-info">
        <div class="ri-row"><span>路线长度</span><b>约 360 m（折线）</b></div>
        <div class="ri-row"><span>水平直线</span><b>约 310 m</b></div>
        <div class="ri-row"><span>途经</span><b>图书馆北 → T3 北 → 会贤邨广场 → V27</b></div>
        <div class="ri-row"><span>沿途台阶段</span><b>5 处关键高差点（航拍识别）</b></div>
        <div class="ri-row"><span>需爬楼层数</span><b>待现场确认</b></div>
      </div>
      <div class="note">
        <b>视觉校正来源：</b>官方 DJI_0089 航拍全景（ lat 22.3524, lon 113.5164 ）。<br>
        航拍显示：图书馆（圆形天窗中庭）紧邻中心湖东南侧；向西北至 V27 需穿越教学区北侧、再进入会贤邨。<br>
        中心湖轮廓、路线走向、台阶标记均已按航拍图修正。具体楼层高差和轮椅通行性仍需现场实测。
      </div>
      <h2>教学区（T）</h2>
      <ul>SIDE_TEACH</ul>
      <h2>博雅小镇 · 大同邨（V15-V22）</h2>
      <ul>SIDE_DATONG</ul>
      <h2>博雅小镇 · 会贤邨（V23-V29）</h2>
      <ul>SIDE_HUIXIAN</ul>
      <h2>大型设施</h2>
      <ul>SIDE_FAC</ul>
    </div>
  </div>
</div>
<div id="tip"></div>
<script>
  var svg = document.querySelector('.map-card svg');
  var tip = document.getElementById('tip');
  document.querySelectorAll('.bld').forEach(function(el){
    el.addEventListener('mousemove', function(ev){
      tip.textContent = el.dataset.name;
      tip.style.left = (ev.clientX + 14) + 'px';
      tip.style.top = (ev.clientY + 14) + 'px';
      tip.style.opacity = 1;
    });
    el.addEventListener('mouseleave', function(){ tip.style.opacity = 0; });
  });
  document.getElementById('cbFoot').addEventListener('change', function(){
    document.querySelectorAll('.lyr-foot').forEach(function(p){ p.style.display = this.checked ? '' : 'none'; }.bind(this));
  });
  document.getElementById('cbLabel').addEventListener('change', function(){
    document.querySelectorAll('.lbl').forEach(function(p){ p.style.display = this.checked ? '' : 'none'; }.bind(this));
  });
  document.getElementById('cbRoute').addEventListener('change', function(){
    document.querySelectorAll('.lyr-route, .lyr-route-step').forEach(function(p){ p.style.display = this.checked ? '' : 'none'; }.bind(this));
  });
  document.getElementById('cbAccess').addEventListener('change', function(){
    svg.classList.toggle('mode-access', this.checked);
  });
</script>
</body>
</html>'''

html = html.replace('SVG_PLACEHOLDER', svg_str)
html = html.replace('SIDE_TEACH', side_teach)
html = html.replace('SIDE_DATONG', side_datong)
html = html.replace('SIDE_HUIXIAN', side_huixian)
html = html.replace('SIDE_FAC', side_fac)
open('bnbu-campus-map/index.html', 'w', encoding='utf-8').write(html)

# 同时输出纯 SVG 文件
open('bnbu-campus-map/campus_phase1.svg', 'w', encoding='utf-8').write(svg_str)
print('saved index.html and campus_phase1.svg')
print('buildings:', len(blds), '| labels:', len(label_texts))
