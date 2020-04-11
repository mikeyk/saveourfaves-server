from collections import defaultdict
import django
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'carebackend.settings'
sys.path.append(os.path.dirname(__file__) + '/..')
django.setup()

from django.db.models import Q
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core import mail

from places.models import EmailSubscription

really_send = len(sys.argv) > 1 and (sys.argv[1] == "send")

if len(sys.argv) > 2:
    limit = int(sys.argv[2])
else:
    limit = 1

subs = EmailSubscription.objects.filter(
    processed=False,
    place__gift_card_url__isnull=True,
    place__email_contact__isnull=True
).exclude(
    (Q(place__phone_number__isnull=True) & Q(place__email_contact__isnull=True))
)[0:limit]

with mail.get_connection() as connection:
    for sub in subs:
        place = sub.place
        if not (place.phone_number or place.email_contact or place.place_url):
            print("Skipping", place.name, "because we have no contact info")
            continue
        place_name = place.name
        phone_number = place.phone_number
        website_plain = ", or visit them at:\n%s" % place.place_url if place.place_url else "."
        phone_number_html = "<a href='tel:{phone}'>{phone}</a>".format(phone=place.phone_number) if place.phone_number else ""
        website_html = ", or <a href='%s'>visit their site</a>." % place.place_url if place.place_url else "."
        to_address = sub.email

        plain_email_body = f"""
Hi there from the SaveOurFaves.org team! You recently told us you were interested in buying a gift card to support {place_name}. Unfortunately, we still don’t have a gift card link for them, but there’s a good chance they can sell you one over the phone that you can pick up when they reopen.

You can call them at {phone_number}{website_plain}

Not sure how much to spend? Consider a gift card for one month’s worth of spending, if you’re able. Thank you for doing your part to keep our local businesses around. We hope you are safe and healthy.

Cheers,
The Save Our Faves Team

P.S. If you find out that they do have a gift card link, you can add it to our site here: https://saveourfaves.org/addplace
"""
        html_email_body = f"""
<p>Hi there from the SaveOurFaves.org team! You recently told us you were interested in buying a gift card to support {place_name}. Unfortunately, we still don’t have a gift card link for them, but there’s a good chance they can sell you one over the phone that you can pick up when they reopen.</p>

<p>You can call them at {phone_number_html}{website_html}</p>

<p>Not sure how much to spend? Consider a gift card for one month’s worth of spending, if you’re able. Thank you for doing your part to keep our local businesses around. We hope you are safe and healthy.</p>

<p>Cheers,<br />
The Save Our Faves Team</p>

<p>P.S. If you find out that they do have a gift card link, you can <a href="https://saveourfaves.org/addplace">add it to our site</a>.</p>.
        """
        if not really_send:
            print("Would have sent to", to_address, place_name, plain_email_body, html_email_body)
            continue
        message = EmailMultiAlternatives(
            subject=f"Still want to support {place_name}?",
            body=plain_email_body,
            from_email="SaveOurFaves Team <info@saveourfaves.org>",
            to=[to_address],
            connection=connection,
        )
        message.attach_alternative(html_email_body, 'text/html')
        message.send()
        print("Sent email to", place_name, to_address)
        sub.processed = True
        sub.save()