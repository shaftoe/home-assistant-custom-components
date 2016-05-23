"""
Subscribe to feedreader events.

Parse the entity content and add multimedia link (if available) to Sonos queue.
"""
from logging import getLogger

from homeassistant.components.feedreader import EVENT_FEEDREADER
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.components.media_player import (
    SERVICE_PLAY_MEDIA, ATTR_MEDIA_ENQUEUE, ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE)

DOMAIN = 'feed2sonos'
DEPENDENCIES = [MEDIA_PLAYER_DOMAIN]
_LOGGER = getLogger(__name__)


def setup(hass, config):
    """Setup the feed2sonos component."""
    def get_uri_from_data(entry):
        """Get mp3 link from feed entry data."""
        for link in entry.links:
            if link.get('type') == 'audio/mpeg':
                return link.get('href')

    def parse_event(event):
        """Parse event and add it to queue if has multimedia content."""
        uri = get_uri_from_data(event.data)
        if uri:
            hass.services.call(MEDIA_PLAYER_DOMAIN,
                               SERVICE_PLAY_MEDIA,
                               {ATTR_MEDIA_CONTENT_ID: uri,
                                ATTR_MEDIA_CONTENT_TYPE: 'audio/mpeg',
                                ATTR_MEDIA_ENQUEUE: True})
            _LOGGER.info('Added URI "%s" to queue', uri)

    hass.bus.listen(EVENT_FEEDREADER, parse_event)
    return True
