import django
django.setup()
from places.models import Neighborhood, NeighborhoodEntry, Place
import pandas as pd
import sys
fl = sys.argv[1]

Neighborhood.dump_neighborhoods(fl)