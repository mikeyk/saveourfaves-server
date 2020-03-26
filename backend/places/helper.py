from urllib.parse import urlparse
from places.constants import BLACKLISTED_DOMAINS

def check_link_against_blacklist(link):
    if link:
        parsed = urlparse(link)
        if parsed.hostname.replace('www.', '') in BLACKLISTED_DOMAINS:
            return None
    return link