from django.contrib import admin
from places.models import (
    Place, 
    NeighborhoodEntry, 
    Neighborhood, 
    EmailSubscription, 
    Area,
    SubmittedPlace,
    SubmittedGiftCardLink)



def accept_link(modeladmin, request, queryset):
    for suggestion in queryset:
        pl = suggestion.place
        pl.gift_card_url = suggestion.link
        pl.save()
    queryset.delete()
accept_link.short_description = "Accept suggested link"

class PlacesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'place_id']

class EntryAdmin(admin.ModelAdmin):
    autocomplete_fields = ['place']


class GiftCardSuggestionAdmin(admin.ModelAdmin):
    actions = [accept_link]



# Register your models here.
admin.site.register(Place, PlacesAdmin)
admin.site.register(Neighborhood)
admin.site.register(NeighborhoodEntry, EntryAdmin)
admin.site.register(EmailSubscription)
admin.site.register(Area)
admin.site.register(SubmittedGiftCardLink, GiftCardSuggestionAdmin)
admin.site.register(SubmittedPlace)