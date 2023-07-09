# -*- coding: utf-8 -*-
# Copyright 2014-2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
import logging
import random
import uuid
import base64

from synapse.api.constants import EventTypes, Membership
from synapse.api.errors import AuthError, SynapseError
from synapse.events import EventBase
from synapse.handlers.presence import format_user_presence_state
from synapse.logging.utils import log_function
from synapse.types import UserID
from synapse.visibility import filter_events_for_client

from ._base import BaseHandler

logger = logging.getLogger(__name__)


class InviteHandler(BaseHandler):
    def __init__(self, hs):
        super(InviteHandler, self).__init__(hs)
        
        self.clock = hs.get_clock()

    @log_function
    async def get_invite_link(
        self,
        auth_user_id,
        affect_presence,
        room_id,
    ):
        
        if room_id:
            blocked = await self.store.is_room_blocked(room_id)
            if blocked:
                raise SynapseError(403, "This room has been blocked on this server")

        presence_handler = self.hs.get_presence_handler()
        
        
        invite_uuid = uuid.uuid4()
        encoded_uuid = str(base64.urlsafe_b64encode(invite_uuid.bytes), "utf-8")
        await self.store.insert_invite(encoded_uuid, room_id, self.clock.time_msec())
        link = self.hs.config.public_baseurl + "join/" + encoded_uuid
        
        

        context = await presence_handler.user_syncing(
            auth_user_id, affect_presence=affect_presence
        )
        with context:            
            chunk = {
                "link": link,
            }

            return chunk
     
    @log_function
    async def decode_invite_link(
        self,
        auth_user_id,
        affect_presence,
        short_id,
    ): 
        presence_handler = self.hs.get_presence_handler()
        room_id = await self.store.get_invite_for_short_id(short_id)
        context = await presence_handler.user_syncing(
            auth_user_id, affect_presence=affect_presence
        )
        with context:            
            chunk = {
                "room_id": room_id,
            }

            return chunk

