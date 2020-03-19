import json
import django
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'carebackend.settings'
sys.path.append(os.path.dirname(__file__) + '/..')
django.setup()
from places.models import Neighborhood, NeighborhoodEntry, Place, Area
import pandas as pd
out_fl = sys.argv[1]

NEIGHBORHOOD_JS_OUTPUT_TEMPLATE = """
const Neighborhoods = %s;
export default Neighborhoods;
"""

def sort_key(neighborhood):
    return neighborhood.rank or 99

with open(out_fl, 'w') as fl:
    all_output = {}
    for area in Area.objects.all():
        matching_hoods = sorted(Neighborhood.objects.filter(area=area), key=sort_key)
        output = [x.to_json() for x in matching_hoods]
        all_output[area.key] = output
    fl.write(NEIGHBORHOOD_JS_OUTPUT_TEMPLATE % json.dumps(all_output))