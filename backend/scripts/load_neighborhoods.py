import django
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/..')
ddjango.setup()
from places.models import Neighborhood, NeighborhoodEntry, Place
import pandas as pd

fl = sys.argv[1]

df = pd.read_csv(fl)

for _, row in df.iterrows():
    try:
        n = Neighborhood.objects.get(name=row['Neighborhood'])
    except Neighborhood.DoesNotExist:
        n = Neighborhood(name=row['Neighborhood'])
    lat,lng = [x.strip() for x in row['Location'].split(',')]
    n.key = n.name.lower().replace('&', 'n').replace(' ', '_').replace('/','_')
    n.lat = lat
    n.lng = lng
    n.photo_attribution = row['Attribution']
    n.save()