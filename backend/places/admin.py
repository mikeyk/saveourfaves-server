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

def accept_place(modeladmin, request, queryset):
    from places.google_places_helper import fetch_details_for_place_id
    # we listify the queryset since we're going to edit objects such that they won't appear
    # in the queryset anymore
    any_added = False
    for suggestion in list(queryset):
        place_id = suggestion.place_id
        try:
            p = Place.objects.get(place_id=place_id)
        except Place.DoesNotExist:
            any_added = True
            p = Place(place_id=place_id)

            r, photo_url, photo_attrib = fetch_details_for_place_id(place_id)
            p.name = r['name']
            p.address = r['formatted_address']
            p.image_url = photo_url
            p.user_rating = r['rating']
            p.num_ratings = r['user_ratings_total']
            p.place_url = r.get('website')
            lat, lng = r['geometry']['location']['lat'], r['geometry']['location']['lng']
            p.lat = lat
            p.lng = lng
            p.image_attribution = photo_attrib
        p.gift_card_url = suggestion.gift_card_url or p.gift_card_url
        p.email_contact = suggestion.email or p.email_contact
        p.save()
        suggestion.processed = True
        suggestion.save()
    if any_added:
        # Note: this is a fairly expensive operation, but should be ok to run
        # once at the end of an admin action
        Area.update_area_for_all_places()


class PlacesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'place_id']

class EntryAdmin(admin.ModelAdmin):
    autocomplete_fields = ['place']


class GiftCardSuggestionAdmin(admin.ModelAdmin):
    actions = [accept_link]

class PlaceSuggestionAdmin(admin.ModelAdmin):
    actions = [accept_place]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(processed=False)


# Register your models here.
admin.site.register(Place, PlacesAdmin)
admin.site.register(Neighborhood)
admin.site.register(NeighborhoodEntry, EntryAdmin)
admin.site.register(EmailSubscription)
admin.site.register(Area)
admin.site.register(SubmittedGiftCardLink, GiftCardSuggestionAdmin)
admin.site.register(SubmittedPlace, PlaceSuggestionAdmin)