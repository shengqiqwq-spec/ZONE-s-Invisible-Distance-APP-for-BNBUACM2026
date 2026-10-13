import json
data = json.load(open('bnbu-campus-map/osm_full.json', encoding='utf-8'))

LIB = (22.352488, 113.515779)   # 学习资源中心
V27 = (22.353508, 113.512679)   # 雨果楼

# 路线走廊 bbox（两栋楼之间，稍放大）
la0, la1 = 22.3518, 22.3543
lo0, lo1 = 113.5120, 113.5165

def pts_of(el):
    return [[p['lat'], p['lon']] for p in el.get('geometry', []) if p.get('lat') is not None]

def mid(el):
    p = pts_of(el)
    if not p: return None
    return sum(x[0] for x in p)/len(p), sum(x[1] for x in p)/len(p)

def inbox(la, lo):
    return la0 <= la <= la1 and lo0 <= lo <= lo1

print('=== 走廊内 building ===')
for el in data['buildings']:
    m = mid(el)
    if m and inbox(*m):
        t = el['tags']
        print('  ', t.get('name',''), '| levels:', t.get('building:levels'), '|', t.get('building'))

print('=== 走廊内 steps（台阶）===')
for el in data.get('footpaths', []):
    t = el['tags']
    if t.get('highway') != 'steps':
        continue
    m = mid(el)
    if m and inbox(*m):
        p = pts_of(el)
        print('  steps 点数', len(p), '| 中心', [round(x,5) for x in m], '|', t.get('name',''), t.get('incline',''))

print('=== 走廊内 footway/path ===')
for el in data.get('footpaths', []):
    t = el['tags']
    if t.get('highway') in ('footway','path'):
        m = mid(el)
        if m and inbox(*m):
            print('  ', t.get('highway'), '点数', len(pts_of(el)), '| 中心', [round(x,5) for x in m])

print('=== 走廊内 主路 road ===')
for el in data.get('roads', []):
    m = mid(el)
    if m and inbox(*m):
        t = el['tags']
        print('  ', t.get('highway'), '点数', len(pts_of(el)), '| 中心', [round(x,5) for x in m], '|', t.get('name',''))

print('=== 图书馆 & V27 精确中心 ===')
for el in data['buildings']:
    t = el['tags']
    if '学习资源' in (t.get('name','')) or 'V27' in (t.get('name','')):
        print('  ', t.get('name'), mid(el))
