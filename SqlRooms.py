"""Sql operations for room table."""
import gc
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlRoom:
    """Room sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_room(name, building, notes, user):
        """Insert new room."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO room (
                name, building, notes,
                meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s)
            """, (name, building, notes, user)
        )
        con.commit()
        # Update log table.
        sql_log.log("room", "", name, "insert", "", user)

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name
                IN ('room', 'building')"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_rooms(cls, sort="room.name"):
        """Retrieve all rooms."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT room.id, room.name, building.name, room.notes
            FROM room, building
            WHERE room.id > 5
                AND room.building = building.id
            ORDER BY %s""" % (sort))
        keys = ["id", "name", "building", "notes"]
        rooms = [dict(zip(keys, room)) for room in cur.fetchall()]
        return rooms

    @staticmethod
    def get_one_room(room_id):
        """Get info and rooms in room."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT room.name,
                CASE WHEN building.id::varchar IN ('1', '2', '3', '4')
                    THEN 0::varchar
                ELSE
                    building.name
                END,
                building.id, room.notes,
                room.meta_update_user, room.meta_update_time, room.id
            FROM room, building
            WHERE room.id = %s
                AND room.building = building.id""", (room_id,)
        )
        room = cur.fetchone()
        room = {
            "name": room[0],
            "building": room[1],
            "build_id": room[2],
            "notes": room[3],
            "update_user": room[4],
            "update_time": room[5],
            "room_id": room[6]
        }
        cur.execute(
            """SELECT rack.id, rack.name
            FROM rack, room, row, building
            WHERE room = %s
                AND rack.row = row.id
                AND row.room = room.id
                AND room.building = building.id
            ORDER BY rack.name""", (room_id,)
        )
        racks = [dict(zip(["id", "name"], rack)) for rack in cur.fetchall()]
        room["racks"] = racks
        return room

    @staticmethod
    def get_nearest_room_by_id(room_id):
        """Get id, name of nearest room by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM room ORDER BY ABS(id - %s) LIMIT 1",
            (room_id,)
        )
        room = cur.fetchone()
        return room

    @staticmethod
    def update_room(room_id, name, building, notes, user):
        """Update new room."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE room
            SET name = %s,
                building = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (name, building, notes, user, room_id)
        )
        con.commit()
        # Update log table.
        sql_log.log("room", room_id, name, "update", "", user)

    @staticmethod
    def delete_room(room_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM room WHERE id = %s", (room_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM room WHERE id = %s", (room_id,))
        con.commit()
        # Update log table.
        sql_log.log("room", room_id, name, "delete", "", user)
