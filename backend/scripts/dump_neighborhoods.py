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

# TODO this is hacky
ranks = {
    'mission_n_bernal': 1,
    'pacific_heights': 2,
    'north_beach_n_jackson_sq': 3,
    'nopa_n_hayes_valley': 4,
    'richmond_district': 5,
    'noe_valley': 5,
}
def sort_key(neighborhood):
    return ranks.get(neighborhood.key, 99)
with open(out_fl, 'w') as fl:
    all_output = {}
    for area in Area.objects.all():
        output = [x.to_json() for x in Neighborhood.objects.filter(area=area)]
        all_output[area.key] = output
    fl.write(NEIGHBORHOOD_JS_OUTPUT_TEMPLATE % json.dumps(all_output))