"""Sql operations for os table."""
import gc
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlOs:
    """Insert oss."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def get_all_developers():
        """Get all manufacturers."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM org WHERE software > 0 ORDER BY name"
        )
        devs = [dict(zip(["id", "name"], dev)) for dev in cur.fetchall()]
        return devs

    @staticmethod
    def add_new_os(name, manufacturer, notes, user):
        """Insert new os."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO os (
                name, manufacturer, notes, meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s)
            """, (name, manufacturer, notes, user)
        )
        con.commit()
        # Update log table.
        sql_log.log("os", "", name, "insert", "", user)

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name
                IN ('os', 'org')"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_oses(cls, sort="os.name"):
        """Retrieve all oses."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT os.id, os.name, org.name, os.notes
            FROM os, org
            WHERE os.id > 2
                AND os.manufacturer = org.id
            ORDER BY %s""" % (sort))
        keys = ["id", "name", "maker", "notes"]
        oses = [dict(zip(keys, os)) for os in cur.fetchall()]
        return oses

    @staticmethod
    def get_one_os(os_id):
        """Get info on a os."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT os.id, os.name, org.name,
                os.notes, os.meta_update_user,
                os.meta_update_time
            FROM os, org
            WHERE os.id = %s
                AND os.manufacturer = org.id""", (os_id,)
        )
        os = cur.fetchone()
        os = {
            "id": os[0],
            "name": os[1],
            "maker": os[2],
            "notes": os[3],
            "update_user": os[4],
            "update_time": os[5]
        }
        return os

    @staticmethod
    def get_nearest_os_by_id(os_id):
        """Get id, name of nearest os by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM os ORDER BY ABS(id - %s) LIMIT 1",
            (os_id,)
        )
        os = cur.fetchone()
        return os

    @staticmethod
    def update_os(os_id, name, manufacturer, notes, user):
        """Update new os."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE os
            SET name = %s,
                manufacturer = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (name, manufacturer, notes, user, os_id)
        )
        con.commit()
        # Update log table.
        sql_log.log("os", os_id, name, "update", "", user)

    @staticmethod
    def delete_os(os_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM os WHERE id = %s", (os_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM os WHERE id = %s", (os_id,))
        con.commit()
        # Update log table.
        sql_log.log("os", os_id, name, "delete", "", user)
