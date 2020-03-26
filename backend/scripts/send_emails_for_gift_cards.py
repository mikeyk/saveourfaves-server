from collections import defaultdict
import django
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'carebackend.settings'
sys.path.append(os.path.dirname(__file__) + '/..')
django.setup()
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core import mail

from places.models import EmailSubscription

really_send = len(sys.argv) > 1 and (sys.argv[1] == "send")

if len(sys.argv) > 2:
    limit = int(sys.argv[2])
else:
    limit = 1

by_place = defaultdict(list)
for sub in EmailSubscription.objects.filter(
    processed=False,
    place__gift_card_url__isnull=True,
    place__email_contact__isnull=False
):
    by_place[sub.place.place_id].append(sub)

by_place_items = sorted(by_place.items(), key=lambda x: len(x[1]), reverse=True)

subs = EmailSubscription.objects.filter(
    processed=False,
    place__gift_card_url__isnull=False
)[0:limit]

with mail.get_connection() as connection:
    for sub in subs:
        place = sub.place
        if not place.gift_card_url:
            print("Skipping", place.name, "because we somehow don't have a gift card URL for it")
            continue
        place_name = place.name
        gift_card_url = place.gift_card_url
        to_address = sub.email

        plain_email_body = f"""
Hi there from the SaveOurFaves.org team! You recently told us you were interested in buying a gift card to support {place_name}. They now have a link where you can do this online:

{gift_card_url}

Not sure how much to spend? Consider a gift card for one month’s worth of your usual spending there, if you’re able. Thank you for doing your part to keep our local businesses around. We hope you are safe and healthy.

Thanks,
The SaveOurFaves team
"""
        html_email_body = f"""
<p>Hi there from the SaveOurFaves.org team! You recently told us you were interested in buying a gift card to support {place_name}. They now have a <a href="{gift_card_url}">link where you can do this online.</a></p>

<p>Not sure how much to spend? Consider a gift card for one month’s worth of your usual spending there, if you’re able. Thank you for doing your part to keep our local businesses around. We hope you are safe and healthy.</p>

<p>Thanks,<br/>
The SaveOurFaves team</p>
        """
        if not really_send:
            print("Would have sent to", to_address, place_name, gift_card_url)
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