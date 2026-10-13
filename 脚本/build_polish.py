import re

IN = 'invisible-distance-prototype/index.html'
OUT = 'invisible-distance-prototype/index.html'

with open(IN, 'r', encoding='utf-8') as f:
    html = f.read()

# =============================================================================
# 1. 取消中心湖蓝色标记：把 lyr-lake 的 fill 改成与背景一致 (#eef3ea) 并去掉 stroke
# =============================================================================
html = html.replace(
    '<path class="lyr-lake" d="M 520.1 543.0 L 591.4 535.3 L 691.1 504.5 L 790.9 466.0 L 847.9 442.9 L 805.1 419.8 L 733.9 412.1 L 662.6 435.2 L 598.5 473.7 L 541.5 512.2 L 513.0 543.0 Z" fill="#a8cfe8" stroke="#8bb8d8" stroke-width="1.5"/>',
    '<path class="lyr-lake" d="M 520.1 543.0 L 591.4 535.3 L 691.1 504.5 L 790.9 466.0 L 847.9 442.9 L 805.1 419.8 L 733.9 412.1 L 662.6 435.2 L 598.5 473.7 L 541.5 512.2 L 513.0 543.0 Z" fill="#eef3ea" stroke="none"/>'
)

# =============================================================================
# 2. 湖心岛改名+铺更明显的绿色底（扩大填充范围，覆盖栈道区域）
# =============================================================================
# 把原来的岛 + 栈道 合并成一个更大的绿色区域
html = html.replace(
    '<path d="M 560.5 444.6 L 580.2 438.5 L 586.8 426.2 L 573.6 420.0 L 553.9 426.2 L 547.3 438.5" fill="#c8e6c9" stroke="#81c784" stroke-width="1"/>',
    '<path d="M 555 440 L 585 432 L 592 418 L 572 412 L 548 420 L 540 435 Z" fill="#a5d6a7" stroke="#66bb6a" stroke-width="1"/>'
)
html = html.replace(
    '<path d="M 540.7 432.3 L 557.8 436.0" fill="none" stroke="#d97757" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>',
    '<path d="M 540 430 L 560 435" fill="none" stroke="#d97757" stroke-width="2" stroke-linecap="round" opacity="0.8"/>'
)
html = html.replace(
    '<text class="lbl" x="567" y="432" font-size="11" font-weight="600" fill="#2e7d32" font-style="italic" paint-order="stroke" stroke="#ffffff" stroke-width="2">湖心岛</text>',
    '<text class="lbl" x="565" y="430" font-size="12" font-weight="700" fill="#1b5e20" paint-order="stroke" stroke="#ffffff" stroke-width="3">中心岛</text>'
)

# =============================================================================
# 3. 删除DJI航拍标记
# =============================================================================
html = html.replace(
    '<text class="lbl" x="677" y="494" font-size="10" font-weight="600" fill="#059669" paint-order="stroke" stroke="#ffffff" stroke-width="2">DJI航拍点</text>\n<polygon points="677,470 672,480 682,480" fill="#10b981" stroke="#fff" stroke-width="1.5"/>',
    ''
)

# =============================================================================
# 4. 路线默认隐藏：去掉 checked，并在SVG路线元素上加 display:none
# =============================================================================
html = html.replace(
    '<label><input type="checkbox" id="cbRoute" checked> <span>路线</span></label>',
    '<label><input type="checkbox" id="cbRoute"> <span>路线</span></label>'
)

# 给所有 route-A / route-B / beeline / route-step / 起终点标记 / 方向文字 加默认隐藏
# 替换 </svg>\n</svg> 为正确的单个 </svg>
html = html.replace('</svg>\n</svg>', '</svg>')

# 在 <svg> 内的 defs 后添加一个 style 块，默认隐藏路线
old_defs_end = '</style></defs>'
new_defs_end = '''</style></defs>
<style>
  .lyr-route, .lyr-route-step, .lyr-beeline, .route-marker, .route-guide { display:none; }
  .routes-visible .lyr-route, .routes-visible .lyr-route-step, .routes-visible .lyr-beeline,
  .routes-visible .route-marker, .routes-visible .route-guide { display:inline; }
</style>'''
html = html.replace(old_defs_end, new_defs_end, 1)

