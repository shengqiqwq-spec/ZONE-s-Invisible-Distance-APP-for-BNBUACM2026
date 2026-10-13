#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the prettified + responsive prototype.
Reads the existing SVG core from svg_core.txt and wraps it in a new UI.
"""

import os

# Read existing SVG content (paths, buildings, labels, routes)
svg_path = 'D:/study/Workbuddy/2026-10-11-18-01-42/bnbu-campus-map/svg_core.txt'
with open(svg_path, 'r', encoding='utf-8') as f:
    svg_core = f.read().strip()

output_path = 'D:/study/Workbuddy/2026-10-11-18-01-42/invisible-distance-prototype/index.html'

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>看不见的距离 · 图书馆 → V27</title>
<style>
  /* ========== CSS Variables ========== */
  :root {
    --bg: #f0f2f5;
    --surface: #ffffff;
    --surface-2: #f8fafc;
    --text: #0f172a;
    --text-2: #334155;
    --text-3: #64748b;
    --text-muted: #94a3b8;
    --primary: #4f46e5;
    --primary-light: #e0e7ff;
    --primary-soft: #6366f1;
    --success: #10b981;
    --success-light: #d1fae5;
    --warning: #f59e0b;
    --warning-light: #fef3c7;
    --danger: #ef4444;
    --danger-light: #fee2e2;
    --info: #0ea5e9;
    --info-light: #e0f2fe;
    --shadow-sm: 0 1px 2px rgba(15,23,42,0.04);
    --shadow: 0 4px 16px rgba(15,23,42,0.06);
    --shadow-lg: 0 12px 40px rgba(15,23,42,0.1);
    --radius-sm: 10px;
    --radius: 16px;
    --radius-lg: 20px;
    --transition: all .25s cubic-bezier(.4,0,.2,1);
  }

  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; min-height: 100vh; background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    line-height: 1.6;
  }

  /* ========== Layout ========== */
  .wrap { max-width: 1520px; margin: 0 auto; padding: 24px; }
  @media (max-width: 768px) { .wrap { padding: 12px; } }

  /* ========== Header ========== */
  header {
    text-align: center; margin-bottom: 24px;
    animation: fadeInDown .6s ease both;
  }
  header h1 {
    font-size: 28px; font-weight: 800; margin: 0;
    background: linear-gradient(135deg, var(--primary) 0%, #7c3aed 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -0.5px;
  }
  header .sub {
    color: var(--text-3); font-size: 14px; margin-top: 8px;
    line-height: 1.8; max-width: 640px; margin-left: auto; margin-right: auto;
  }
  header .sub strong { color: var(--text-2); font-weight: 600; }
  @media (max-width: 768px) {
    header h1 { font-size: 22px; }
    header .sub { font-size: 12.5px; }
  }

  /* ========== Control Bar ========== */
  .control-bar {
    display: flex; flex-wrap: wrap; justify-content: center; align-items: center;
    gap: 16px; margin-bottom: 20px;
    animation: fadeInUp .5s ease .1s both;
  }
  .switch-row {
    display: flex; gap: 8px;
    background: var(--surface); padding: 5px; border-radius: 999px;
    box-shadow: var(--shadow); border: 1px solid rgba(0,0,0,0.04);
  }
  .switch-row button {
    border: none; background: transparent; color: var(--text-3);
    font: inherit; font-size: 14px; font-weight: 600;
    padding: 10px 22px; border-radius: 999px; cursor: pointer;
    transition: var(--transition); position: relative; white-space: nowrap;
  }
  .switch-row button:hover { color: var(--primary); }
  .switch-row button.active {
    background: linear-gradient(135deg, var(--primary) 0%, #7c3aed 100%);
    color: #fff; box-shadow: 0 4px 12px rgba(79,70,229,0.35);
  }
  @media (max-width: 768px) {
    .switch-row button { font-size: 13px; padding: 10px 16px; }
  }

  .floor-selector {
    display: flex; align-items: center; gap: 10px;
    background: var(--surface); border-radius: 999px;
    padding: 8px 18px; font-size: 14px;
    box-shadow: var(--shadow); border: 1px solid rgba(0,0,0,0.04);
  }
  .floor-selector label { color: var(--text-3); font-weight: 600; white-space: nowrap; }
  .floor-selector select {
    border: none; background: transparent; font: inherit; font-size: 14px;
    color: var(--text-2); cursor: pointer; outline: none; min-width: 200px;
    appearance: none; -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 0 center; padding-right: 22px;
  }
  @media (max-width: 768px) {
    .floor-selector { width: 100%; justify-content: space-between; border-radius: var(--radius-sm); }
    .floor-selector select { min-width: 0; flex: 1; }
  }

  /* ========== Main Layout ========== */
  .layout {
    display: grid; grid-template-columns: 1fr 360px; gap: 20px; align-items: start;
    animation: fadeInUp .5s ease .2s both;
  }
  @media (max-width: 1024px) { .layout { grid-template-columns: 1fr 300px; } }
  @media (max-width: 768px) { .layout { grid-template-columns: 1fr; gap: 14px; } }

  /* ========== Cards ========== */
  .card {
    background: var(--surface); border-radius: var(--radius-lg);
    box-shadow: var(--shadow); padding: 20px;
    transition: var(--transition); border: 1px solid rgba(0,0,0,0.03);
  }
  .card:hover { box-shadow: var(--shadow-lg); transform: translateY(-1px); }
  @media (max-width: 768px) { .card { padding: 16px; border-radius: var(--radius); } }

  /* ========== Map Panel ========== */
  .map-panel { position: relative; overflow: hidden; }
  .map-panel svg {
    width: 100%; height: auto; display: block; border-radius: var(--radius);
    background: #eef3ea; cursor: grab;
    touch-action: pan-x pan-y pinch-zoom;
  }
  .map-panel svg:active { cursor: grabbing; }
  .map-toolbar {
    display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
    margin-bottom: 12px; font-size: 13px;
  }
  .map-toolbar label {
    display: inline-flex; align-items: center; gap: 6px; cursor: pointer;
    background: var(--surface-2); padding: 6px 14px; border-radius: 999px;
    border: 1px solid rgba(0,0,0,0.05); font-weight: 500; color: var(--text-2);
    transition: var(--transition); user-select: none; font-size: 12.5px;
  }
  .map-toolbar label:hover { background: var(--primary-light); color: var(--primary); border-color: var(--primary-soft); }
  .map-toolbar label input[type="checkbox"] {
    accent-color: var(--primary); width: 15px; height: 15px; cursor: pointer;
  }

  /* ========== Side Panel ========== */
  .side-panel { display: flex; flex-direction: column; gap: 16px; }
  .side-panel h2 {
    margin: 0 0 10px; font-size: 15px; font-weight: 700; color: var(--text);
    display: flex; align-items: center; gap: 8px;
  }
  .side-panel h2::before {
    content: ''; display: inline-block; width: 4px; height: 18px;
    background: linear-gradient(180deg, var(--primary), #7c3aed);
    border-radius: 2px;
  }
  .side-panel .hint {
    color: var(--text-muted); font-size: 12.5px; margin-bottom: 12px; line-height: 1.6;
  }

  /* ========== Floor Info ========== */
  .floor-info { margin-bottom: 4px; }
  .floor-title { font-size: 17px; font-weight: 800; color: var(--text); margin-bottom: 8px; }
  .floor-meta { font-size: 13px; color: var(--text-3); margin-bottom: 12px; line-height: 1.7; }
  .floor-status {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 12px; font-weight: 700; padding: 5px 14px; border-radius: 999px;
    margin-bottom: 12px; letter-spacing: 0.3px;
  }
  .floor-status::before {
    content: ''; display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  }
  .status-ok { background: var(--success-light); color: #065f46; }
  .status-ok::before { background: var(--success); }
  .status-warn { background: var(--warning-light); color: #92400e; }
  .status-warn::before { background: var(--warning); }
  .status-danger { background: var(--danger-light); color: #991b1b; }
  .status-danger::before { background: var(--danger); }
  .status-info { background: var(--info-light); color: #075985; }
  .status-info::before { background: var(--info); }

  /* ========== Badges & Notes ========== */
  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 13px; font-weight: 700; color: #fff;
    border-radius: 999px; padding: 7px 16px; margin-bottom: 12px;
    box-shadow: var(--shadow-sm);
  }
  .badge::before { content: '★'; font-size: 11px; }
  .badge.rec-a { background: linear-gradient(135deg, #3b82f6, #2563eb); }
  .badge.rec-b { background: linear-gradient(135deg, #10b981, #059669); }
  .badge.warn { background: linear-gradient(135deg, #f59e0b, #d97706); }
  .badge.danger { background: linear-gradient(135deg, #ef4444, #dc2626); }

  .note {
    background: linear-gradient(135deg, #eff6ff, #eef2ff);
    border-left: 4px solid var(--primary); border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 12px 14px; font-size: 13px; line-height: 1.8; color: #1e3a8a; margin-bottom: 14px;
  }
  .note.warn {
    background: linear-gradient(135deg, #fffbeb, #fef9c3);
    border-left-color: var(--warning); color: #92400e;
  }

  /* ========== Table ========== */
  table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; }
  th, td { padding: 9px 10px; text-align: center; }
  th:first-child, td:first-child { text-align: left; color: var(--text-2); font-weight: 600; }
  th {
    background: var(--surface-2); color: var(--text-3); font-weight: 600; font-size: 11.5px;
    text-transform: uppercase; letter-spacing: 0.5px;
    position: sticky; top: 0; z-index: 1;
  }
  th:first-child { border-radius: 8px 0 0 8px; }
  th:last-child { border-radius: 0 8px 8px 0; }
  tr { transition: background .15s; }
  tr:hover td { background: rgba(79,70,229,0.03); }
  tr.win td { background: rgba(16,185,129,0.06); }
  tr.lose td { background: rgba(239,68,68,0.05); }
  .rec-mark { color: var(--success); font-weight: 700; }
  .risk-mark { color: var(--danger); font-weight: 700; }
  td { border-bottom: 1px solid #f1f5f9; }

  /* ========== Bars ========== */
  .bars { margin-top: 18px; }
  .bar-group { margin-bottom: 16px; }
  .bar-title { font-size: 12px; color: var(--text-3); margin-bottom: 6px; font-weight: 600; display: flex; justify-content: space-between; }
  .bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
  .bar-name { width: 70px; font-size: 12px; color: var(--text-2); text-align: right; font-weight: 500; }
  .bar-track { flex: 1; background: #f1f5f9; border-radius: 8px; height: 14px; overflow: hidden; position: relative; }
  .bar-fill { height: 100%; border-radius: 8px; transition: width .5s cubic-bezier(.4,0,.2,1); position: relative; }
  .bar-fill::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg, rgba(255,255,255,0.2) 0%, transparent 100%);
  }
  .bar-fill.A { background: linear-gradient(90deg, #60a5fa, #3b82f6); }
  .bar-fill.B { background: linear-gradient(90deg, #34d399, #10b981); }
  .bar-val { width: 56px; font-size: 12px; color: var(--text-2); font-weight: 600; text-align: right; }

  /* ========== Legend ========== */
  .legend {
    display: flex; flex-wrap: wrap; gap: 14px; margin-top: 14px; font-size: 12.5px;
    color: var(--text-2); padding-top: 14px; border-top: 1px solid #f1f5f9;
  }
  .legend span { display: inline-flex; align-items: center; gap: 6px; font-weight: 500; }
  .dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; box-shadow: var(--shadow-sm); }

  /* ========== Source ========== */
  .source {
    margin-top: 14px; font-size: 11.5px; color: var(--text-muted);
    line-height: 1.7; padding: 12px; background: var(--surface-2);
    border-radius: var(--radius-sm);
  }
  .source b { color: var(--text-3); }

  /* ========== Footer ========== */
  footer {
    text-align: center; color: var(--text-muted); font-size: 12.5px;
    margin-top: 24px; line-height: 1.8; padding-bottom: 80px;
  }
  footer strong { color: var(--text-3); }
  @media (min-width: 769px) { footer { padding-bottom: 24px; } }

  /* ========== Tooltip ========== */
  #tip {
    position: fixed; pointer-events: none; background: rgba(15,23,42,0.92);
    color: #fff; font-size: 12.5px; padding: 8px 14px; border-radius: 10px;
    opacity: 0; transition: opacity .15s, transform .15s; z-index: 100;
    max-width: 280px; backdrop-filter: blur(8px); line-height: 1.6;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2); transform: translateY(4px);
  }
  #tip.visible { opacity: 1; transform: translateY(0); }

  /* ========== SVG Route Interactions ========== */
  .route-A { opacity: 0.85; transition: opacity .4s, stroke-width .4s; }
  .route-B { opacity: 0.35; transition: opacity .4s, stroke-width .4s; }
  .view-walker .route-A { opacity: 0.95; stroke-width: 6; filter: drop-shadow(0 2px 4px rgba(37,99,235,0.3)); }
  .view-walker .route-B { opacity: 0.25; }
  .view-luggage .route-A { opacity: 0.25; }
  .view-luggage .route-B { opacity: 0.95; stroke-width: 6; filter: drop-shadow(0 2px 4px rgba(22,163,74,0.3)); }
  .view-wheelchair .route-A { opacity: 0.12; stroke-dasharray: 8 4; }
  .view-wheelchair .route-B { opacity: 0.95; stroke-width: 6; filter: drop-shadow(0 2px 4px rgba(22,163,74,0.3)); }

  /* ========== Mobile Bottom Nav ========== */
  .mobile-nav {
    display: none; position: fixed; bottom: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.92); backdrop-filter: blur(16px);
    border-top: 1px solid rgba(0,0,0,0.06); z-index: 50;
    padding: 8px 12px 16px; box-shadow: 0 -4px 20px rgba(0,0,0,0.06);
  }
  .mobile-nav .nav-row {
    display: flex; justify-content: space-around; align-items: center;
  }
  .mobile-nav .nav-btn {
    display: flex; flex-direction: column; align-items: center; gap: 3px;
    background: none; border: none; font: inherit; font-size: 11px;
    color: var(--text-muted); cursor: pointer; padding: 6px 12px;
    transition: var(--transition); border-radius: 12px;
  }
  .mobile-nav .nav-btn .nav-icon {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; transition: var(--transition);
  }
  .mobile-nav .nav-btn.active { color: var(--primary); }
  .mobile-nav .nav-btn.active .nav-icon {
    background: linear-gradient(135deg, var(--primary), #7c3aed);
    color: #fff; box-shadow: 0 4px 12px rgba(79,70,229,0.35);
  }
  @media (max-width: 768px) { .mobile-nav { display: block; } }

  /* ========== Animations ========== */
  @keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
  }

  /* ========== Scrollbar ========== */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

  /* ========== Accessibility improvements ========== */
  .sr-only {
    position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
  }

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
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>看不见的距离 · 图书馆 → V27</h1>
    <div class="sub">
      <strong>同一段路，三种人生，三种「最近」</strong><br>
      底图基于 OpenStreetMap 真实坐标投影 · 路线基于现场核实 · 楼层信息基于用户实测
    </div>
  </header>

  <div class="control-bar">
    <div class="switch-row" id="desktopSwitch">
      <button data-view="walker" class="active" aria-pressed="true">普通行人</button>
      <button data-view="luggage" aria-pressed="false">拖行李</button>
      <button data-view="wheelchair" aria-pressed="false">轮椅 / 无障碍</button>
    </div>
    <div class="floor-selector">
      <label for="floorSelect">当前楼层</label>
      <select id="floorSelect" aria-label="选择当前楼层">
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
        <label><input type="checkbox" id="cbFoot" checked> <span>步行小径</span></label>
        <label><input type="checkbox" id="cbLabel" checked> <span>楼栋标注</span></label>
        <label><input type="checkbox" id="cbRoute" checked> <span>路线</span></label>
        <label><input type="checkbox" id="cbAccess"> <span>无障碍视角</span></label>
      </div>
      <div style="overflow:auto;-webkit-overflow-scrolling:touch;">
        <svg id="campusMap" viewBox="0 0 1200 840" xmlns="http://www.w3.org/2000/svg" font-family="PingFang SC, Microsoft YaHei, sans-serif">
''' + svg_core + r'''
        </svg>
      </div>
      <div class="legend">
        <span><span class="dot" style="background:linear-gradient(135deg,#3b82f6,#2563eb)"></span> 路线 A（台阶近路）</span>
        <span><span class="dot" style="background:linear-gradient(135deg,#34d399,#10b981)"></span> 路线 B（绕行平路）</span>
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
      <div class="card floor-info" id="floorCard">
        <h2>楼层状态</h2>
        <div class="hint">选择上方「当前楼层」，查看该层的出入口与可达性。</div>
        <div id="floorContent"></div>
      </div>

      <div class="card">
        <h2>路线对比</h2>
        <div class="hint">切换上方视角，观察推荐如何反转。</div>
        <div id="recBadge" class="badge rec-a">推荐路线 A</div>
        <div class="note" id="note"></div>

        <div style="overflow-x:auto;">
          <table>
            <thead>
              <tr><th>指标</th><th>路线 A</th><th>路线 B</th></tr>
            </thead>
            <tbody id="tbody"></tbody>
          </table>
        </div>

        <div class="bars">
          <div class="bar-group">
            <div class="bar-title">距离 <span style="font-weight:400;color:var(--text-muted)">(m)</span></div>
            <div class="bar-row"><span class="bar-name">路线 A</span><span class="bar-track"><span class="bar-fill A" id="barDistA"></span></span><span class="bar-val" id="valDistA"></span></div>
            <div class="bar-row"><span class="bar-name">路线 B</span><span class="bar-track"><span class="bar-fill B" id="barDistB"></span></span><span class="bar-val" id="valDistB"></span></div>
          </div>
          <div class="bar-group">
            <div class="bar-title">预估时间 <span style="font-weight:400;color:var(--text-muted)">(min)</span></div>
            <div class="bar-row"><span class="bar-name">路线 A</span><span class="bar-track"><span class="bar-fill A" id="barTimeA"></span></span><span class="bar-val" id="valTimeA"></span></div>
            <div class="bar-row"><span class="bar-name">路线 B</span><span class="bar-track"><span class="bar-fill B" id="barTimeB"></span></span><span class="bar-val" id="valTimeB"></span></div>
          </div>
          <div class="bar-group">
            <div class="bar-title">楼层高差 <span style="font-weight:400;color:var(--text-muted)">(层)</span></div>
            <div class="bar-row"><span class="bar-name">路线 A</span><span class="bar-track"><span class="bar-fill A" id="barFloorA"></span></span><span class="bar-val" id="valFloorA"></span></div>
            <div class="bar-row"><span class="bar-name">路线 B</span><span class="bar-track"><span class="bar-fill B" id="barFloorB"></span></span><span class="bar-val" id="valFloorB"></span></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <footer>
    <strong>核心洞察：</strong>对普通行人，最短的路就是最近的路；但对拖行李和轮椅，最短的路反而变成了最远甚至不可达的路。<br>
    图书馆 4 层、出入口在 2 层朝湖；V27 入口无台阶有电梯；路线 A 有一段 -1 层台阶下坡；路线 B 经体育馆→V28→V29 全平路绕行。
  </footer>
</div>

<!-- Mobile Bottom Navigation -->
<nav class="mobile-nav" aria-label="视角切换">
  <div class="nav-row">
    <button class="nav-btn active" data-view="walker" aria-pressed="true">
      <span class="nav-icon">🚶</span>
      <span>行人</span>
    </button>
    <button class="nav-btn" data-view="luggage" aria-pressed="false">
      <span class="nav-icon">🧳</span>
      <span>行李</span>
    </button>
    <button class="nav-btn" data-view="wheelchair" aria-pressed="false">
      <span class="nav-icon">♿</span>
      <span>轮椅</span>
    </button>
  </div>
</nav>

<div id="tip"></div>

<script>
  // ===== Floor Data =====
  var FLOOR_DATA = {
    'ground': {
      title: '户外地面层',
      status: 'status-ok',
      statusText: '可自由通行',
      desc: '地面层视角：所有户外路线均可通行。图书馆 2F 出口和 V27 1F 入口均直接可达。',
      routeNote: '从地面出发，路线选择取决于你的身体条件。'
    },
    'lib-1': {
      title: '图书馆 1F',
      status: 'status-warn',
      statusText: '无直接出入口',
      desc: '1F 没有通往户外的出入口。你必须乘坐电梯或走楼梯到 2F，才能从唯一的出口离开建筑。',
      routeNote: '先上楼到 2F，再选择路线 A 或路线 B。'
    },
    'lib-2': {
      title: '图书馆 2F · 唯一出入口',
      status: 'status-ok',
      statusText: '唯一出入口·可直接出发',
      desc: '2F 是图书馆唯一有出入口的楼层，出口朝东南（中心湖方向），无台阶。出门后可选路线 A（台阶近路）或路线 B（绕行平路）。',
      routeNote: '这是理想的出发楼层，出门即可选择任意路线。'
    },
    'lib-3': {
      title: '图书馆 3F',
      status: 'status-info',
      statusText: '需下至 2F',
      desc: '3F 没有通往户外的出入口。整栋楼有互通电梯，可乘电梯或走楼梯下至 2F，再从 2F 出口离开。',
      routeNote: '先下至 2F，再选择路线。电梯可通全楼层。'
    },
    'lib-4': {
      title: '图书馆 4F',
      status: 'status-info',
      statusText: '需下至 2F',
      desc: '4F 没有通往户外的出入口。整栋楼有互通电梯，可乘电梯或走楼梯下至 2F，再从 2F 出口离开。',
      routeNote: '先下至 2F，再选择路线。电梯可通全楼层。'
    },
    'v27-1': {
      title: 'V27 1F · 入口层',
      status: 'status-ok',
      statusText: '入口层·可直接到达',
      desc: '1F 是 V27 的入口层，入口位于整栋楼的拐弯处，无台阶。楼内有电梯可通达全楼层（1F–7F）。',
      routeNote: '从户外到达后可直接从 1F 入口进入。'
    },
    'v27-2': {
      title: 'V27 2F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '2F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    },
    'v27-3': {
      title: 'V27 3F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '3F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    },
    'v27-4': {
      title: 'V27 4F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '4F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    },
    'v27-5': {
      title: 'V27 5F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '5F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    },
    'v27-6': {
      title: 'V27 6F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '6F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    },
    'v27-7': {
      title: 'V27 7F',
      status: 'status-info',
      statusText: '需下至 1F',
      desc: '7F 没有通往户外的直接出入口。需乘电梯或走楼梯下至 1F，再从 1F 入口进出。',
      routeNote: '先下至 1F，再出入建筑。电梯全楼层通达。'
    }
  };

  function renderFloor(floorKey) {
    var d = FLOOR_DATA[floorKey];
    var html = '<div class="floor-title">' + d.title + '</div>' +
               '<div class="floor-status ' + d.status + '">' + d.statusText + '</div>' +
               '<div class="floor-meta">' + d.desc + '</div>';
    if (d.routeNote) {
      html += '<div class="note">' + d.routeNote + '</div>';
    }
    document.getElementById('floorContent').innerHTML = html;
    var svg = document.getElementById('campusMap');
    svg.classList.remove('floor-active');
    void svg.offsetWidth; // force reflow
    if (floorKey.startsWith('lib-') || floorKey.startsWith('v27-')) {
      svg.classList.add('floor-active');
      setTimeout(function() { svg.classList.remove('floor-active'); }, 2000);
    }
  }
  document.getElementById('floorSelect').addEventListener('change', function() {
    renderFloor(this.value);
  });
  renderFloor('ground');

  // ===== View Data =====
  var VIEWS = {
    walker: {
      rec: 'A',
      badgeClass: 'rec-a',
      badgeText: '推荐路线 A（台阶近路）',
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
    },
    luggage: {
      rec: 'B',
      badgeClass: 'rec-b',
      badgeText: '推荐路线 B（绕行平路）',
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
    },
    wheelchair: {
      rec: 'B',
      badgeClass: 'rec-b',
      badgeText: '推荐路线 B（绕行平路）',
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
    }
  };

  function renderView(view) {
    var v = VIEWS[view];
    var badge = document.getElementById('recBadge');
    badge.className = 'badge ' + v.badgeClass;
    badge.textContent = v.badgeText;
    document.getElementById('note').textContent = v.note;
    var svg = document.getElementById('campusMap');
    svg.setAttribute('class', 'view-' + view);
    var tbody = document.getElementById('tbody');
    tbody.innerHTML = '';
    v.rows.forEach(function(r) {
      var tr = document.createElement('tr');
      var recIdx = v.rec === 'A' ? 1 : 2;
      r.forEach(function(cell, i) {
        var td = document.createElement('td');
        td.textContent = cell;
        if (i === recIdx) td.className = 'rec-mark';
        tr.appendChild(td);
      });
      if (r[1] === '不可达' || r[2] === '不可达') tr.className = 'lose';
      tbody.appendChild(tr);
    });
    var maxDist = Math.max(v.dist[0], v.dist[1]);
    var maxTime = Math.max(v.time[0] || 1, v.time[1]);
    var maxFloor = Math.max(v.floor[0], v.floor[1]) || 1;
    setBar('barDistA', 'valDistA', v.dist[0], maxDist, v.dist[0] + 'm');
    setBar('barDistB', 'valDistB', v.dist[1], maxDist, v.dist[1] + 'm');
    setBar('barTimeA', 'valTimeA', v.time[0], maxTime, v.time[0] === 0 ? '不可达' : v.time[0] + '分');
    setBar('barTimeB', 'valTimeB', v.time[1], maxTime, v.time[1] + '分');
    setBar('barFloorA', 'valFloorA', v.floor[0], maxFloor, (v.floor[0] > 0 ? '+' : '') + v.floor[0] + '层');
    setBar('barFloorB', 'valFloorB', v.floor[1], maxFloor, (v.floor[1] > 0 ? '+' : '') + v.floor[1] + '层');
  }
  function setBar(fillId, valId, val, max, text) {
    var pct = max > 0 ? Math.max(0, Math.round(val / max * 100)) : 0;
    document.getElementById(fillId).style.width = pct + '%';
    document.getElementById(valId).textContent = text;
  }

  // Sync desktop and mobile switchers
  var currentView = 'walker';
  function setView(view) {
    currentView = view;
    // desktop buttons
    document.querySelectorAll('#desktopSwitch button').forEach(function(b) {
      b.classList.toggle('active', b.dataset.view === view);
      b.setAttribute('aria-pressed', b.dataset.view === view);
    });
    // mobile nav
    document.querySelectorAll('.mobile-nav .nav-btn').forEach(function(b) {
      b.classList.toggle('active', b.dataset.view === view);
      b.setAttribute('aria-pressed', b.dataset.view === view);
    });
    renderView(view);
  }
  document.querySelectorAll('#desktopSwitch button').forEach(function(btn) {
    btn.addEventListener('click', function() { setView(btn.dataset.view); });
  });
  document.querySelectorAll('.mobile-nav .nav-btn').forEach(function(btn) {
    btn.addEventListener('click', function() { setView(btn.dataset.view); });
  });
  renderView('walker');

  // ===== Map Layer Toggles =====
  document.getElementById('cbFoot').addEventListener('change', function() {
    document.querySelectorAll('.lyr-foot').forEach(function(p) { p.style.display = this.checked ? '' : 'none'; }.bind(this));
  });
  document.getElementById('cbLabel').addEventListener('change', function() {
    document.querySelectorAll('.lbl').forEach(function(p) { p.style.display = this.checked ? '' : 'none'; }.bind(this));
  });
  document.getElementById('cbRoute').addEventListener('change', function() {
    document.querySelectorAll('.lyr-route, .lyr-route-step').forEach(function(p) { p.style.display = this.checked ? '' : 'none'; }.bind(this));
  });
  document.getElementById('cbAccess').addEventListener('change', function() {
    var svg = document.getElementById('campusMap');
    svg.classList.toggle('mode-access', this.checked);
  });

  // ===== Tooltip =====
  var tip = document.getElementById('tip');
  document.querySelectorAll('.bld').forEach(function(el) {
    el.addEventListener('mousemove', function(ev) {
      tip.textContent = el.dataset.name || '';
      tip.style.left = (ev.clientX + 14) + 'px';
      tip.style.top = (ev.clientY + 14) + 'px';
      tip.classList.add('visible');
    });
    el.addEventListener('mouseleave', function() { tip.classList.remove('visible'); });
  });

  // ===== Mobile Map Pan/Zoom (basic touch support) =====
  (function() {
    var svg = document.getElementById('campusMap');
    var container = svg.parentElement;
    var scale = 1, tx = 0, ty = 0;
    var lastDist = 0, lastX = 0, lastY = 0;
    var isPinching = false, isPanning = false;

    container.addEventListener('touchstart', function(e) {
      if (e.touches.length === 2) {
        isPinching = true;
        var dx = e.touches[0].clientX - e.touches[1].clientX;
        var dy = e.touches[0].clientY - e.touches[1].clientY;
        lastDist = Math.sqrt(dx*dx + dy*dy);
      } else if (e.touches.length === 1) {
        isPanning = true;
        lastX = e.touches[0].clientX;
        lastY = e.touches[0].clientY;
      }
    }, {passive: true});

    container.addEventListener('touchmove', function(e) {
      if (isPinching && e.touches.length === 2) {
        e.preventDefault();
        var dx = e.touches[0].clientX - e.touches[1].clientX;
        var dy = e.touches[0].clientY - e.touches[1].clientY;
        var dist = Math.sqrt(dx*dx + dy*dy);
        var delta = dist - lastDist;
        scale = Math.max(0.8, Math.min(3, scale + delta * 0.005));
        lastDist = dist;
        updateTransform();
      } else if (isPanning && e.touches.length === 1) {
        e.preventDefault();
        var cx = e.touches[0].clientX;
        var cy = e.touches[0].clientY;
        tx += cx - lastX;
        ty += cy - lastY;
        lastX = cx; lastY = cy;
        updateTransform();
      }
    }, {passive: false});

    container.addEventListener('touchend', function() {
      isPinching = false; isPanning = false;
    });

    container.addEventListener('wheel', function(e) {
      e.preventDefault();
      var delta = e.deltaY > 0 ? -0.1 : 0.1;
      scale = Math.max(0.8, Math.min(3, scale + delta));
      updateTransform();
    }, {passive: false});

    function updateTransform() {
      svg.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
      svg.style.transformOrigin = 'center center';
    }

    // double tap to reset
    var lastTap = 0;
    container.addEventListener('touchend', function(e) {
      var now = Date.now();
      if (now - lastTap < 300) {
        scale = 1; tx = 0; ty = 0;
        updateTransform();
      }
      lastTap = now;
    });
  })();
</script>
</body>
</html>'''

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Built', output_path, 'size', len(html), 'chars')
