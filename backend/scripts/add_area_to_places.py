import django
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'carebackend.settings'
sys.path.append(os.path.dirname(__file__) + '/..')
django.setup()
from django.contrib.gis.measure import D
from places.models import Neighborhood, Place, Area

Area.update_area_for_all_places()