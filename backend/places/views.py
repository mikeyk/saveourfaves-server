import json
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt


# from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from places.models import (
    EmailSubscription,
    Neighborhood,
    Place,
    SubmittedGiftCardLink,
    SubmittedPlace
)

@csrf_protect
def neighborhood_detail(request):
    neighborhood_key = request.GET.get('neighborhood')
    offset = int(request.GET.get('offset', 0))
    if not neighborhood_key:
        return JsonResponse({'error': 'missing neighborhood'})
    try:
        neighborhood = Neighborhood.objects.get(key=neighborhood_key)
    except Neighborhood.DoesNotExist:
        return JsonResponse({'error': 'can\'t find neighborhood'})

    place_list, more_available = neighborhood.place_list(limit=9, offset=offset)
    return JsonResponse({
        'suggestedPlaces': [x.to_json() for x in place_list],
        'moreAvailable': more_available
    })

@csrf_protect
def place_detail(request):
    place_id = request.GET.get('place_id')
    if not place_id:
        return JsonResponse({'error': 'missing place ID'})
    try:
        place = Place.objects.get(place_id=place_id)
    except Place.DoesNotExist:
        return JsonResponse({'error': 'can\'t find place with that ID'})

    nearby = []
    if place.geom:
        nearby = Place.objects.filter(
                Q(geom__distance_lt=(place.geom, D(m=2500))) & (Q(gift_card_url__isnull=False) | Q(email_contact__isnull=False))
            ).exclude(
                place_id=place_id
            ).annotate(
                distance=Distance('geom', place.geom)
            ).order_by('distance')[0:9]

    return JsonResponse({'place': place.to_json(), 'suggestedPlaces': [x.to_json() for x in nearby]})

@csrf_exempt
def submit_email_for_place(request):
    data = json.loads(request.body)
    place_id = data.get('place_id')
    email = data.get('email')
    if not (place_id and email):
        return JsonResponse({'error': 'missing parameters'}, status=400)

    try:
        place = Place.objects.get(place_id=place_id)
    except Place.DoesNotExist:
        return JsonResponse({'error': 'bad place ID'}, status=400)
    try:
        subscription = EmailSubscription.objects.get(
            email=email,
            place=place
        )
    except EmailSubscription.DoesNotExist:
        subscription = EmailSubscription(
            email=email,
            place=place
        )
        try:
            subscription.full_clean()
        except ValidationError:
            return JsonResponse({'error': 'bad email'}, status=400)
        subscription.save()
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def submit_gift_card_link(request):
    data = json.loads(request.body)
    place_id = data.get('place_id')
    gift_card_url = data.get('gift_card_url')
    if not (place_id and gift_card_url):
        return JsonResponse({'error': 'missing parameters'}, status=400)

    try:
        URLValidator()(gift_card_url)
    except ValidationError:
        return JsonResponse({'error': 'bad url'}, status=400)
    try:
        place = Place.objects.get(place_id=place_id)
    except Place.DoesNotExist:
        return JsonResponse({'error': 'bad place ID'}, status=400)
    submission = SubmittedGiftCardLink.objects.create(
        link=gift_card_url,
        place=place
    )
    submission.save()
    return JsonResponse({'status': 'ok'})

@csrf_exempt
def submit_new_place(request):
    data = json.loads(request.body)
    gift_card_url = data.get('gift_card_url')
    donation_url = data.get('donation_url')
    email = data.get('email')
    if not (data.get('place_details')):
        return JsonResponse({'error': 'missing parameters'}, status=400)

    # Hacky way if people enter incomplete URLs
    def add_url_prefix(url):
        if url and not url.startswith('http'):
            return 'http://%s/' % url
        return url
    gift_card_url = add_url_prefix(gift_card_url)
    donation_url = add_url_prefix(donation_url)

    place_data = data['place_details']
    try:
        URLValidator()(gift_card_url) if gift_card_url else None
    except ValidationError:
        return JsonResponse({'error': "Gift card link isn't valid"}, status=400)

    sub = SubmittedPlace(
        place_id=place_data['place_id'],
        place_name=place_data['structured_formatting']['main_text'],
        place_rough_location=place_data['structured_formatting']['secondary_text'],
        email=email,
        donation_url=donation_url,
        gift_card_url=gift_card_url
    )
    sub.save()
    return JsonResponse({'status': 'ok'})