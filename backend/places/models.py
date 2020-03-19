import json
from django.db.models import Q
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

class EmailSubscription(models.Model):
    email = models.EmailField()
    place = models.ForeignKey(to='Place', on_delete=models.CASCADE)
    sent_to_place_owner = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s to %s" % (self.email, self.place.name)

class SubmittedGiftCardLink(models.Model):

    link = models.URLField()
    place = models.ForeignKey(to='Place', on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s to %s" % (self.link, self.place.name)
    

class Neighborhood(models.Model):
    name = models.TextField()
    key = models.TextField(primary_key=True)
    places = models.ManyToManyField(through='NeighborhoodEntry', to='Place')
    lat = models.FloatField()
    lng = models.FloatField()
    geom = models.PointField(srid=4326, null=True)
    bounds = models.PolygonField(srid=4326, null=True, blank=True)
    photo_url = models.URLField(blank=True, null=True)
    photo_attribution = models.TextField(blank=True, null=True)
    area = models.ForeignKey(to='Area', on_delete=models.SET_NULL, blank=True, null=True)

    def place_list(self, limit, offset):
        hardcoded = []
        if offset == 0:
            hardcoded = [x.place for x in NeighborhoodEntry.objects.filter(neighborhood=self).order_by('rank')]
        to_fetch = (limit - len(hardcoded)) + 1
        if self.bounds:
            close_by = Place.objects.filter(
                Q(geom__within=self.bounds)
            ).annotate(
                has_card=models.Count('gift_card_url')
            ).exclude(
                place_id__in=[x.place_id for x in hardcoded]
            ).order_by('-has_card', '-num_ratings')[offset:offset + (limit - len(hardcoded) + 1)]
        else:
            close_by = Place.objects.filter(
                Q(geom__distance_lt=(self.geom, D(m=2500))) & (Q(gift_card_url__isnull=False) | Q(email_contact__isnull=False))
            ).exclude(
                place_id__in=[x.place_id for x in hardcoded]
            ).annotate(
                distance=Distance('geom', self.geom)
            ).order_by('distance')[offset:offset + (limit - len(hardcoded) + 1)] 
        more_available = len(close_by) == to_fetch
        joined = (hardcoded + list(close_by))
        end_list = -1 if more_available else len(joined)
        return joined[0:end_list], more_available

    def to_json(self):
        return {
            "name": self.name,
            "key": self.key,
            "image": self.photo_url
        }
    
    def save(self, *args, **kwargs):
        if (self.lat and self.lng):
            self.geom = Point([float(x) for x in (self.lng, self.lat)], srid=4326)

        super(self.__class__, self).save(*args, **kwargs)


class NeighborhoodEntry(models.Model):
    place = models.ForeignKey('Place', on_delete=models.CASCADE)
    neighborhood = models.ForeignKey('Neighborhood', on_delete=models.CASCADE)
    rank = models.IntegerField()


class Area(models.Model):
    key = models.TextField(primary_key=True)
    display_name = models.TextField()

# Create your models here.
class Place(models.Model):
    name = models.TextField()
    place_id = models.TextField(primary_key=True)
    lat = models.FloatField()
    lng = models.FloatField()
    user_rating = models.FloatField()
    num_ratings = models.FloatField()
    address = models.TextField()
    area = models.ForeignKey(to='Area', null=True, blank=True, on_delete=models.SET_NULL)
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
        return self.address.split(', CA')[0]

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

    def to_typeahead_json(self):
        return {
            'name': self.name,
            'address': self.get_short_address(),
            'key': self.place_id,
            'image_attribution': self.image_attribution
        }

    def __str__(self):
        return '%s (%s)' % (self.name, self.address)

    def save(self, *args, **kwargs):
        if (self.lat and self.lng):
            self.geom = Point([float(x) for x in (self.lng, self.lat)], srid=4326)
        super(self.__class__, self).save(*args, **kwargs)