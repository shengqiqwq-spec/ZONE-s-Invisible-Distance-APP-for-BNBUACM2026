#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作品页回归测试 —— 改完 作品/index.html 后跑一下，确认没有把修好的东西改回去。

用法：
    python3 脚本/verify_page.py                 # 测作品页
    python3 脚本/verify_page.py 作品/index.html  # 指定文件
    python3 脚本/verify_page.py --shot out.png   # 顺便出张截图

依赖：只用 Python 标准库 + 一个本机 Chromium（自动查找，找不到会告诉你装哪个）
退出码：0 全通过 / 1 有失败
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 每一条 = (断言名, 说明为什么重要)
# 这些断言对应 2026-10-12 代码体检修掉的问题，属于"回归护栏"：
# 谁把它们改回去了，这里会立刻 FAIL。
HARNESS = r"""
<script>
(function () {
  var out = [];
  function ok(name, cond, extra) { out.push((cond ? 'PASS' : 'FAIL') + '\t' + name + (extra ? '\t' + extra : '')); }
  var svg = document.getElementById('campusMap');
  var $ = function (id) { return document.getElementById(id); };

  // ---- 护栏 1：切视角不能清空地图 class（原致命 bug） ----
  $('cbRoute').checked = true; $('cbRoute').dispatchEvent(new Event('change'));
  ok('勾选「路线」后 routes-visible 生效', svg.classList.contains('routes-visible'), svg.getAttribute('class'));
  setView('luggage');
  ok('切「拖行李」后 routes-visible 仍保留', svg.classList.contains('routes-visible'), svg.getAttribute('class'));
  ok('切视角后 view-* 正确', svg.classList.contains('view-luggage'), svg.getAttribute('class'));
  setView('wheelchair');
  ok('切「轮椅」后 routes-visible 仍保留', svg.classList.contains('routes-visible'), svg.getAttribute('class'));
  ok('切「轮椅」后 view-wheelchair 生效', svg.classList.contains('view-wheelchair'), svg.getAttribute('class'));

  // ---- 护栏 2：无障碍视角同样不能被清掉 ----
  $('cbAccess').checked = true; $('cbAccess').dispatchEvent(new Event('change'));
  setView('walker');
  ok('切视角后 mode-access 仍保留', svg.classList.contains('mode-access'), svg.getAttribute('class'));

  // ---- 护栏 3：楼层高差符号不能变回正数 ----
  ok('楼层高差条形图显示 -1层（不是 +1层）', $('valFloorA').textContent === '-1层', $('valFloorA').textContent);
  ok('楼层高差第二行显示 0层', $('valFloorB').textContent === '0层', $('valFloorB').textContent);

  // ---- 护栏 4：三视角 switch 都要存在且口径一致 ----
  ok('拖行李建议路线 B', (function(){ setView('luggage'); return $('recBadge').textContent.indexOf('B') > -1; })());
  ok('轮椅建议路线 B（合规措辞，无绝对化表述）', (function(){ setView('wheelchair'); return $('recBadge').textContent.indexOf('B') > -1; })());
  ok('轮椅路线 B 时间为 7 分钟（与 CONTEXT 一致）', (function(){ setView('wheelchair'); return $('valTimeB').textContent === '7分'; })(), (function(){ return $('valTimeB').textContent; })());
  setView('walker');

  // ---- 护栏 5：楼层高亮依赖的 id 必须存在（曾经是死代码） ----
  ok('#bld-library 存在', !!$('bld-library'));
  ok('#bld-v27 存在', !!$('bld-v27'));
  var sel = $('floorSelect');
  sel.value = 'lib-3'; sel.dispatchEvent(new Event('change'));
  ok('选楼层后 floor-active 生效', svg.classList.contains('floor-active'), svg.getAttribute('class'));
  ok('floor-active 能与 routes-visible / mode-access 共存',
     svg.classList.contains('floor-active') && svg.classList.contains('routes-visible') && svg.classList.contains('mode-access'),
     svg.getAttribute('class'));

  // ---- 护栏 6：class 只能由 applySvgClass 拼装，不能整体覆盖 ----
  ok('applySvgClass 存在（class 统一出口）', typeof applySvgClass === 'function');

  // ---- 护栏 7：数据合规——模拟数据声明与分级表不能丢 ----
  // 注意：只查 .source 区块内的文本，不能拿整页 textContent 做关键字匹配——
  // 断言脚本自己被注入在 <body> 里，字符串会把自己匹配上（假 PASS）。
  var src = document.querySelector('.source');
  var srcTxt = src ? src.textContent : '';
  ok('数据真实性分级表存在', !!document.querySelector('table.grade'));
  ok('模拟数据声明存在', srcTxt.indexOf('模拟数据声明') > -1);
  ok('分级表覆盖「示意/模拟」一行', srcTxt.indexOf('示意') > -1 && srcTxt.indexOf('非实测') > -1);

  // ---- 护栏 7b：图书馆楼层必须改成 4 层（查 tooltip 属性，不查整页文本） ----
  var lib = $('bld-library');
  ok('图书馆 tooltip 写的是 4 层', !!lib && (lib.dataset.name || '').indexOf('4 层') > -1, lib ? lib.dataset.name : '(缺失)');
  ok('图书馆标注了 data-levels=4', !!lib && lib.dataset.levels === '4', lib ? lib.dataset.levels : '(缺失)');

  // ---- 护栏 8：楼栋标注不能有空名（会弹空白浮层） ----
  ok('不存在空的 data-name', document.querySelectorAll('.bld[data-name=""]').length === 0,
     document.querySelectorAll('.bld[data-name=""]').length + ' 处');

  // ---- 护栏 9：可访问性与交互控件 ----
  ok('7 个指引点均可键盘聚焦', document.querySelectorAll('.guide-dot[tabindex="0"]').length === 7,
     document.querySelectorAll('.guide-dot[tabindex="0"]').length + ' 个');
  ok('「复位视图」按钮存在', !!$('mapReset'));
  var vp = document.querySelector('meta[name=viewport]');
  ok('viewport 未禁用用户缩放', vp && vp.content.indexOf('user-scalable=no') === -1, vp ? vp.content : '(缺失)');

  // ---- 护栏 10：湖岸线必须是卫星图参照版（不是旧的错误示意多边形，也不许虚线回归） ----
  var lake = document.querySelector('.lyr-lake');
  ok('湖岸线为实心卫星图描绘版（非虚线示意）', !!lake && !lake.getAttribute('stroke-dasharray')
     && (lake.getAttribute('d') || '').indexOf('630 495') > -1,
     lake ? ('d前缀=' + (lake.getAttribute('d') || '').slice(0, 30)) : '(缺失)');
  ok('湖标注为卫星图描绘口径', (function () {
    var texts = Array.prototype.slice.call(document.querySelectorAll('svg .lbl')).map(function (t) { return t.textContent; }).join('|');
    return texts.indexOf('参照卫星图描绘') > -1;
  })());
  ok('中心岛已移出图书馆轮廓', (function () {
    var isl = document.querySelectorAll('path[fill="#a5d6a7"]');
    return isl.length >= 1 && isl[isl.length - 1].getAttribute('d').indexOf('700 422') > -1;
  })());

  // ---- 护栏 11：滚轮不能被无条件劫持（这条在 Python 侧查源码，见 SOURCE_CHECKS） ----

  // ---- 护栏 12（P0 批次）：赛题红线——不得声称某条路线绝对安全或完全无障碍 ----
  // 注意：只查具体容器（badge / 表格 / 页脚 / .source），不查整页文本，
  // 否则断言脚本自己的字符串会把自己匹配上（假 PASS）。
  function noBanned(t) {
    return ['唯一可行', '唯一选择', '完全阻断', '轮椅友好', '全平路'].every(function (k) {
      return t.indexOf(k) === -1;
    });
  }
  ok('轮椅视角徽章无「唯一可行」', (function () {
    setView('wheelchair'); var t = $('recBadge').textContent; setView('walker'); return t.indexOf('唯一可行') === -1;
  })());
  ok('轮椅视角对比表无「全平路 / 完全阻断」', (function () {
    setView('wheelchair'); var t = $('tbody').textContent; setView('walker'); return noBanned(t);
  })());
  ok('徽章 / 对比表 / 页脚均无绝对化表述', (function () {
    var foot = document.querySelector('footer');
    return noBanned($('recBadge').textContent) && noBanned($('tbody').textContent) && (!foot || noBanned(foot.textContent));
  })());

  // ---- 护栏 13（P0 批次）：免责声明与限定语不能删 ----
  ok('「使用限制」免责声明存在', srcTxt.indexOf('使用限制') > -1 && srcTxt.indexOf('不构成') > -1 && srcTxt.indexOf('保证') > -1);
  ok('对比表附「未见台阶」限定脚注', !!document.querySelector('.table-footnote'));

  // ---- 护栏 14（P0 批次）：打开页面路线默认可见 ----
  ok('cbRoute 默认勾选', $('cbRoute').checked);
  ok('初始即 routes-visible（无需任何点击）', svg.classList.contains('routes-visible'), svg.getAttribute('class'));
  ok('地图引导提示有内容', !!$('mapHint') && $('mapHint').textContent.length > 10);

  // ---- 护栏 15（P0 批次）：命题 / 方法 / 结论区块 ----
  ok('命题/方法/结论三枚标签齐全',
     !!document.querySelector('.t-prop') && !!document.querySelector('.t-meth') && !!document.querySelector('.t-conc'));

  // ---- 护栏 16（P0 批次）：相近产品对比卡片 ----
  var cmp = document.querySelector('.cmp-table');
  ok('相近产品对比卡片存在', !!cmp);
  ok('对比覆盖 Google Maps/高德 与 Wheelmap.org',
     !!cmp && cmp.textContent.indexOf('Google Maps') > -1 && cmp.textContent.indexOf('Wheelmap') > -1 && cmp.textContent.indexOf('高德') > -1);
  ok('对比含「本作品」行且附不构成保证限定',
     !!cmp && cmp.textContent.indexOf('本作品') > -1 && cmp.textContent.indexOf('不构成无障碍通行保证') > -1);

  // ---- 护栏 17（P1 批次）：楼层接进代价模型（楼内前置） ----
  var sel2 = $('floorSelect');
  sel2.value = 'ground'; sel2.dispatchEvent(new Event('change'));
  ok('地面层无「楼内前置」行', !document.querySelector('#tbody tr.indoor-row'));
  sel2.value = 'lib-4'; sel2.dispatchEvent(new Event('change'));
  ok('选图书馆 4F 后出现「楼内前置」行', !!document.querySelector('#tbody tr.indoor-row'));
  ok('选 4F 后 note 含楼内前置提示', $('note').textContent.indexOf('楼内前置') > -1);
  ok('楼层卡片显示楼内前置（接进代价模型）', $('floorContent').textContent.indexOf('楼内前置') > -1);
  sel2.value = 'v27-5'; sel2.dispatchEvent(new Event('change'));
  ok('V27 楼层方向措辞正确（上到 5F，不是下到）', $('note').textContent.indexOf('上到 5F') > -1,
     $('note').textContent.slice(0, 50));
  sel2.value = 'ground'; sel2.dispatchEvent(new Event('change'));

  // ---- 护栏 18（P1 批次）：最后折返点指引 ----
  ok('「最后折返点」指引点存在', !!document.querySelector('.guide-dot[data-guide="turnback"]'));
  ok('「最后折返点」弹窗存在', !!document.getElementById('guide-turnback'));

  // ---- 护栏 19（P1 批次）：模型参数面板与现场核查记录 ----
  ok('「模型参数」面板存在（含可复算参数）', srcTxt.indexOf('模型参数') > -1 && srcTxt.indexOf('6 分 31 秒') > -1);
  ok('「现场核查记录」面板存在', srcTxt.indexOf('现场核查记录') > -1 && srcTxt.indexOf('绕建筑步行一周') > -1);
  ok('楼内移动系数已写进数据分级表并标注模拟', srcTxt.indexOf('楼内垂直移动') > -1);

  var pre = document.createElement('pre');
  pre.id = '__VERIFY_OUT__';
  pre.textContent = out.join('\n');
  document.body.appendChild(pre);
})();
window.addEventListener('error', function (e) {
  var p = document.getElementById('__VERIFY_OUT__');
  if (p) p.textContent += '\nFAIL\t运行期 JS 异常\t' + e.message;
});
</script>
"""