# =============================================================================
# 5. 路径画细 + 给路线元素加 class 便于统一控制
# =============================================================================
# route-A stroke-width 4→2.5, 5→3
html = re.sub(r'stroke-width="4"([^>]*class="lyr-route route-A")', r'stroke-width="2.5"\1', html)
html = re.sub(r'stroke-width="5"([^>]*class="lyr-route route-A")', r'stroke-width="3"\1', html)
# route-B stroke-width 4→2.5
html = re.sub(r'stroke-width="4"([^>]*class="lyr-route route-B")', r'stroke-width="2.5"\1', html)
# 方向直线也画细
html = re.sub(r'stroke-width="1\.5"([^>]*class="lyr-beeline")', r'stroke-width="1"\1', html)

# =============================================================================
# 6. 在路径关键点添加可点击的指引标记（默认收起）
#    关键点：图书馆出口、台阶点（2个）、V27入口、路线B的转角点
# =============================================================================

# 在SVG末尾（</svg>之前）插入交互标记和指引面板
# 先找到最后一个 </svg> 的位置
svg_end = html.rfind('</svg>')
if svg_end > 0:
    # 找到实际地图SVG结束位置（在 route markers 之后，文字之前）
    # 我们直接在所有路线标记之后、最后的 </svg> 标签之前插入
    markers_html = '''
<!-- 路线关键点指引标记 -->
<g class="route-marker route-A-only">
  <circle cx="534" cy="426" r="6" fill="#3b82f6" stroke="#fff" stroke-width="2" class="guide-dot" data-guide="lib-exit" style="cursor:pointer"/>
  <circle cx="534" cy="426" r="10" fill="none" stroke="#3b82f6" stroke-width="1.5" opacity="0.4" class="guide-pulse"/>
</g>
<g class="route-marker route-A-only">
  <circle cx="461" cy="412" r="6" fill="#dc2626" stroke="#fff" stroke-width="2" class="guide-dot" data-guide="steps-down" style="cursor:pointer"/>
  <circle cx="461" cy="412" r="10" fill="none" stroke="#dc2626" stroke-width="1.5" opacity="0.4" class="guide-pulse"/>
</g>
<g class="route-marker route-A-only">
  <circle cx="551" cy="455" r="5" fill="#f59e0b" stroke="#fff" stroke-width="1.5" class="guide-dot" data-guide="turn-a1" style="cursor:pointer"/>
</g>
<g class="route-marker route-B-only">
  <circle cx="219" cy="292" r="6" fill="#10b981" stroke="#fff" stroke-width="2" class="guide-dot" data-guide="plaza" style="cursor:pointer"/>
  <circle cx="219" cy="292" r="10" fill="none" stroke="#10b981" stroke-width="1.5" opacity="0.4" class="guide-pulse"/>
</g>
<g class="route-marker route-B-only">
  <circle cx="292" cy="290" r="5" fill="#10b981" stroke="#fff" stroke-width="1.5" class="guide-dot" data-guide="turn-b1" style="cursor:pointer"/>
</g>
<g class="route-marker route-B-only">
  <circle cx="145" cy="305" r="6" fill="#10b981" stroke="#fff" stroke-width="2" class="guide-dot" data-guide="v27-entry" style="cursor:pointer"/>
  <circle cx="145" cy="305" r="10" fill="none" stroke="#10b981" stroke-width="1.5" opacity="0.4" class="guide-pulse"/>
</g>

<!-- 指引弹窗（默认隐藏，通过JS控制显示） -->
<g class="route-guide" id="guide-lib-exit" opacity="0" style="pointer-events:none">
  <rect x="544" y="400" width="200" height="90" rx="10" fill="rgba(255,255,255,0.98)" stroke="#3b82f6" stroke-width="1.5" filter="drop-shadow(0 4px 12px rgba(0,0,0,0.15))"/>
  <text x="554" y="422" font-size="12" font-weight="700" fill="#1e40af">图书馆 2F 出口</text>
  <text x="554" y="440" font-size="11" fill="#475576">唯一出入口，朝东南（湖方向）</text>
  <text x="554" y="456" font-size="11" fill="#475576">出口无台阶，可直接外出</text>
  <text x="554" y="472" font-size="11" fill="#475576">出门后左转选路线A，右转选路线B</text>
  <polygon points="534,426 544,416 544,436" fill="#3b82f6"/>
</g>
<g class="route-guide" id="guide-steps-down" opacity="0" style="pointer-events:none">
  <rect x="471" y="340" width="180" height="80" rx="10" fill="rgba(255,255,255,0.98)" stroke="#dc2626" stroke-width="1.5" filter="drop-shadow(0 4px 12px rgba(0,0,0,0.15))"/>
  <text x="481" y="362" font-size="12" font-weight="700" fill="#991b1b">台阶路段 · 下坡 -1 层</text>
  <text x="481" y="380" font-size="11" fill="#475576">从此处下台阶，直达地面层</text>
  <text x="481" y="396" font-size="11" fill="#475576">普通行人：省力捷径</text>
  <text x="481" y="412" font-size="11" fill="#475576">拖行李/轮椅：建议绕行路线B</text>
  <polygon points="461,412 471,402 471,422" fill="#dc2626"/>
</g>
<g class="route-guide" id="guide-turn-a1" opacity="0" style="pointer-events:none">
  <rect x="561" y="435" width="150" height="55" rx="10" fill="rgba(255,255,255,0.98)" stroke="#f59e0b" stroke-width="1.5" filter="drop-shadow(0 4px 12px rgba(0,0,0,0.15))"/>
  <text x="571" y="457" font-size="12" font-weight="700" fill="#92400e">转角 · 向V27方向</text>
  <text x="571" y="475" font-size="11" fill="#475576">沿步道继续向西，直达V27入口</text>
  <polygon points="551,455 561,445 561,465" fill="#f59e0b"/>
</g>
<g class="route-guide" id="guide-plaza" opacity="0" style="pointer-events:none">
  <rect x="229" y="252" width="180" height="80" rx="10" fill="rgba(255,255,255,0.98)" stroke="#10b981" stroke-width="1.5" filter="drop-shadow(0 4px 12px rgba(0,0,0,0.15))"/>
  <text x="239" y="274" font-size="12" font-weight="700" fill="#065f46">会贤邨广场</text>
  <text x="239" y="292" font-size="11" fill="#475576">路线B经过的开放广场区域</text>
  <text x="239" y="308" font-size="11" fill="#475576">全平路，无台阶，轮椅友好</text>
  <text x="239" y="324" font-size="11" fill="#475576">从这里继续向西可达V28→V29</text>
  <polygon points="219,292 229,282 229,302" fill="#10b981"/>
</g>
<g class="route-guide" id="guide-turn-b1" opacity="0" style="pointer-events:none">
  <rect x="302" y="270" width="150" height="55" rx="10" fill="rgba(255,255,255,0.98)" stroke="#10b981" stroke-width="1.5" filter="drop-shadow(0 4px 12px rgba(0,0,0,0.15))"/>
  <text x="312" y="292" font-size="12" font-weight="700" fill="#065f46">转角 · 向南绕行</text>
  <text x="312" y="310" font-size="11" fill="#475576">转向南，经体育馆方向绕行</text>
  <polygon points="292,290 302,280 302,300" fill="#10b981"/>
</g>
<g class="route-guide" id="guide-v27-entry" opacity="0" style="pointer-events:none">
  <rect x="155" y="275" width="170" height="80" rx="10" fill="rgba(255,255,255,0.98)" stroke="#10b981" stroke-width="1.5" filter="drop-shadow(0 4px 12px rgba(0,0,0,0.15))"/>
  <text x="165" y="297" font-size="12" font-weight="700" fill="#065f46">V27 雨果楼 1F 入口</text>
  <text x="165" y="315" font-size="11" fill="#475576">入口位于楼栋拐弯处</text>
  <text x="165" y="331" font-size="11" fill="#475576">无台阶，有电梯通达全楼层</text>
  <text x="165" y="347" font-size="11" fill="#475576">路线A和路线B均到达此入口</text>
  <polygon points="145,305 155,295 155,315" fill="#10b981"/>
</g>
'''
    # 插入到最后一个 </svg> 之前
    html = html[:svg_end] + markers_html + html[svg_end:]

