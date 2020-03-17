import django
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/..')
print(sys.path)
django.setup()
from places.models import Place
import pandas as pd
import sys

fl = sys.argv[1]

df = pd.read_csv(fl)

for _, row in df.iterrows():
    try:
        p = Place.objects.get(place_id=row['place_id'])
    except Place.DoesNotExist:
        p = Place(
            place_id=row['place_id'])
    
    p.lat = row['lat']
    p.lng = row['lng']
    p.address = row['formatted_address']
    p.user_rating = row['rating']
    p.name = row['name']
    p.num_ratings = row['user_ratings_total']
    p.photo_attribution = row['image_attribution']
    p.image_url = row['photo_url']
    p.save()