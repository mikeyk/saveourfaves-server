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

area = Area.objects.get(key=area_to_use)

df = pd.read_csv(fl)

for _, row in df.iterrows():
    print("Processing", row['Neighborhood'])
    try:
        n = Neighborhood.objects.get(name=row['Neighborhood'])
    except Neighborhood.DoesNotExist:
        n = Neighborhood(name=row['Neighborhood'])
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
    n.key = n.name.lower().replace('&', 'n').replace(' ', '_').replace('/','_')
    n.lat = lat
    n.lng = lng
    n.area = area
    n.save()