# =============================================================================
# 7. 更新JS：路线复选框控制 + 指引点击交互
# =============================================================================
# 修改 cbRoute 事件，同时切换 routes-visible class
old_route_cb = """  document.getElementById('cbRoute').addEventListener('change', function() {
    document.querySelectorAll('.lyr-route, .lyr-route-step').forEach(function(p) { p.style.display = this.checked ? '' : 'none'; }.bind(this));
  });"""

new_route_cb = """  document.getElementById('cbRoute').addEventListener('change', function() {
    var svg = document.getElementById('campusMap');
    svg.classList.toggle('routes-visible', this.checked);
    // 默认收起所有指引
    document.querySelectorAll('.route-guide').forEach(function(g) { g.setAttribute('opacity', '0'); });
  });"""

html = html.replace(old_route_cb, new_route_cb)

# 在移动端手势代码之前添加指引点击交互代码
old_touch = "  // ===== Mobile Map Pan/Zoom"
new_guide_js = """  // ===== Route Guide Interactions =====
  (function() {
    var activeGuide = null;
    document.querySelectorAll('.guide-dot').forEach(function(dot) {
      dot.addEventListener('click', function(e) {
        e.stopPropagation();
        var gid = dot.dataset.guide;
        var guide = document.getElementById('guide-' + gid);
        if (!guide) return;
        // 如果点击的是当前已展开的，则收起
        if (activeGuide === guide) {
          guide.setAttribute('opacity', '0');
          activeGuide = null;
          return;
        }
        // 收起其他
        document.querySelectorAll('.route-guide').forEach(function(g) { g.setAttribute('opacity', '0'); });
        // 展开当前
        guide.setAttribute('opacity', '1');
        activeGuide = guide;
      });
    });
    // 点击地图空白处收起指引
    document.getElementById('campusMap').addEventListener('click', function(e) {
      if (!e.target.classList.contains('guide-dot')) {
        document.querySelectorAll('.route-guide').forEach(function(g) { g.setAttribute('opacity', '0'); });
        activeGuide = null;
      }
    });
  })();

  // ===== Mobile Map Pan/Zoom"""

