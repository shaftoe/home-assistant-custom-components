"""
Subscribe to feedreader events. If event is from Spreaker url.

Parse the content and add the MP3 link to Sonos queue.
"""
import pickle
from logging import getLogger
from os.path import exists, join

from homeassistant.config import get_default_config_dir
from homeassistant.components.feedreader import EVENT_FEEDREADER
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.components.media_player import (
    SERVICE_PLAY_MEDIA, ATTR_MEDIA_ENQUEUE, ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE)

DOMAIN = 'spreaker2sonos'
DEPENDENCIES = [MEDIA_PLAYER_DOMAIN]
_LOGGER = getLogger(__name__)
FILE = join(get_default_config_dir(), DOMAIN + '.pickle')
DATE_FORMAT = '%a, %d %b %Y %H:%M:%S +0000'
TIMESTAMP_ENTITY_KEY = 'published_parsed'


def setup(hass, config):
    """Setup the spreaker2sonos component."""
    def get_stored_data():
        """Return stored data."""
        if not exists(FILE):
            return {}
        with open(FILE, 'rb') as myfile:
            content = pickle.load(myfile)
        myfile.close()
        return content

    def store_uri_timestamp(timestamp, feed_url):
        """Store uri timestamp to file."""
        with open(FILE, 'wb') as myfile:
            pickle.dump({feed_url: timestamp}, myfile, pickle.HIGHEST_PROTOCOL)
        myfile.close()

    def get_uri_from_data(entry):
        """Get mp3 link from feed entry data."""
        for link in entry.links:
            if link.get('type') == 'audio/mpeg':
                return link.get('href')

    def get_new_uri_from_data(entry, feed_url):
        """Return uri if does not match stored one."""
        uri = get_uri_from_data(entry)
        stored_entry_timestamp = get_stored_data().get(feed_url)
        if (stored_entry_timestamp and
                entry.get(TIMESTAMP_ENTITY_KEY) <= stored_entry_timestamp):
            _LOGGER.debug('URI %s already processed', uri)
            return None
        return uri

    def parse_event(event):
        """If event is a Spreaker feed url, parse and add it to queue."""
        feed_url = event.data.get('feed_url', '')
        if 'spreaker' in feed_url:
            uri = get_new_uri_from_data(event.data, feed_url)

            if uri:
                hass.services.call(MEDIA_PLAYER_DOMAIN,
                                   SERVICE_PLAY_MEDIA,
                                   {ATTR_MEDIA_CONTENT_ID: uri,
                                    ATTR_MEDIA_CONTENT_TYPE: 'audio/mpeg',
                                    ATTR_MEDIA_ENQUEUE: True})
                _LOGGER.info('Added URI "%s" to queue', uri)
                store_uri_timestamp(event.data.get(TIMESTAMP_ENTITY_KEY),
                                    feed_url)

    hass.bus.listen(EVENT_FEEDREADER, parse_event)
    return True
