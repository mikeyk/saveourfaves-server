from django.conf import settings
from places.models import Place
import requests

PLACES_API_ROOT = "https://maps.googleapis.com/maps/api/place"

PLACES_DETAILS_URL = "{ROOT_URL}/details/json?inputtype=textquery&key={key}&place_id={place_id}&fields={fields}"
PLACES_PHOTO_URL = "{ROOT_URL}/photo?key={key}&photoreference={photo_ref}&maxwidth={width}"
FETCH_FIELDS = "photo,website,formatted_address,geometry,permanently_closed,type,name,rating,user_ratings_total"


def fetch_photo_redirect(photo_ref):
    photo_url = PLACES_PHOTO_URL.format(
        ROOT_URL=PLACES_API_ROOT,
        key=settings.GOOGLE_PLACES_API_KEY,
        photo_ref=photo_ref,
        width=800
    )
    photo_req = requests.get(photo_url, allow_redirects=False)
    redirect = photo_req.headers.get("Location")
    return redirect or None


def fetch_details_for_place_id(place_id):
    full_url = PLACES_DETAILS_URL.format(
        ROOT_URL=PLACES_API_ROOT,
        key=settings.GOOGLE_PLACES_API_KEY,
        place_id=place_id,
        fields=FETCH_FIELDS)
    resp = requests.get(full_url)
    data = resp.json()
    if not 'result' in data:
        return {}, None, None
    r = data['result']
    photo_url = None
    photo_attrib = None
    if r.get('photos'):
        first_photo = r['photos'][0]
        photo_attrib = first_photo['html_attributions']
        photo_ref = first_photo['photo_reference']
        photo_url = fetch_photo_redirect(photo_ref)
    return r, photo_url, photo_attrib