html = html.replace(old_touch, new_guide_js)

# =============================================================================
# 8. 删除重复的图例项（原文件有重复的"方向直线"和"遮阴/连廊区"）
# =============================================================================
# 把 legend 里重复的三组改成一组
old_legend = '''      <div class="legend">
        <span><span class="dot" style="background:linear-gradient(135deg,#3b82f6,#2563eb)"></span> 路线 A（台阶近路）</span>
        <span><span class="dot" style="background:linear-gradient(135deg,#34d399,#10b981)"></span> 路线 B（绕行平路）</span>
        <span><span class="dot" style="background:#ef4444"></span> 方向直线</span>
        <span><span class="dot" style="background:rgba(16,185,129,0.3);border:1px solid #10b981"></span> 遮阴/连廊区</span>
        <span><span class="dot" style="background:#ef4444"></span> 方向直线</span>
        <span><span class="dot" style="background:rgba(16,185,129,0.3);border:1px solid #10b981"></span> 遮阴/连廊区</span>
        <span><span class="dot" style="background:#ef4444"></span> 方向直线</span>
        <span><span class="dot" style="background:rgba(16,185,129,0.3);border:1px solid #10b981"></span> 遮阴/连廊区</span>
        <span><span class="dot" style="background:#f59e0b"></span> 台阶成本点</span>
        <span><span class="dot" style="background:#c7d2fe"></span> 教学楼</span>
        <span><span class="dot" style="background:#fde68a"></span> 宿舍楼</span>
        <span><span class="dot" style="background:#a7d8d0"></span> 大型设施</span>
      </div>'''