# 源码级检查（在 Python 侧做，避免断言脚本的字符串把自己匹配上造成假 PASS）
SOURCE_CHECKS = [
    ('wheel 处理器带 ⌘/Ctrl 判定（不再无条件劫持滚动）',
     lambda s: bool(re.search(r"addEventListener\(\s*'wheel'[\s\S]{0,300}?(ctrlKey|metaKey)", s))),
    ('class 只在 applySvgClass 里写一次（禁止整体覆盖）',
     lambda s: len(re.findall(r"\.setAttribute\(\s*['\"]class", s)) == 1),
    ('applySvgClass 被多处调用（renderView / renderFloor / 开关）',
     lambda s: len(re.findall(r'applySvgClass\(\)', s)) >= 5),
    ('地图 SVG 用 touch-action:none 交给 JS 接管手势',
     lambda s: bool(re.search(r'\.map-panel svg\s*\{[\s\S]{0,300}?touch-action:\s*none', s))),
    ('缩放范围有上下界夹取',
     lambda s: bool(re.search(r'Math\.max\(MIN,\s*Math\.min\(MAX', s))),
    ('两份「未命名建筑」占位不再留下空名',
     lambda s: s.count('data-name=""') == 0),

    # ---- P0 批次（2026-10-12）：赛题合规红线与默认体验 ----
    ('禁止绝对化表述（唯一可行/唯一选择/完全阻断/轮椅友好/全平路）',
     lambda s: not any(k in s for k in ['唯一可行', '唯一选择', '完全阻断', '轮椅友好', '全平路'])),
    ('「使用限制」免责声明存在（不构成无障碍通行保证）',
     lambda s: '使用限制' in s and '不构成' in s and '无障碍通行保证' in s),
    ('cbRoute 默认勾选（打开页面即可见路线）',
     lambda s: bool(re.search(r'id="cbRoute"\s+checked', s))),
    ('初始化以 checkbox 实际状态为真源（防 HTML/JS 失配）',
     lambda s: bool(re.search(r"svgState\.routes\s*=\s*document\.getElementById\('cbRoute'\)\.checked", s))),
    ('命题/方法/结论三枚标签存在（P0-3）',
     lambda s: all(k in s for k in ['t-prop', 't-meth', 't-conc'])),
    ('相近产品对比卡片存在且覆盖两款产品（P0-5）',
     lambda s: bool(re.search(r'class="cmp-table"', s)) and 'Wheelmap' in s and 'Google Maps' in s),
    ('对比表脚注限定语存在（不代表绝对安全或完全无障碍）',
     lambda s: 'table-footnote' in s and '不代表该路线绝对安全或完全无障碍' in s),

    # ---- P1 批次（2026-10-12）：楼层接进代价模型 / 折返点 / 参数面板 ----
    ('FLOOR_META 数值表存在且出入口层正确（图书馆 2F / V27 1F）',
     lambda s: bool(re.search(r"'lib-2'\s*:\s*\{\s*building:\s*'library',\s*floorNum:\s*2,\s*exitFloor:\s*2", s))
               and bool(re.search(r"'v27-1'\s*:\s*\{\s*building:\s*'v27',\s*floorNum:\s*1,\s*exitFloor:\s*1", s))),
    ('楼内移动系数三身份齐全（行人/行李/轮椅）',
     lambda s: bool(re.search(r'INDOOR_COEF\s*=\s*\{\s*walker:\s*0\.5,\s*luggage:\s*1\.0,\s*wheelchair:\s*1\.0', s))),
    ('indoorInfo 区分起点/终点语义（防方向写反）',
     lambda s: 'function indoorInfo' in s and '目标层' in s),
    ('「最后折返点」指引已接入地图',
     lambda s: 'data-guide="turnback"' in s and 'guide-turnback' in s),
    ('模型参数面板存在且标注模拟',
     lambda s: '模型参数' in s and '6 分 31 秒' in s and '经验值' in s),
    ('现场核查记录存在',
     lambda s: '现场核查记录' in s and '绕建筑步行一周' in s),

    # ---- P2 批次（2026-10-12 晚）：实测数据落地 ----
    ('实测长度 537/470 已替换估算值（300/450 不再出现）',
     lambda s: '537' in s and '470' in s and not re.search(r'约 300 m|约 450 m', s)),
    ('「台阶近路」不再作为路线称谓（叙事性引用允许，括号称谓禁止）',
     lambda s: '（台阶近路）' not in s),
    ('行人推荐反转为 B',
     lambda s: bool(re.search(r"walker:\s*\{\s*rec:\s*'B'", s))),
    ('轮椅 A 为「坡道可替代」而非不可达',
     lambda s: '坡道' in s and '旁有坡道替代' in s and '完全阻断' not in s),
    ('室内路线 C 占位说明存在',
     lambda s: '第三条候选路线' in s and '室内' in s),
    ('沿途补给信息已写入（B 最近补给偏离约 30 m）',
     lambda s: '沿途补给' in s and '最近补给偏离约 30 m' in s),

    # ---- P3 批次（2026-10-13）：室内路线 C 上图 ----
    ('路线 C 已画入地图（室内段虚线 + 户外段）',
     lambda s: 'route-C' in s and 'stroke-dasharray="9 5"' in s and '室内 1F 通道' in s),
    ('路线 C 走法结构已写入（T4 下 1 层 → T8）',
     lambda s: '电梯/楼梯下 1 层' in s.replace(' ', '') or '下 1 层' in s and 'T8' in s and 'T4' in s),
    ('路线 C 长度未编造（页面不得出现 C 的具体米数）',
     lambda s: not re.search(r'C[^<]{0,40}\d{3}\s*m', s)),

    # ---- P3b 批次（2026-10-13）：室内通道长度估算 + 电梯分时模型 ----
    ('室内路线 C 长度按坐标估算约 510 m 已标注',
     lambda s: '510 m' in s and '坐标累计估算' in s.replace(' ', '')),
    ('电梯时段切换控件存在（自动/课间/非课间）',
     lambda s: 'id="elevatorPeriod"' in s and 'value="auto"' in s and 'value="peak"' in s),
    ('电梯分时模型（>=45 分钟判课间）已实现',
     lambda s: 'getMinutes()' in s and '>= 45' in s and "'peak'" in s),
    ('电梯等候分时值写入（1 分钟 / 3–5 分钟）',
     lambda s: '3–5 分钟' in s and '约 1 分钟' in s),
]


