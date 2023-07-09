# -*- coding: utf-8 -*-
# Copyright 2015, 2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from synapse.api.errors import SynapseError
from synapse.http.servlet import RestServlet

from ._base import client_patterns
import synapse.types
from synapse.types import UserID

logger = logging.getLogger(__name__)


class ReceiptRestServlet(RestServlet):
    PATTERNS = client_patterns(
        "/rooms/(?P<room_id>[^/]*)"
        "/receipt/(?P<receipt_type>[^/]*)"
        "/(?P<event_id>[^/]*)$"
    )

    def __init__(self, hs):
        super(ReceiptRestServlet, self).__init__()
        self.hs = hs
        self.auth = hs.get_auth()
        self.receipts_handler = hs.get_receipts_handler()
        self.presence_handler = hs.get_presence_handler()
        self.store = hs.get_datastore()
        self.event_handler = hs.get_event_handler()

    async def on_POST(self, request, room_id, receipt_type, event_id):
        requester = await self.auth.get_user_by_req(request)

        if receipt_type != "m.read":
            raise SynapseError(400, "Receipt type must be 'm.read'")

        await self.presence_handler.bump_presence_active_time(requester.user)

        await self.receipts_handler.received_client_receipt(
            room_id, receipt_type, user_id=requester.user.to_string(), event_id=event_id
        )

        return 200, {}

    async def on_GET(self, request, room_id, receipt_type, event_id):
        """requester = await self.auth.get_user_by_req(request, allow_guest=True)
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
            )"""
        
        receipts = await self.store.get_receipts_for_room(room_id, receipt_type)
        requester = await self.auth.get_user_by_req(request)
        
        user_id = None;
        if b"user_id" in request.args:
            user_id = request.args[b"user_id"][0].decode("ascii")
            
        ts = 0
        event = None
        for r in receipts: 
            if user_id is None or user_id and r["user_id"] == user_id:
                event = await self.event_handler.get_event(requester.user, None, r["event_id"])
                ts = max(ts, event["origin_server_ts"]);

        return 200, {"origin_server_ts" : ts}


def register_servlets(hs, http_server):
    ReceiptRestServlet(hs).register(http_server)
