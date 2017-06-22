import re

from six.moves.urllib.parse import urlparse

def jurisdiction_levels_from_url(url):
    """
    Returns jurisdictions covered by results based on the result URL.
    """
    levels = []
    parsed = urlparse(url)
    path_bits = parsed.path.split('/')

    if re.match(r'^[A-Z]{2}$', path_bits[1]):
        levels.append({
            'level': 'state',
            'name': path_bits[1],
        })

    if not re.match(r'^\d+$', path_bits[2]):
        levels.append({
            'level': 'county',
            'name': path_bits[2],
        })

    return levels
