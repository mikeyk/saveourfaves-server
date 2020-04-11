import django
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'carebackend.settings'
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
        print("Couldn't find matching place", row['place_id'])
        continue

    p.phone_number = p.phone_number or row['phone_number']
    p.place_url = p.place_url or row['website']
    try:
        p.save()
    except Exception as e:
        print(e)
        continue