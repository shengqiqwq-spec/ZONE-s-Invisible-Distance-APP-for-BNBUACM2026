import urllib.request, urllib.parse, json

# 一期校园 bbox（稍外扩）
BBOX = '22.347,113.509,22.358,113.521'
query = f'''[out:json][timeout:180];
(
  way["building"]({BBOX});
  way["highway"]({BBOX});
  way["natural"="water"]({BBOX});
  way["waterway"]({BBOX});
  way["leisure"~"pitch|track|sports_centre|garden|park|playground"]({BBOX});
  nwr["railway"="station"]({BBOX});
  nwr["barrier"="gate"]({BBOX});
  nwr["entrance"]({BBOX});
);
out tags geom;
'''
data = urllib.parse.urlencode({'data': query}).encode()
req = urllib.request.Request(
    'https://overpass-api.de/api/interpreter',
    data=data,
    headers={'User-Agent': 'WorkBuddy-Map/1.0', 'Accept': 'application/json'}
)
with urllib.request.urlopen(req, timeout=240) as r:
    osm = json.loads(r.read().decode('utf-8'))

elements = osm.get('elements', [])
print('total elements:', len(elements))

buildings, roads, waters, pitches, gates = [], [], [], [], []
for e in elements:
    tags = e.get('tags', {})
    geom = e.get('geometry') or []
    center = e.get('center') or {}
    item = {
        'id': e.get('id'), 'type': e.get('type'), 'tags': tags,
        'geom': [[p.get('lat'), p.get('lon')] for p in geom if p.get('lat') is not None],
        'center': [center.get('lat'), center.get('lon')],
    }
    if 'building' in tags:
        buildings.append(item)
    elif 'highway' in tags:
        roads.append(item)
    elif tags.get('natural') == 'water' or 'waterway' in tags:
        waters.append(item)
    elif 'leisure' in tags:
        pitches.append(item)
    elif tags.get('barrier') == 'gate' or 'entrance' in tags:
        gates.append(item)

print('buildings:', len(buildings), 'roads:', len(roads), 'waters:', len(waters), 'pitches:', len(pitches), 'gates:', len(gates))
json.dump({'buildings': buildings, 'roads': roads, 'waters': waters, 'pitches': pitches, 'gates': gates},
          open('bnbu-campus-map/osm_full.json', 'w', encoding='utf-8'), ensure_ascii=False)

# 打印有名字的 building + 楼层信息
for b in buildings:
    t = b['tags']
    name = t.get('name') or t.get('name:en')
    if name:
        print(name, '| levels:', t.get('building:levels'), '| building:', t.get('building'), '| amenity:', t.get('amenity'))
