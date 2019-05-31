"""Sql operations for role table."""
import gc
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlRole:
    """Role sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_role(name, descript, notes, user):
        """Insert new role."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO role (
                name, descript, notes, meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s)
            """, (name, descript, notes, user)
        )
        con.commit()
        # Update log table.
        sql_log.log("role", "", name, "insert", "", user)

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name = 'role'"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_roles(cls, sort="role.name"):
        """Retrieve all roles."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM role ORDER BY %s" % (sort))
        keys = [
            "id", "name", "descript", "notes", "meta", "update_time",
            "update_user"
        ]
        roles = [dict(zip(keys, role)) for role in cur.fetchall()]
        return roles

    @staticmethod
    def get_one_role(role_id):
        """Get info on one role."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT id, name, descript, notes,
                meta_update_user, meta_update_time
            FROM role WHERE id = %s""", (role_id,)
        )
        role = cur.fetchone()
        role = {
            "id": role[0],
            "name": role[1],
            "descript": role[2],
            "notes": role[3],
            "update_user": role[4],
            "update_time": role[5]
        }
        return role

    @staticmethod
    def get_nearest_role_by_id(role_id):
        """Get id, name of nearest role by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM role ORDER BY ABS(id - %s) LIMIT 1",
            (role_id,)
        )
        role = cur.fetchone()
        return role

    @staticmethod
    def update_role(role_id, name, descript, notes, user):
        """Update new role."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE role
            SET name = %s,
                descript = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (name, descript, notes, user, role_id)
        )
        con.commit()
        # Update log table.
        sql_log.log("role", role_id, name, "update", "", user)

    @staticmethod
    def delete_role(role_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM role WHERE id = %s", (role_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM role WHERE id = %s", (role_id,))
        con.commit()
        # Update log table.
        sql_log.log("role", role_id, name, "delete", "", user)