new_legend = '''      <div class="legend">
        <span><span class="dot" style="background:linear-gradient(135deg,#3b82f6,#2563eb)"></span> 路线 A（台阶近路）</span>
        <span><span class="dot" style="background:linear-gradient(135deg,#34d399,#10b981)"></span> 路线 B（绕行平路）</span>
        <span><span class="dot" style="background:#ef4444"></span> 方向直线</span>
        <span><span class="dot" style="background:rgba(16,185,129,0.3);border:1px solid #10b981"></span> 遮阴/连廊区</span>
        <span><span class="dot" style="background:#f59e0b"></span> 可点击指引点</span>
        <span><span class="dot" style="background:#c7d2fe"></span> 教学楼</span>
        <span><span class="dot" style="background:#fde68a"></span> 宿舍楼</span>
        <span><span class="dot" style="background:#a7d8d0"></span> 大型设施</span>
      </div>'''

html = html.replace(old_legend, new_legend)

# 同时更新 source 描述
html = html.replace(
    '路线 A 沿真实 OSM 步道（含台阶下坡），路线 B 沿真实 OSM 步道经体育馆→V28→V29 全平路绕行。遮阴数据来自校园建筑设计资料。',
    '路线 A 沿真实 OSM 步道（含台阶下坡），路线 B 沿真实 OSM 步道经体育馆→V28→V29 全平路绕行。遮阴数据来自校园建筑设计资料。点击地图上的彩色圆点可查看详细指引。'
)

# =============================================================================
# 9. 添加指引标记的脉冲动画CSS
# =============================================================================
old_css_end = '''  /* Mobile card stacking */
  @media (max-width: 768px) {
    .side-panel { gap: 12px; }
    .map-toolbar { gap: 6px; }
    .map-toolbar label { padding: 5px 10px; font-size: 11.5px; }
    .legend { gap: 10px; font-size: 11.5px; }
    .bar-name { width: 60px; font-size: 11px; }
    .bar-val { width: 48px; font-size: 11px; }
    table { font-size: 12px; }
    th, td { padding: 7px 6px; }
  }
</style>'''

new_css_end = '''  /* Guide dot pulse */
  @keyframes guidePulse {
    0%, 100% { r: 8; opacity: 0.5; }
    50% { r: 14; opacity: 0.15; }
  }
  .guide-pulse { animation: guidePulse 2s ease-in-out infinite; }
  .routes-visible .guide-dot { display: inline; cursor: pointer; }
  .routes-visible .guide-dot:hover { filter: drop-shadow(0 0 4px rgba(0,0,0,0.3)); }
  .route-guide { transition: opacity .2s ease; }

  /* Mobile card stacking */
  @media (max-width: 768px) {
    .side-panel { gap: 12px; }
    .map-toolbar { gap: 6px; }
    .map-toolbar label { padding: 5px 10px; font-size: 11.5px; }
    .legend { gap: 10px; font-size: 11.5px; }
    .bar-name { width: 60px; font-size: 11px; }
    .bar-val { width: 48px; font-size: 11px; }
    table { font-size: 12px; }
    th, td { padding: 7px 6px; }
  }
</style>'''

html = html.replace(old_css_end, new_css_end)

# =============================================================================
# 10. 删除原路线标记里的旧台阶点和文字（被新的交互标记替代）
# =============================================================================
# 删除旧的 route-step 圆圈
html = re.sub(r'<circle class="lyr-route-step"[^/]*/>\n?', '', html)
# 删除旧的 "会贤邨广场" 文字（已整合到指引中）
html = re.sub(r'<text class="lbl" x="227" y="286"[^>]*>会贤邨广场</text>\n?', '', html)
# 删除旧的起点/终点重叠文字（已有指引弹窗）
html = re.sub(r'<text class="lbl lyr-route" x="542" y="494"[^>]*>起点·图书馆</text>\n?', '', html)
html = re.sub(r'<text class="lbl lyr-route" x="142" y="291"[^>]*>终点·V27</text>\n?', '', html)

# =============================================================================
# 保存
# =============================================================================
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print('done. file size:', len(html))
# 验证关键元素
print('guide dots:', html.count('guide-dot'))
print('route-guide groups:', html.count('route-guide'))
print('cbRoute checked:', 'checked' in html[html.find('cbRoute'):html.find('cbRoute')+80])
print('lyr-lake fill:', '#eef3ea' in html[html.find('lyr-lake'):html.find('lyr-lake')+120])
print('中心岛:', '中心岛' in html)
print('DJI:', 'DJI' in html)
