"""Sql operations for app table."""
from app import application as app
import gc
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlApp:
    """App sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_app(name, desc, notes, user):
        """Insert new app."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO app (
                name, descript, notes,
                meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s)
            """, (name, desc, notes, user)
        )
        con.commit()
        # Update log table.
        sql_log.log("app", "", name, "insert", "", user)

    @staticmethod
    def add_app_device_relation(app, device, relation, user):
        """Insert new app to device relationship."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO device_app (
                app, device, relation,
                meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s)
            """, (app, device, relation, user)
        )
        con.commit()
        # Update log table.
        sql_log.log(
            "device_app", "", f"{app} - {relation} - {device}",
            "insert", "", user
        )

    @staticmethod
    def get_relation_name(rel_id):
        """Get app of relationship."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT app FROM device_app WHERE id = %s", (rel_id,))
        return cur.fetchone()[0]

    @classmethod
    def get_all_relations(cls):
        """Get all types of relations."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM app_relation"
        )
        relations = cur.fetchall()
        return relations

    @classmethod
    def get_all_devices(cls):
        """Get all ids and names for devices."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM device ORDER BY name"
        )
        devices = cur.fetchall()
        return devices

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name = 'app'"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_apps(cls, sort="app.name"):
        """Retrieve all apps."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(f"SELECT * FROM app ORDER BY {sort}")
        keys = [
            "id", "name", "descript", "notes", "meta", "update_time",
            "update_user"
        ]
        apps = [dict(zip(keys, app)) for app in cur.fetchall()]
        return apps

    @staticmethod
    def get_one_app(app_id):
        """Get info on one app."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT name, descript, meta_update_user, meta_update_time,
                notes, id
            FROM app WHERE id = %s""", (app_id,)
        )
        app = cur.fetchone()
        one_app = {
            "name": app[0],
            "descript": app[1],
            "update_user": app[2],
            "update_time": app[3],
            "notes": app[4],
            "id": app[5]
        }
        cur.execute(
            """SELECT device.name, app_relation.name, device_app.id
            FROM device, app, device_app, app_relation
            WHERE app.id = %s
                AND device_app.relation = app_relation.id
                AND device_app.app = app.id
                AND device_app.device = device.id""", (app_id,))
        keys = ["name", "relation", "device_app"]
        devices = [dict(zip(keys, device)) for device in cur.fetchall()]
        one_app["devices"] = devices
        return one_app

    @staticmethod
    def get_nearest_app_by_id(app_id):
        """Get id, name of nearest app by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM app ORDER BY ABS(id - %s) LIMIT 1",
            (app_id,)
        )
        return cur.fetchone()

    @staticmethod
    def update_app(app_id, name, desc, notes, user):
        """Update new app."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE app
            SET name = %s,
                descript = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (name, desc, notes, user, app_id)
        )
        con.commit()
        # Update log table.
        sql_log.log("app", app_id, name, "update", "", user)

    @staticmethod
    def delete_app(table, app_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        if table == "device_app":
            cur.execute("SELECT app FROM device_app WHERE id = %s", (app_id,))
            name = cur.fetchone()[0]
            cur.execute("DELETE FROM device_app WHERE id = %s", (app_id,))
        else:
            cur.execute("SELECT name FROM app WHERE id = %s", (app_id,))
            name = cur.fetchone()[0]
            cur.execute("DELETE FROM app WHERE id = %s", (app_id,))
        con.commit()
        # Update log table.
        sql_log.log("app", app_id, name, "delete", "", user)
