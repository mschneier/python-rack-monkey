"""Sql operations for building table."""
import gc
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlBuilding:
    """Building sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_building(name, short, notes, user):
        """Insert new building."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO building (
                name, name_short, notes,
                meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s)
            """, (name, short, notes, user)
        )
        # Update log table.
        con.commit()
        sql_log.log("building", "", name, "insert", "", user)

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name = 'building'"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_buildings(cls, sort="building.name"):
        """Retrieve all apps."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT id, name, name_short, notes FROM building
            WHERE id > 5 ORDER BY %s""" % (sort))
        keys = ["id", "name", "name_short", "notes"]
        buildings = [dict(zip(keys, build)) for build in cur.fetchall()]
        return buildings

    @staticmethod
    def get_one_building(build_id):
        """Get info and rooms in building."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT name, name_short, notes, meta_update_user,
                meta_update_time, id
            FROM building WHERE id = %s""", (build_id,)
        )
        building = list(cur.fetchone())
        one_build = {
            "name": building[0],
            "name_short": building[1],
            "notes": building[2],
            "update_user": building[3],
            "update_time": building[4],
            "id": building[5]
        }
        cur.execute(
            """SELECT id, name FROM room
            WHERE building = %s""", (build_id,)
        )
        rooms = [dict(zip(["id", "name"], room)) for room in cur.fetchall()]
        one_build["rooms"] = rooms
        return one_build

    @staticmethod
    def get_nearest_building_by_id(building_id):
        """Get id, name of nearest building by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM building ORDER BY ABS(id - %s) LIMIT 1",
            (building_id,)
        )
        building = cur.fetchone()
        return building

    @staticmethod
    def update_building(build_id, name, short, notes, user):
        """Update new building."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE building
            SET name = %s,
                name_short = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (name, short, notes, user, build_id)
        )
        con.commit()
        # Update log table.
        sql_log.log("building", build_id, name, "update", "", user)

    @staticmethod
    def delete_building(build_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM buidling WHERE id = %s", (build_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM building WHERE id = %s", (build_id,))
        con.commit()
        # Update log table.
        sql_log.log("building", build_id, name, "delete", "", user)
