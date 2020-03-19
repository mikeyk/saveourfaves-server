from django.contrib import admin
from places.models import (
    Place, 
    NeighborhoodEntry, 
    Neighborhood, 
    EmailSubscription, 
    Area,
    SubmittedGiftCardLink)



class PlacesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'place_id']

class EntryAdmin(admin.ModelAdmin):
    autocomplete_fields = ['place']

# Register your models here.
admin.site.register(Place, PlacesAdmin)
admin.site.register(Neighborhood)
admin.site.register(NeighborhoodEntry, EntryAdmin)
admin.site.register(EmailSubscription)
admin.site.register(Area)
admin.site.register(SubmittedGiftCardLink)