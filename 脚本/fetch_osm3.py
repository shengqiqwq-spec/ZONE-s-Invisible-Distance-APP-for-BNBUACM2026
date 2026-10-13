import urllib.request, urllib.parse, json, time

BBOX = '22.347,113.509,22.358,113.521'
ENDPOINTS = [
    'https://overpass-api.de/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
    'https://overpass.private.coffee/api/interpreter',
]

def run(query, name):
    data = urllib.parse.urlencode({'data': query}).encode()
    for attempt in range(2):
        for ep in ENDPOINTS:
            try:
                req = urllib.request.Request(ep, data=data, headers={
                    'User-Agent': 'WorkBuddy-Map/1.0', 'Accept': 'application/json'})
                with urllib.request.urlopen(req, timeout=180) as r:
                    res = json.loads(r.read().decode('utf-8'))
                print(f'{name}: OK via {ep} ({len(res.get("elements", []))} elements)')
                return res
            except Exception as ex:
                print(f'{name}: fail {ep} {repr(ex)[:80]}')
        time.sleep(3)
    return None

q_bld = f'''[out:json][timeout:120];way["building"]({BBOX});out tags geom;'''
q_road = f'''[out:json][timeout:120];way["highway"~"^(primary|secondary|tertiary|residential|unclassified|pedestrian|living_street)$"]({BBOX});out tags geom;'''
q_foot = f'''[out:json][timeout:120];way["highway"~"^(footway|path|steps|service|cycleway)$"]({BBOX});out tags geom;'''
q_misc = f'''[out:json][timeout:120];(way["natural"="water"]({BBOX});way["waterway"]({BBOX});way["leisure"]({BBOX});nwr["barrier"="gate"]({BBOX});nwr["entrance"]({BBOX}););out tags geom;'''

res_bld = run(q_bld, 'buildings')
res_road = run(q_road, 'roads')
res_foot = run(q_foot, 'footpaths')
res_misc = run(q_misc, 'misc')

out = {'buildings': [], 'roads': [], 'footpaths': [], 'misc': []}
for key, res in [('buildings', res_bld), ('roads', res_road), ('footpaths', res_foot), ('misc', res_misc)]:
    if res:
        out[key] = res.get('elements', [])

json.dump(out, open('bnbu-campus-map/osm_full.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('saved. counts:', {k: len(v) for k, v in out.items()})

# 汇总有名字的楼 + 楼层
for b in out['buildings']:
    t = b.get('tags', {})
    name = t.get('name') or t.get('name:en')
    if name:
        print(name, '| levels:', t.get('building:levels'), '|', t.get('building'))
