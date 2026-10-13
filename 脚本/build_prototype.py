import re

# 读取 SVG 核心内容
svg_core = open('bnbu-campus-map/svg_core.txt', encoding='utf-8').read()

# 替换路线部分：把单一路线改为双路线
old_route_block = '''<path class="lyr-route" d="M 542 474 L 484 443 L 428 412 L 370 381 L 299 350 L 242 327 L 185 312 L 142 304" fill="none" stroke="#e11d48" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
<circle class="lyr-route-step" cx="513" cy="458" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
<circle class="lyr-route-step" cx="449" cy="428" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
<circle class="lyr-route-step" cx="392" cy="397" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
<circle class="lyr-route-step" cx="321" cy="366" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
<circle class="lyr-route-step" cx="214" cy="320" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
<circle class="lyr-route" cx="542" cy="474" r="7" fill="#16a34a" stroke="#fff" stroke-width="2"/>
<text class="lbl lyr-route" x="542" y="494" font-size="12" font-weight="700" fill="#15803d" paint-order="stroke" stroke="#fff" stroke-width="3">起点·图书馆</text>
<circle class="lyr-route" cx="142" cy="304" r="7" fill="#dc2626" stroke="#fff" stroke-width="2"/>
<text class="lbl lyr-route" x="142" y="291" font-size="12" font-weight="700" fill="#b91c1c" paint-order="stroke" stroke="#fff" stroke-width="3">终点·V27</text>'''

new_route_block = '''<!-- 路线 A：台阶近路（下坡 -1 层，距离短） -->
<path class="lyr-route route-A" d="M 560 520 L 530 490 L 490 450 L 440 420 L 380 390 L 320 360 L 260 340 L 200 325 L 145 311" fill="none" stroke="#2563eb" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
<!-- 路线 B：绕行平路（无台阶，距离长） -->
<path class="lyr-route route-B" d="M 560 520 L 530 560 L 490 600 L 450 630 L 420 600 L 380 560 L 340 520 L 300 480 L 260 440 L 220 400 L 180 360 L 145 311" fill="none" stroke="#16a34a" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.35"/>
<!-- 路线 A 台阶点 -->
<circle class="lyr-route-step" cx="490" cy="450" r="6" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/>
<text class="lbl" x="505" y="445" font-size="11" font-weight="700" fill="#b45309">台阶 -1层</text>
<!-- 路线 B 便利点 -->
<circle class="lyr-route-step" cx="450" cy="630" r="6" fill="#16a34a" stroke="#fff" stroke-width="1.5"/>
<text class="lbl" x="465" y="645" font-size="11" font-weight="700" fill="#15803d">体育馆平路</text>
<circle class="lyr-route-step" cx="300" cy="480" r="6" fill="#16a34a" stroke="#fff" stroke-width="1.5"/>
<text class="lbl" x="315" y="470" font-size="11" font-weight="700" fill="#15803d">V28连廊</text>
<!-- 起点终点 -->
<circle class="lyr-route" cx="560" cy="520" r="8" fill="#16a34a" stroke="#fff" stroke-width="2.5"/>
<text class="lbl" x="560" y="545" font-size="13" font-weight="700" fill="#15803d" paint-order="stroke" stroke="#fff" stroke-width="3">起·图书馆 2F出口</text>
<circle class="lyr-route" cx="145" cy="311" r="8" fill="#dc2626" stroke="#fff" stroke-width="2.5"/>
<text class="lbl" x="145" y="295" font-size="13" font-weight="700" fill="#b91c1c" paint-order="stroke" stroke="#fff" stroke-width="3">终·V27 1F入口</text>'''

svg_core = svg_core.replace(old_route_block, new_route_block)

# 给 SVG 添加一个 id 以便 JS 操作
svg_core = svg_core.replace('<svg viewBox="0 0 1200 840" xmlns="http://www.w3.org/2000/svg" font-family="PingFang SC, Microsoft YaHei, sans-serif">',
                           '<svg id="campusMap" viewBox="0 0 1200 840" xmlns="http://www.w3.org/2000/svg" font-family="PingFang SC, Microsoft YaHei, sans-serif">')

