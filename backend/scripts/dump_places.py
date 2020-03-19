import django
import sys
import os
import json
os.environ['DJANGO_SETTINGS_MODULE'] = 'carebackend.settings'
sys.path.append(os.path.dirname(__file__) + '/..')
django.setup()
from places.models import Place
import pandas as pd
fl = sys.argv[1]

all_places = Place.objects.all()
all_json = [p.to_typeahead_json() for p in all_places]

template = """

const SFPlaces = 
%s;
export default SFPlaces;
""" 

with open(fl, 'w') as out:
    out.write(template % json.dumps(all_json))
