import django
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/..')
django.setup()
from places.models import Neighborhood, NeighborhoodEntry, Place
import pandas as pd
fl = sys.argv[1]

Neighborhood.dump_neighborhoods(fl)