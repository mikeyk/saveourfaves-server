from collections import defaultdict
import django
import csv
import sys
import os
import json
os.environ['DJANGO_SETTINGS_MODULE'] = 'carebackend.settings'
sys.path.append(os.path.dirname(__file__) + '/..')
django.setup()
from places.models import EmailSubscription

outfl = sys.argv[1]

by_place = defaultdict(list)
for sub in EmailSubscription.objects.filter(processed=False, place__email_contact__isnull=True, place__gift_card_url__isnull=True):
    by_place[sub.place.place_id].append(sub)

by_place_items = sorted(by_place.items(), key=lambda x: len(x[1]), reverse=True)
with open(outfl, 'w') as fl:
    writer = csv.DictWriter(fl, fieldnames=['place_id', 'Place', 'Place Email', 'Website', 'Count', 'Emails', 'Gift Card URL'])
    writer.writeheader()
    for place_id, items in by_place_items:
        place = items[0].place
        writer.writerow({
            'place_id': place.place_id,
            'Place': place.name,
            'Place Email': place.email_contact,
            'Website': place.place_url,
            'Count': len(items),
            'Emails': '; '.join([x.email for x in items]),
            'Gift Card URL': place.gift_card_url
        })