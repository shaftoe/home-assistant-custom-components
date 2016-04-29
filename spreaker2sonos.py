'''Subscribe to feedreader events. If event is from Spreaker url.
Parse the content and add the MP3 link to Sonos queue.'''
from logging import getLogger
from homeassistant.components.feedreader import EVENT_FEEDREADER
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.components.media_player import (SERVICE_PLAY_MEDIA,
    ATTR_MEDIA_ENQUEUE, ATTR_MEDIA_CONTENT_ID, ATTR_MEDIA_CONTENT_TYPE)


DOMAIN = 'spreaker2sonos'
DEPENDENCIES = [MEDIA_PLAYER_DOMAIN]
_LOGGER = getLogger(__name__)


def setup(hass, config):
    """Setup the spreaker2sonos component."""

    def get_uri_from_data(data):
        '''Get mp3 link from feed data.'''
        for link in data.links:
            if link.get('type') == 'audio/mpeg':
                return link.get('href')

    def parse_event(event):
        '''If event is a Spreaker feed url, parse and add it to queue.'''
        if 'spreaker' in event.data.get('feed_url', ''):
            uri = get_uri_from_data(event.data)

            if uri:
                hass.services.call(MEDIA_PLAYER_DOMAIN,
                                   SERVICE_PLAY_MEDIA,
                                   {ATTR_MEDIA_CONTENT_ID: uri,
                                    ATTR_MEDIA_CONTENT_TYPE: 'audio/mpeg',
                                    ATTR_MEDIA_ENQUEUE: True})
                _LOGGER.info('Added URI "%s" to queue', uri)
                # TODO store last parsed item and ignore if already processed
            else:
                _LOGGER.error('Could not find mp3 link from Spreaker '
                              'feed entry "%s"', event.data.title)

    hass.bus.listen(EVENT_FEEDREADER, parse_event)
    return True
