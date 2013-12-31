"""utils.py"""

import random

from pyechonest import config as echonest_config
from pyechonest import song as echonest_song
import rfc3987

from gweetr import app
from gweetr.exceptions import GweetrError

echonest_config.ECHO_NEST_API_KEY = app.config['ECHO_NEST_API_KEY']


def fetch_track(track_params):
    """
    Fetch a track from 7digital via the Echo Nest API.

    Available track parameters are listed at
    http://developer.echonest.com/docs/v4/song.html#search
    """
    try:
        search_results = echonest_song.search(
            buckets=['id:7digital-US', 'tracks'],
            limit=True,
            results=app.config['ECHO_NEST_SONG_RESULTS'],
            **track_params
        )
    except TypeError as exc:
        raise GweetrError("Received unknown track parameter: %s" % str(exc))

    if search_results:
        song_obj = random.choice(search_results)
        tracks = song_obj.get_tracks('7digital-US')
        track_data = tracks[0]
        track = {
            'title': song_obj.title,
            'artist': song_obj.artist_name,
            'url': track_data['preview_url']
        }
        return track


def is_valid_url(a_string):
    """Check if a string is a valid URL."""
    return rfc3987.match(a_string, 'URI')
