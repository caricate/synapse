from synapse.storage._base import SQLBaseStore


class InviteStore(SQLBaseStore):
    def insert_invite(self, short_id, room_id, ts):
        return self.db.simple_insert(
            table="invites",
            values={
                "short_id": short_id,
                "room_id": room_id,
                "ts": ts,
            },
            desc="insert_invite",
        )

    def get_invite_for_short_id(self, short_id):
        return self.db.simple_select_one_onecol(
            table="invites",
            retcol="room_id",
            keyvalues={"short_id": short_id},
            allow_none=True,
            desc="get_invite_for_short_id",
        )
    
 
