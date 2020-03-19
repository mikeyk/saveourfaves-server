import json
import django
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'carebackend.settings'
sys.path.append(os.path.dirname(__file__) + '/..')
django.setup()
from places.models import Neighborhood, NeighborhoodEntry, Place, Area
from django.contrib.gis.geos import Polygon
import pandas as pd
from shapely.geometry import Polygon as ShapelyPolygon

fl = sys.argv[1]
area_to_use = sys.argv[2]

insert_if_not_found = sys.argv[3] == 'yes' if len(sys.argv) > 3 else False
area = Area.objects.get(key=area_to_use)

df = pd.read_csv(fl)

for _, row in df.iterrows():
    print("Processing", row['Neighborhood'])
    try:
        n = Neighborhood.objects.get(key=row['DB Key'])
    except Neighborhood.DoesNotExist:
        if insert_if_not_found:
            n = Neighborhood(name=row['Neighborhood'])
            n.key = row['DB Key']
        else:
            print("No DB Key match and not inserting, continuing...")
            continue
    if row['GeoJSON'] and not pd.isna(row['GeoJSON']):
        if row['GeoJSON'].startswith('[[['):
            row['GeoJSON'] = row['GeoJSON'][1:-1]
        if not row['GeoJSON'].startswith('[['):
            row['GeoJSON'] = '[%s]' % row['GeoJSON']
        geo_json = json.loads(row['GeoJSON'])
        n.bounds = Polygon(geo_json)
        poly = ShapelyPolygon(geo_json)
        centroid = poly.centroid
        lat = centroid.y
        lng = centroid.x
    elif row.get('Location'):
        lat,lng = [x.strip() for x in row['Location'].split(',')]
    else:
        print("missing necessary data!")
        continue
    n.lat = lat
    n.lng = lng
    n.area = area
    n.rank = row.get('Rank') if not pd.isna(row.get('Rank')) else None
    n.save()