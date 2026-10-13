import re

with open('invisible-distance-prototype/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 目标：把 route-A 的 stroke-width="4" 和 "5" 统一改为 "2.5"
# 把 route-B 的 stroke-width="4" 统一改为 "2.5"
# 把 beeline 的 stroke-width="1.5" 改为 "1"

def replace_route_width(tag_html, new_width):
    # 在单个标签内替换 stroke-width
    return re.sub(r'stroke-width="[^"]+"', f'stroke-width="{new_width}"', tag_html)

lines = html.split('\n')
out_lines = []
for line in lines:
    if 'class="lyr-route route-A"' in line:
        if 'stroke-dasharray' in line:
            line = re.sub(r'stroke-width="[^"]+"', 'stroke-width="3"', line)
        else:
            line = re.sub(r'stroke-width="[^"]+"', 'stroke-width="2.5"', line)
    elif 'class="lyr-route route-B"' in line:
        line = re.sub(r'stroke-width="[^"]+"', 'stroke-width="2.5"', line)
    elif 'class="lyr-beeline"' in line:
        line = re.sub(r'stroke-width="[^"]+"', 'stroke-width="1"', line)
    out_lines.append(line)

html = '\n'.join(out_lines)

with open('invisible-distance-prototype/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('done')
# verify
for cls in ['route-A', 'route-B', 'lyr-beeline']:
    widths = set(re.findall(r'stroke-width="([^"]+)"', line) for line in html.split('\n') if cls in line)
    print(cls, 'widths:', widths)
