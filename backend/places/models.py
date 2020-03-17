import json
from django.db.models import Q
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

NEIGHBORHOOD_JS_OUTPUT_TEMPLATE = """
const Neighborhoods = %s;
export default Neighborhoods;
"""

class EmailSubscription(models.Model):
    email = models.EmailField()
    place = models.ForeignKey(to='Place', on_delete=models.CASCADE)
    sent_to_place_owner = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s to %s" % (self.email, self.place.name)

class Neighborhood(models.Model):
    name = models.TextField()
    key = models.TextField(primary_key=True)
    places = models.ManyToManyField(through='NeighborhoodEntry', to='Place')
    lat = models.FloatField()
    lng = models.FloatField()
    geom = models.PointField(srid=4326, null=True)
    photo_url = models.URLField(blank=True, null=True)
    photo_attribution = models.TextField(blank=True, null=True)

    def place_list(self, limit, offset):
        hardcoded = []
        if offset == 0:
            hardcoded = [x.place for x in NeighborhoodEntry.objects.filter(neighborhood=self).order_by('rank')]
        to_fetch = (limit - len(hardcoded)) + 1
        close_by = Place.objects.filter(
            Q(geom__distance_lt=(self.geom, D(m=2500))) & (Q(gift_card_url__isnull=False) | Q(email_contact__isnull=False))
        ).exclude(
            place_id__in=[x.place_id for x in hardcoded]
        ).annotate(
            distance=Distance('geom', self.geom)
        ).order_by('distance')[offset:offset + (limit - len(hardcoded) + 1)] 
        more_available = len(close_by) == to_fetch
        return (hardcoded + list(close_by)[0:-1]), more_available

    def to_json(self):
        return {
            "name": self.name,
            "key": self.key,
            "image": self.photo_url
        }

    @classmethod
    def dump_neighborhoods(cls, out_fl):
        # TODO this is hacky
        ranks = {
            'mission_n_bernal': 1,
            'pacific_heights': 2,
            'nopa_n_hayes_valley': 3,
            'richmond_district': 4,
            'noe_valley': 5,
        }
        def sort_key(neighborhood):
            return ranks.get(neighborhood.key, 99)
        all_hoods = sorted(cls.objects.all(), key=sort_key)
        with open(out_fl, 'w') as fl:
            output = [x.to_json() for x in all_hoods]
            fl.write(NEIGHBORHOOD_JS_OUTPUT_TEMPLATE % json.dumps(output))
    
    def save(self, *args, **kwargs):
        if (self.lat and self.lng):
            self.geom = Point([float(x) for x in (self.lat, self.lng)])
        super(self.__class__, self).save(*args, **kwargs)


class NeighborhoodEntry(models.Model):
    place = models.ForeignKey('Place', on_delete=models.CASCADE)
    neighborhood = models.ForeignKey('Neighborhood', on_delete=models.CASCADE)
    rank = models.IntegerField()

# Create your models here.
class Place(models.Model):
    name = models.TextField()
    place_id = models.TextField(primary_key=True)
    lat = models.FloatField()
    lng = models.FloatField()
    user_rating = models.FloatField()
    num_ratings = models.FloatField()
    address = models.TextField()
    email_contact = models.EmailField(null=True, blank=True)
    place_url = models.URLField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    image_attribution = models.TextField(null=True, blank=True)
    gift_card_url = models.URLField(null=True, blank=True)
    geom = models.PointField(srid=4326, null=True)

    @classmethod
    def dump_names_for_site(cls, out_fl):
        all_places = cls.objects.all()
        output = []
        for place in all_places:
            info = (
                """{{key: "{place_id}", address: "{address}", name: "{name}"}},""".format(
                    name=place.name,
                    address=place.get_short_address(),
                    place_id=place.place_id)
            )
            output.append(info)
        with open(out_fl, 'w') as fl:
            fl.writelines(output)

    @classmethod
    def dump_places_missing_photos(cls, out_fl):
        missing_photo = cls.objects.filter(image_url=None)
        names = ['%s\n' % place.place_id for place in missing_photo]
        with open(out_fl, 'w') as fl:
            fl.writelines(names)

    @classmethod
    def dump_places_missing_website(cls, out_fl):
        missing_photo = cls.objects.filter(place_url=None)
        names = ['%s\n' % place.place_id for place in missing_photo]
        with open(out_fl, 'w') as fl:
            fl.writelines(names)
        
    def get_image_url(self):
        return self.image_url or "http://TODO/placeholder"

    def get_short_address(self):
        return self.address.split(",")[0]

    def to_json(self):
        return {
            'name': self.name,
            'address': self.get_short_address(),
            'giftCardURL': self.gift_card_url,
            'placeURL': self.place_url,
            'emailContact': self.email_contact,
            'imageURL': self.get_image_url(),
            'placeID': self.place_id
        }

    def __str__(self):
        return '%s (%s)' % (self.name, self.address)

    def save(self, *args, **kwargs):
        if (self.lat and self.lng):
            self.geom = Point([float(x) for x in (self.lat, self.lng)])
        super(self.__class__, self).save(*args, **kwargs)