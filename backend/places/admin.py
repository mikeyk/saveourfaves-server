from django.contrib import admin
from places.models import Place, NeighborhoodEntry, Neighborhood, EmailSubscription


class PlacesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'place_id']

class EntryAdmin(admin.ModelAdmin):
    autocomplete_fields = ['place']

# Register your models here.
admin.site.register(Place, PlacesAdmin)
admin.site.register(Neighborhood)
admin.site.register(NeighborhoodEntry, EntryAdmin)
admin.site.register(EmailSubscription)