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
        if not p.email_contact:
            p.email_contact = row['email_1']
            p.save()
        else:
            print("Not saving because I already had an email", p.name)
    except Place.DoesNotExist:
        print("ERROR! Adding an email to a place we don't have")
        continue