def source_checks(src):
    out = []
    for name, fn in SOURCE_CHECKS:
        try:
            out.append(('PASS' if fn(src) else 'FAIL', name, ''))
        except Exception as e:  # 检查本身写错也要报出来，不能静默通过
            out.append(('FAIL', name, '检查执行出错: %s' % e))
    return out


# 本机 Chromium 候选路径（按优先级）
CANDIDATES = [
    os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-*/chrome-headless-shell'),
    os.path.expanduser('~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium'),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    'chromium', 'chromium-browser', 'google-chrome', 'chrome',
]


def find_browser():
    import glob
    for c in CANDIDATES:
        if any(ch in c for ch in '*/?['):
            hits = sorted(glob.glob(c))
            if hits:
                return hits[-1]
        else:
            p = shutil.which(c) if os.sep not in c else (c if os.access(c, os.X_OK) else None)
            if p:
                return p
    return None


def run(browser, url, extra=None):
    cmd = [browser, '--headless', '--disable-gpu', '--no-sandbox',
           '--hide-scrollbars', '--virtual-time-budget=5000']
    if extra:
        cmd += extra
    cmd.append(url)
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=90)


def main():
    ap = argparse.ArgumentParser(description='作品页回归测试')
    ap.add_argument('target', nargs='?', default=os.path.join(ROOT, '作品', 'index.html'))
    ap.add_argument('--shot', metavar='PNG', help='顺便把页面截图存到指定路径')
    args = ap.parse_args()

    if not os.path.exists(args.target):
        print('找不到文件：%s' % args.target, file=sys.stderr)
        return 1

    browser = find_browser()
    if not browser:
        print('未找到可用的 Chromium 内核浏览器。装一个即可：', file=sys.stderr)
        print('  方式一（推荐，Playwright 自带 headless shell）：', file=sys.stderr)
        print('    npx playwright install chromium-headless-shell', file=sys.stderr)
        print('  方式二：安装 Google Chrome', file=sys.stderr)
        return 2

    src = open(args.target, encoding='utf-8').read()
    if '</body>' not in src:
        print('文件里找不到 </body>，无法注入断言脚本。', file=sys.stderr)
        return 1
    injected = src.replace('</body>', HARNESS + '\n</body>')

    tmp_html = os.path.join(tempfile.gettempdir(), 'verify_page_injected.html')
    with open(tmp_html, 'w', encoding='utf-8') as f:
        f.write(injected)

    print('浏览器：%s' % browser)
    print('被测文件：%s' % os.path.abspath(args.target))
    print('-' * 78)

    res = run(browser, 'file://' + tmp_html, ['--dump-dom'])
    dom = res.stdout.decode('utf-8', 'replace')
    m = re.search(r'<pre id="__VERIFY_OUT__">(.*?)</pre>', dom, re.S)
    rows = []
    if m:
        rows = [r.split('\t') for r in m.group(1).strip().split('\n') if r.strip()]
    else:
        print('（页面级断言没拿到输出——可能在初始化阶段就崩了）', file=sys.stderr)
        dump = os.path.join(tempfile.gettempdir(), 'verify_page_dump.html')
        open(dump, 'w', encoding='utf-8').write(dom)
        print('（完整 DOM 已存到 %s，用浏览器打开可看控制台报错）' % dump, file=sys.stderr)

    rows += source_checks(src)

    fails = 0
    for r in rows:
        status, name = r[0], r[1]
        note = ('  ← ' + r[2]) if len(r) > 2 and status == 'FAIL' else ''
        if status == 'FAIL':
            fails += 1
        print('%s  %s%s' % ('  ✓' if status == 'PASS' else '  ✗', name, note))

    print('-' * 78)
    if not rows:
        print('没有跑出任何断言结果，视为失败。')
        return 1
    print('通过 %d / %d' % (len(rows) - fails, len(rows)))
    if fails:
        print('有 %d 条失败——请对照 文档/代码体检报告.html 里的问题清单排查。' % fails)

    if args.shot:
        r2 = run(browser, 'file://' + os.path.abspath(args.target),
                 ['--window-size=1500,1400', '--screenshot=' + os.path.abspath(args.shot)])
        if os.path.exists(args.shot):
            print('截图已保存：%s' % os.path.abspath(args.shot))

    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
