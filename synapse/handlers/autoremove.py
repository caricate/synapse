import logging
from collections import namedtuple
from typing import List

from twisted.internet import defer

from synapse.api.errors import AuthError, SynapseError
from synapse.logging.context import run_in_background
from synapse.types import UserID, get_domain_from_id
from synapse.util.caches.stream_change_cache import StreamChangeCache
from synapse.util.metrics import Measure
from synapse.util.wheel_timer import WheelTimer


class AutoremoveNotificationEventSource(object):
    def __init__(self, hs):
        self.hs = hs
        self.store = hs.get_datastore()
        self.clock = hs.get_clock()
        self.get_typing_handler = hs.get_typing_handler

    def _make_event_for(self, room_id):
        typing = self.get_typing_handler()._room_typing[room_id]
        return {
            "type": "m.room.autoremove",
            "room_id": room_id,
        }

    def get_new_events(self, from_key, room_ids, **kwargs):
        with Measure(self.clock, "autoremove.get_new_events"):
            from_key = int(from_key)
            #handler = self.get_typing_handler()

            events = []
            #for room_id in room_ids:
            #    if room_id not in handler._room_serials:
            #        continue
            #    if handler._room_serials[room_id] <= from_key:
            #        continue

            #    events.append(self._make_event_for(room_id))

            return defer.succeed((events, handler._latest_room_serial))

    def get_current_key(self):
        return 1

    def get_current_key_for_room(self, room_id):
        return 1
