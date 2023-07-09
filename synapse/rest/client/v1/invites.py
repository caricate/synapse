# -*- coding: utf-8 -*-
# Copyright 2014-2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software

"""This module contains REST servlets to do with invites, /invites."""
import logging

from synapse.api.errors import SynapseError
from synapse.http.servlet import RestServlet
from synapse.rest.client.v2_alpha._base import client_patterns
from synapse.streams.config import PaginationConfig

logger = logging.getLogger(__name__)


class InviteRestServlet(RestServlet):
    PATTERNS = client_patterns("/join$", v1=True)

    DEFAULT_LONGPOLL_TIME_MS = 30000

    def __init__(self, hs):
        super(InviteRestServlet, self).__init__()
        self.invite_handler = hs.get_invite_handler()
        self.auth = hs.get_auth()

    async def on_GET(self, request):
        requester = await self.auth.get_user_by_req(request, allow_guest=True)
        is_guest = requester.is_guest
        room_id = None
        short_id = None
        if b"room_id" not in request.args and b"short_id" not in request.args:
            raise SynapseError(400, "Users must specify room_id or short_id param")
        if b"room_id" in request.args:
            room_id = request.args[b"room_id"][0].decode("ascii")
        if b"short_id" in request.args:
            short_id = request.args[b"short_id"][0].decode("ascii")

        chunk = {}
        if room_id:
            chunk = await self.invite_handler.get_invite_link(
                requester.user.to_string(),            
                affect_presence=(not is_guest),
                room_id=room_id,
            )
        if short_id:
            chunk = await self.invite_handler.decode_invite_link(
                requester.user.to_string(),            
                affect_presence=(not is_guest),
                short_id=short_id,
            )

        return 200, chunk

    def on_OPTIONS(self, request):
        return 200, {}

'''
class EventRestServlet(RestServlet):
    PATTERNS = client_patterns("/events/(?P<event_id>[^/]*)$", v1=True)

    def __init__(self, hs):
        super(EventRestServlet, self).__init__()
        self.clock = hs.get_clock()
        self.event_handler = hs.get_event_handler()
        self.auth = hs.get_auth()
        self._event_serializer = hs.get_event_client_serializer()

    async def on_GET(self, request, event_id):
        requester = await self.auth.get_user_by_req(request)
        event = await self.event_handler.get_event(requester.user, None, event_id)

        time_now = self.clock.time_msec()
        if event:
            event = await self._event_serializer.serialize_event(event, time_now)
            return 200, event
        else:
            return 404, "Event not found."
'''

def register_servlets(hs, http_server):
    InviteRestServlet(hs).register(http_server)
    #EventRestServlet(hs).register(http_server) 
