import urllib.request, urllib.parse, json, sys, io

# 1) OSM Overpass: 校区 relation 18704403 内所有有名字的 building
# 一期校园中心 113.515419,22.352732，bbox 略放大覆盖全校
query = '''[out:json][timeout:120];
(
  way["building"](22.343,113.503,22.363,113.528);
  relation["building"](22.343,113.503,22.363,113.528);
);
out center tags;
'''
data = urllib.parse.urlencode({'data': query}).encode()
req = urllib.request.Request(
    'https://overpass-api.de/api/interpreter',
    data=data,
    headers={'User-Agent': 'WorkBuddy-Map/1.0', 'Accept': 'application/json'}
)
try:
    with urllib.request.urlopen(req, timeout=180) as r:
        osm = json.loads(r.read().decode('utf-8'))
    elements = osm.get('elements', [])
    print('OSM elements:', len(elements))
    out = []
    for e in elements:
        if e.get('type') == 'way':
            tags = e.get('tags', {})
            name = tags.get('name') or tags.get('name:zh') or tags.get('name:en')
            if not name:
                continue
            lat = e.get('center', {}).get('lat')
            lon = e.get('center', {}).get('lon')
            out.append({
                'osm_id': e.get('id'),
                'name': name,
                'name_zh': tags.get('name:zh'),
                'name_en': tags.get('name:en'),
                'building': tags.get('building'),
                'amenity': tags.get('amenity'),
                'lat': lat, 'lon': lon,
            })
    with open('bnbu-campus-map/osm_buildings.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    for o in out:
        print(o['name'], '| zh:', o.get('name_zh'), '| en:', o.get('name_en'), '| building:', o.get('building'), '|', round(o['lon'],6), round(o['lat'],6))
except Exception as ex:
    print('OVERPASS ERROR:', repr(ex))
