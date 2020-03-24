from django.contrib import admin
from django.utils.html import format_html
from places.helper import check_link_against_blacklist
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
        if check_link_against_blacklist(suggestion.link):
            pl = suggestion.place
            pl.gift_card_url = suggestion.link
            pl.save()
    queryset.delete()
accept_link.short_description = "Accept suggested link"

def accept_place_reject_link(modeladmin, request, queryset):
    return accept_place(modeladmin, request, queryset, accept_link=False)
accept_place_reject_link.short_description = "Add place, but don't add the gift card link"

def accept_place(modeladmin, request, queryset, accept_link=True):
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
            if not r.get('rating'):  # probably not meaningful place
                suggestion.processed = True
                suggestion.save()
                continue
            p.name = r['name']
            p.address = r['formatted_address']
            p.image_url = photo_url
            p.user_rating = r['rating']
            p.num_ratings = r['user_ratings_total']
            p.place_types = ','.join(r.get('types', []))
            p.place_url = r.get('website')
            lat, lng = r['geometry']['location']['lat'], r['geometry']['location']['lng']
            p.lat = lat
            p.lng = lng
            p.image_attribution = photo_attrib
        if accept_link:
            p.gift_card_url = check_link_against_blacklist(suggestion.gift_card_url) or p.gift_card_url
        p.email_contact = suggestion.email or p.email_contact
        p.save()
        suggestion.processed = True
        suggestion.save()
    if any_added:
        # Note: this is a fairly expensive operation, but should be ok to run
        # once at the end of an admin action
        Area.update_area_for_all_places()

accept_place.short_description = "Add place, including any gift card link"

class PlacesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'place_id']

class EntryAdmin(admin.ModelAdmin):
    autocomplete_fields = ['place']


class GiftCardSuggestionAdmin(admin.ModelAdmin):
    actions = [accept_link]
    list_display = ('place', 'show_gift_card_url', 'date_submitted')

    def show_gift_card_url(self, obj):
        if obj.link:
            return format_html("<a target='_blank' href='{url}'>{url}</a>", url=obj.link)
        return None
    show_gift_card_url.admin_order_field = 'link'

class PlaceSuggestionAdmin(admin.ModelAdmin):
    actions = [accept_place, accept_place_reject_link]

    list_display = ('place_name', 'place_rough_location', 'show_gift_card_url', 'email', 'date_submitted')

    def show_gift_card_url(self, obj):
        if obj.gift_card_url:
            return format_html("<a target='_blank' href='{url}'>{url}</a>", url=obj.gift_card_url)
        return None
    show_gift_card_url.admin_order_field = 'gift_card_url'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(processed=False)

class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'place', 'show_place_email')
    def show_place_email(self, obj):
        return obj.place.email_contact
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(processed=False)


# Register your models here.
admin.site.register(Place, PlacesAdmin)
admin.site.register(Neighborhood)
admin.site.register(NeighborhoodEntry, EntryAdmin)
admin.site.register(EmailSubscription, EmailSubscriptionAdmin)
admin.site.register(Area)
admin.site.register(SubmittedGiftCardLink, GiftCardSuggestionAdmin)
admin.site.register(SubmittedPlace, PlaceSuggestionAdmin)