# 给图书馆和 V27 的 path 添加 id 以便楼层高亮
svg_core = svg_core.replace(
    'data-name="学习资源中心 / Learning Resource Center · 1 层"',
    'id="bld-library" data-name="学习资源中心 / Learning Resource Center · 4层（用户核实：唯一出入口在2层朝湖）"'
)
svg_core = svg_core.replace(
    'data-name="V27 雨果楼 / V27 Hugo House · 7 层"',
    'id="bld-v27" data-name="V27 雨果楼 / V27 Hugo House · 7层（用户核实：入口无台阶·有电梯）"'
)

# 添加楼层高亮用的 class
svg_core = svg_core.replace(
    '<style>',
    '<style>\n.floor-active #bld-library { stroke:#2563eb; stroke-width:3; filter:drop-shadow(0 0 6px rgba(37,99,235,.4)); }\n.floor-active #bld-v27 { stroke:#16a34a; stroke-width:3; filter:drop-shadow(0 0 6px rgba(22,163,74,.4)); }\n'
)

# 修正图书馆楼层数显示（OSM 标 1 层是错的，用户核实为 4 层）
svg_core = svg_core.replace('学习资源中心 / Learning Resource Center · 1 层', '学习资源中心 / Learning Resource Center · 4 层')
svg_core = svg_core.replace('data-name="学习资源中心 / Learning Resource Center · 4 层"', 'data-name="学习资源中心 / Learning Resource Center · 4层（唯一出入口在2层朝湖）"')

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>看不见的距离 · 图书馆 → V27 真实校园地图版</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; min-height: 100vh; background: #f6f7fb; color: #1f2937;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
    padding: 20px;
  }}
  .wrap {{ max-width: 1500px; margin: 0 auto; }}
  header {{ text-align: center; margin-bottom: 14px; }}
  header h1 {{ font-size: 24px; font-weight: 700; margin: 0; }}
  header .sub {{ color: #64748b; font-size: 13.5px; margin-top: 6px; line-height: 1.7; }}

  .control-bar {{
    display: flex; flex-wrap: wrap; justify-content: center; align-items: center;
    gap: 14px; margin-bottom: 16px;
  }}
  .switch-row {{ display: flex; gap: 10px; }}
  .switch-row button {{
    border: 1px solid #e5e7eb; background: #fff; color: #475569;
    font: inherit; font-size: 14px; font-weight: 600;
    padding: 8px 18px; border-radius: 999px; cursor: pointer; transition: all .15s ease;
  }}
  .switch-row button:hover {{ border-color: #2563eb; color: #2563eb; }}
  .switch-row button.active {{ background: #2563eb; border-color: #2563eb; color: #fff; }}

  .floor-selector {{
    display: flex; align-items: center; gap: 8px;
    background: #fff; border: 1px solid #e5e7eb; border-radius: 999px;
    padding: 6px 14px; font-size: 13.5px;
  }}
  .floor-selector label {{ color: #64748b; font-weight: 600; }}
  .floor-selector select {{
    border: none; background: transparent; font: inherit; font-size: 13.5px;
    color: #334155; cursor: pointer; outline: none; min-width: 180px;
  }}

  .layout {{ display: grid; grid-template-columns: 1fr 340px; gap: 16px; align-items: start; }}
  @media (max-width: 980px) {{ .layout {{ grid-template-columns: 1fr; }} }}

  .card {{
    background: #fff; border: 1px solid #e5e7eb; border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,.05); padding: 16px;
  }}
  .map-panel svg {{ width: 100%; height: auto; display: block; border-radius: 10px; }}
  .map-toolbar {{
    display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
    margin-bottom: 10px; font-size: 13px; color: #475569;
  }}
  .map-toolbar label {{
    display: inline-flex; align-items: center; gap: 5px; cursor: pointer;
    background: #f1f5f9; padding: 5px 12px; border-radius: 999px; border: 1px solid #e5e7eb;
  }}

  .side-panel {{ display: flex; flex-direction: column; gap: 14px; }}
  .side-panel h2 {{ margin: 0 0 8px; font-size: 15px; }}
  .side-panel .hint {{ color: #94a3b8; font-size: 12.5px; margin-bottom: 10px; }}

  .floor-info {{ margin-bottom: 10px; }}
  .floor-title {{ font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 6px; }}
  .floor-meta {{ font-size: 12.5px; color: #64748b; margin-bottom: 10px; line-height: 1.6; }}
  .floor-status {{
    display: inline-block; font-size: 12px; font-weight: 700;
    padding: 4px 12px; border-radius: 999px; margin-bottom: 10px;
  }}
  .status-ok {{ background: #dcfce7; color: #166534; }}
  .status-warn {{ background: #fef9c3; color: #854d0e; }}
  .status-danger {{ background: #fee2e2; color: #991b1b; }}
  .status-info {{ background: #dbeafe; color: #1e40af; }}

  .badge {{
    display: inline-block; font-size: 12px; font-weight: 700; color: #fff;
    border-radius: 999px; padding: 3px 12px; margin-bottom: 10px;
  }}
  .badge.rec-a {{ background: #2563eb; }}
  .badge.rec-b {{ background: #16a34a; }}
  .badge.warn {{ background: #f59e0b; }}
  .badge.danger {{ background: #dc2626; }}

  .note {{
    background: #f1f5fe; border-left: 3px solid #2563eb; border-radius: 0 10px 10px 0;
    padding: 10px 12px; font-size: 13px; line-height: 1.7; color: #1e3a8a; margin-bottom: 12px;
  }}
  .note.warn {{ background: #fffbeb; border-left-color: #f59e0b; color: #92400e; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ padding: 7px 8px; border-bottom: 1px solid #eef2f7; text-align: center; }}
  th:first-child, td:first-child {{ text-align: left; color: #475569; font-weight: 600; }}
  th {{ background: #f8fafc; color: #64748b; font-weight: 600; font-size: 12px; }}
  tr.win td {{ background: #f0fdf4; }}
  tr.lose td {{ background: #fef2f2; }}
  .rec-mark {{ color: #16a34a; font-weight: 700; }}
  .risk-mark {{ color: #dc2626; font-weight: 700; }}

  .bars {{ margin-top: 14px; }}
  .bar-group {{ margin-bottom: 12px; }}
  .bar-title {{ font-size: 12px; color: #64748b; margin-bottom: 4px; font-weight: 600; }}
  .bar-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }}
  .bar-name {{ width: 65px; font-size: 11.5px; color: #475569; text-align: right; }}
  .bar-track {{ flex: 1; background: #f1f5f9; border-radius: 6px; height: 13px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 6px; transition: width .3s ease; }}
  .bar-fill.A {{ background: #60a5fa; }}
  .bar-fill.B {{ background: #4ade80; }}
  .bar-val {{ width: 50px; font-size: 11.5px; color: #334155; }}

  .legend {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; font-size: 12px; color: #475569; }}
  .legend span {{ display: inline-flex; align-items: center; gap: 5px; }}
  .dot {{ width: 11px; height: 11px; border-radius: 50%; display: inline-block; }}

  .source {{ margin-top: 10px; font-size: 11.5px; color: #94a3b8; line-height: 1.6; }}

  footer {{ text-align: center; color: #94a3b8; font-size: 12px; margin-top: 16px; line-height: 1.7; }}

  /* SVG 内路线交互 */
  .route-A {{ opacity: 0.85; }}
  .route-B {{ opacity: 0.35; }}
  .view-walker .route-A {{ opacity: 0.9; stroke-width: 5.5; }}
  .view-walker .route-B {{ opacity: 0.3; }}
  .view-luggage .route-A {{ opacity: 0.3; }}
  .view-luggage .route-B {{ opacity: 0.9; stroke-width: 5.5; }}
  .view-wheelchair .route-A {{ opacity: 0.15; stroke-dasharray: 8 4; }}
  .view-wheelchair .route-B {{ opacity: 0.9; stroke-width: 5.5; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>看不见的距离 · 图书馆 → V27 真实校园地图版</h1>
    <div class="sub">The Invisible Distance —— 同一段路，三种人生，三种「最近」<br>
    底图基于 OpenStreetMap 真实坐标投影 · 路线基于现场核实 · 楼层信息基于用户实测</div>
  </header>

  <div class="control-bar">
    <div class="switch-row">
      <button data-view="walker" class="active">普通行人</button>
      <button data-view="luggage">拖行李</button>
      <button data-view="wheelchair">轮椅 / 无障碍</button>
    </div>
    <div class="floor-selector">
      <label for="floorSelect">当前楼层：</label>
      <select id="floorSelect">
        <optgroup label="户外">
          <option value="ground" selected>地面层</option>
        </optgroup>
        <optgroup label="图书馆（学习资源中心）">
          <option value="lib-1">1F · 无出入口（需上楼）</option>
          <option value="lib-2">2F · 唯一出入口（朝湖·无台阶）</option>
          <option value="lib-3">3F · 需电梯下至 2F</option>
          <option value="lib-4">4F · 需电梯下至 2F</option>
        </optgroup>
        <optgroup label="V27 雨果楼">
          <option value="v27-1">1F · 入口（无台阶·有电梯）</option>
          <option value="v27-2">2F · 需电梯下至 1F</option>
          <option value="v27-3">3F · 需电梯下至 1F</option>
          <option value="v27-4">4F · 需电梯下至 1F</option>
          <option value="v27-5">5F · 需电梯下至 1F</option>
          <option value="v27-6">6F · 需电梯下至 1F</option>
          <option value="v27-7">7F · 需电梯下至 1F</option>
        </optgroup>
      </select>
    </div>
  </div>

  <div class="layout">
    <!-- 左侧：真实地图 -->
    <div class="card map-panel">
      <div class="map-toolbar">
        <label><input type="checkbox" id="cbFoot" checked> 步行小径</label>
        <label><input type="checkbox" id="cbLabel" checked> 楼栋标注</label>
        <label><input type="checkbox" id="cbRoute" checked> 路线</label>
        <label><input type="checkbox" id="cbAccess"> 无障碍视角（高亮台阶）</label>
      </div>
      {svg_core}
      <div class="legend">
        <span><span class="dot" style="background:#2563eb"></span> 路线 A（台阶近路）</span>
        <span><span class="dot" style="background:#16a34a"></span> 路线 B（绕行平路）</span>
        <span><span class="dot" style="background:#f59e0b"></span> 台阶成本点</span>
        <span><span class="dot" style="background:#c7d2fe"></span> 教学楼</span>
        <span><span class="dot" style="background:#fde68a"></span> 宿舍楼</span>
        <span><span class="dot" style="background:#a7d8d0"></span> 大型设施</span>
      </div>
      <div class="source">
        <b>数据来源：</b>OpenStreetMap 真实坐标（relation 18704403）+ DJI_0089 航拍全景视觉校正 + 用户现场实测。<br>
        图书馆 4 层（唯一出入口 2F 朝湖）/ V27 7 层（入口无台阶·有电梯）。路线 A 有一段 -1 层台阶下坡，路线 B 经体育馆→V28→V29 全平路绕行。
      </div>
    </div>

    <!-- 右侧：楼层信息 + 路线对比 -->
    <div class="side-panel">
      <!-- 楼层信息面板 -->
      <div class="card floor-info" id="floorCard">
        <h2>楼层状态</h2>
        <div class="hint">选择上方「当前楼层」，查看该层的出入口与可达性。</div>
        <div id="floorContent"></div>
      </div>

      <!-- 路线对比面板 -->
      <div class="card">
        <h2>路线对比</h2>
        <div class="hint">切换上方视角，观察推荐如何反转。</div>
        <div id="recBadge" class="badge rec-a">推荐路线 A</div>
        <div class="note" id="note"></div>

        <table>
          <thead>
            <tr><th>指标</th><th>路线 A</th><th>路线 B</th></tr>
          </thead>
          <tbody id="tbody"></tbody>
        </table>

        <div class="bars">
          <div class="bar-group">
            <div class="bar-title">距离</div>
            <div class="bar-row"><span class="bar-name">路线 A</span><span class="bar-track"><span class="bar-fill A" id="barDistA"></span></span><span class="bar-val" id="valDistA"></span></div>
            <div class="bar-row"><span class="bar-name">路线 B</span><span class="bar-track"><span class="bar-fill B" id="barDistB"></span></span><span class="bar-val" id="valDistB"></span></div>
          </div>
          <div class="bar-group">
            <div class="bar-title">预估时间</div>
            <div class="bar-row"><span class="bar-name">路线 A</span><span class="bar-track"><span class="bar-fill A" id="barTimeA"></span></span><span class="bar-val" id="valTimeA"></span></div>
            <div class="bar-row"><span class="bar-name">路线 B</span><span class="bar-track"><span class="bar-fill B" id="barTimeB"></span></span><span class="bar-val" id="valTimeB"></span></div>
          </div>
          <div class="bar-group">
            <div class="bar-title">楼层高差</div>
            <div class="bar-row"><span class="bar-name">路线 A</span><span class="bar-track"><span class="bar-fill A" id="barFloorA"></span></span><span class="bar-val" id="valFloorA"></span></div>
            <div class="bar-row"><span class="bar-name">路线 B</span><span class="bar-track"><span class="bar-fill B" id="barFloorB"></span></span><span class="bar-val" id="valFloorB"></span></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <footer>
    基于现场核实数据：图书馆 4 层、出入口在 2 层朝湖；V27 入口无台阶有电梯；路线 A 有一段 -1 层台阶下坡；路线 B 经体育馆→V28→V29 全平路绕行。<br>
    核心洞察：对普通行人，最短的路就是最近的路；但对拖行李和轮椅，最短的路反而变成了最远甚至不可达的路。
  </footer>
</div>
<div id="tip" style="position:fixed;pointer-events:none;background:#0f172a;color:#fff;font-size:12px;padding:6px 10px;border-radius:8px;opacity:0;transition:opacity .12s;z-index:10;max-width:260px;"></div>

<script>
  // ===== 楼层数据 =====
  var FLOOR_DATA = {{
    'ground': {{
      title: '户外地面层',
      status: 'status-ok',
      statusText: '可自由通行',
      desc: '地面层视角：所有户外路线均可通行。图书馆 2F 出口和 V27 1F 入口均直接可达。',
      routeNote: '从地面出发，路线选择取决于你的身体条件。'
    }},
    'lib-1': {{
      title: '图书馆 1F',
      status: 'status-warn',
      statusText: '无直接出入口',
      desc: '1F 没有通往户外的出入口。你必须乘坐电梯或走楼梯到 2F，才能从唯一的出口离开建筑。',
      routeNote: '先上楼到 2F，再选择路线 A 或路线 B。'
    }},
    'lib-2': {{
      title: '图书馆 2F · 唯一出入口',
      status: 'status-ok',
      statusText: '唯一出入口·可直接出发',
      desc: '2F 是图书馆唯一有出入口的楼层，出口朝东南（中心湖方向），无台阶。出门后可选路线 A（台阶近路）或路线 B（绕行平路）。',
      routeNote: '这是理想的出发楼层，出门即可选择任意路线。'
    }},
    'lib-3': {{
      title: '图书馆 3F',
      status: 'status-info',
      statusText: '需下至 2F',
      desc: '3F 没有通往户外的出入口。整栋楼有互通电梯，可乘电梯或走楼梯下至 2F，再从 2F 出口离开。',
      routeNote: '先下至 2F，再选择路线。电梯可通全楼层。'
    }},
    'lib-4': {{
      title: '图书馆 4F',
      status: 'status-info',
      statusText: '需下至 2F',
      desc: '4F 没有通往户外的出入口。整栋楼有互通电梯，可乘电梯或走楼梯下至 2F，再从 2F 出口离开。',
      routeNote: '先下至 2F，再选择路线。电梯可通全楼层。'
    }},
    'v27-1': {{
      title: 'V27 1F · 入口层',
      status: 'status-ok',
      statusText: '入口层·可直接到达',
      desc: '1F 是 V27 的入口层，入口位于整栋楼的拐弯处，无台阶。楼内有电梯可通达全楼层（1F–7F）。',
      routeNote: '从户外到达后可直接从 1F 入口进入。'
    }},
    'v27-2': {{
      title: 'V27 2F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '2F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    }},
    'v27-3': {{
      title: 'V27 3F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '3F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    }},
    'v27-4': {{
      title: 'V27 4F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '4F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    }},
    'v27-5': {{
      title: 'V27 5F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '5F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    }},
    'v27-6': {{
      title: 'V27 6F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '6F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    }},
    'v27-7': {{
      title: 'V27 7F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '7F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    }}
  }};

  function renderFloor(floorKey) {{
    var d = FLOOR_DATA[floorKey];
    var html = '<div class="floor-title">' + d.title + '</div>' +
               '<div class="floor-status ' + d.status + '">' + d.statusText + '</div>' +
               '<div class="floor-meta">' + d.desc + '</div>';
    if (d.routeNote) {{
      html += '<div class="note">' + d.routeNote + '</div>';
    }}
    document.getElementById('floorContent').innerHTML = html;

    // 高亮对应建筑
    var svg = document.getElementById('campusMap');
    svg.classList.remove('floor-active');
    if (floorKey.startsWith('lib-')) {{
      svg.classList.add('floor-active');
      setTimeout(function() {{ svg.classList.remove('floor-active'); }}, 2000);
    }} else if (floorKey.startsWith('v27-')) {{
      svg.classList.add('floor-active');
      setTimeout(function() {{ svg.classList.remove('floor-active'); }}, 2000);
    }}
  }}

  document.getElementById('floorSelect').addEventListener('change', function() {{
    renderFloor(this.value);
  }});
  renderFloor('ground');

  // ===== 三视角路线数据 =====
  var VIEWS = {{
    walker: {{
      rec: 'A',
      badgeClass: 'rec-a',
      note: '普通行人下坡走台阶反而省力。路线 A 距离短、有下坡台阶加速，是明显最优选。此时「最短」=「最近」。',
      rows: [
        ['距离', '约 300 m', '约 450 m'],
        ['预估时间', '约 4 分钟', '约 6 分钟'],
        ['台阶/高差', '1 段（下坡 -1 层）', '0 处（全平路）'],
        ['楼层高差', '-1 层（下坡省力）', '0 层'],
        ['拖行李风险', '低（下坡轻）', '无'],
        ['轮椅通行', '否', '是']
      ],
      dist: [300, 450], time: [4, 6], floor: [1, 0]
    }},
    luggage: {{
      rec: 'B',
      badgeClass: 'rec-b',
      note: '拖着 20kg 行李下坡走台阶，箱子容易失控滑跑甚至摔坏。路线 A 的「近」被高风险抵消，路线 B 的平路绕行反而更安全、更省心。',
      rows: [
        ['距离', '约 300 m', '约 450 m'],
        ['预估时间', '约 8 分钟（控箱减速）', '约 6 分钟'],
        ['台阶/高差', '1 段（下坡高风险）', '0 处（全平路）'],
        ['楼层高差', '-1 层（下坡拖箱危险）', '0 层'],
        ['拖行李风险', '高（易失控/摔箱）', '无'],
        ['轮椅通行', '否', '是']
      ],
      dist: [300, 450], time: [8, 6], floor: [1, 0]
    }},
    wheelchair: {{
      rec: 'B',
      badgeClass: 'rec-b',
      note: '对轮椅使用者，路线 A 的台阶让这条路根本走不通——地图上最近的那条线，恰恰是最不可达的那条线。路线 B 是唯一选择。',
      rows: [
        ['距离', '约 300 m', '约 450 m'],
        ['预估时间', '不可达', '约 8 分钟'],
        ['台阶/高差', '1 段（轮椅不可行）', '0 处（全平路）'],
        ['楼层高差', '-1 层（完全阻断）', '0 层'],
        ['拖行李风险', '不适用', '无'],
        ['轮椅通行', '否', '是']
      ],
      dist: [300, 450], time: [0, 8], floor: [1, 0]
    }}
  }};

  function renderView(view) {{
    var v = VIEWS[view];
    var badge = document.getElementById('recBadge');
    badge.className = 'badge ' + v.badgeClass;
    badge.textContent = v.rec === 'A' ? '推荐路线 A（台阶近路）' : '推荐路线 B（绕行平路）';
    document.getElementById('note').textContent = v.note;

    // 地图视角类
    var svg = document.getElementById('campusMap');
    svg.setAttribute('class', 'view-' + view);

    // 表格
    var tbody = document.getElementById('tbody');
    tbody.innerHTML = '';
    v.rows.forEach(function(r) {{
      var tr = document.createElement('tr');
      var recIdx = v.rec === 'A' ? 1 : 2;
      r.forEach(function(cell, i) {{
        var td = document.createElement('td');
        td.textContent = cell;
        if (i === recIdx) td.className = 'rec-mark';
        tr.appendChild(td);
      }});
      if (r[1] === '不可达' || r[2] === '不可达') {{
        tr.className = 'lose';
      }}
      tbody.appendChild(tr);
    }});

    // 条形图
    var maxDist = Math.max(v.dist[0], v.dist[1]);
    var maxTime = Math.max(v.time[0] || 1, v.time[1]);
    var maxFloor = Math.max(v.floor[0], v.floor[1]) || 1;
    setBar('barDistA', 'valDistA', v.dist[0], maxDist, v.dist[0] + 'm');
    setBar('barDistB', 'valDistB', v.dist[1], maxDist, v.dist[1] + 'm');
    setBar('barTimeA', 'valTimeA', v.time[0], maxTime, v.time[0] === 0 ? '不可达' : v.time[0] + '分');
    setBar('barTimeB', 'valTimeB', v.time[1], maxTime, v.time[1] + '分');
    setBar('barFloorA', 'valFloorA', v.floor[0], maxFloor, (v.floor[0] > 0 ? '+' : '') + v.floor[0] + '层');
    setBar('barFloorB', 'valFloorB', v.floor[1], maxFloor, (v.floor[1] > 0 ? '+' : '') + v.floor[1] + '层');
  }}

  function setBar(fillId, valId, val, max, text) {{
    var pct = max > 0 ? Math.max(0, Math.round(val / max * 100)) : 0;
    document.getElementById(fillId).style.width = pct + '%';
    document.getElementById(valId).textContent = text;
  }}

  document.querySelectorAll('.switch-row button').forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      document.querySelectorAll('.switch-row button').forEach(function(b) {{ b.classList.remove('active'); }});
      btn.classList.add('active');
      renderView(btn.dataset.view);
    }});
  }});

  renderView('walker');

  // ===== 地图图层开关（复用真实地图逻辑）=====
  document.getElementById('cbFoot').addEventListener('change', function() {{
    document.querySelectorAll('.lyr-foot').forEach(function(p) {{ p.style.display = this.checked ? '' : 'none'; }}.bind(this));
  }});
  document.getElementById('cbLabel').addEventListener('change', function() {{
    document.querySelectorAll('.lbl').forEach(function(p) {{ p.style.display = this.checked ? '' : 'none'; }}.bind(this));
  }});
  document.getElementById('cbRoute').addEventListener('change', function() {{
    document.querySelectorAll('.lyr-route, .lyr-route-step').forEach(function(p) {{ p.style.display = this.checked ? '' : 'none'; }}.bind(this));
  }});
  document.getElementById('cbAccess').addEventListener('change', function() {{
    var svg = document.getElementById('campusMap');
    svg.classList.toggle('mode-access', this.checked);
  }});

  // 楼栋悬停 tooltip（复用真实地图逻辑）
  var tip = document.getElementById('tip');
  document.querySelectorAll('.bld').forEach(function(el) {{
    el.addEventListener('mousemove', function(ev) {{
      tip.textContent = el.dataset.name || '';
      tip.style.left = (ev.clientX + 14) + 'px';
      tip.style.top = (ev.clientY + 14) + 'px';
      tip.style.opacity = 1;
    }});
    el.addEventListener('mouseleave', function() {{ tip.style.opacity = 0; }});
  }});
</script>
</body>
</html>'''

with open('invisible-distance-prototype/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('done, chars:', len(html))
