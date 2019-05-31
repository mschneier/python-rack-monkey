"""Sql operations on service table."""
import gc
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlService:
    """Service sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_service(name, descript, notes, user):
        """Insert new service."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO service (
                name, descript, notes, meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s)
            """, (name, descript, notes, user)
        )
        con.commit()
        # Update log table.
        sql_log.log("service", "", name, "insert", "", user)

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name = 'service'"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_services(cls, sort="service.name"):
        """Retrieve all services."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM service ORDER BY %s" % (sort))
        keys = [
            "id", "name", "descript", "notes", "meta", "update_time",
            "update_user"
        ]
        services = [dict(zip(keys, service)) for service in cur.fetchall()]
        return services

    @staticmethod
    def get_one_service(service_id):
        """Get info on one service."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT id, name, descript, notes,
                meta_update_user, meta_update_time
            FROM service WHERE id = %s""", (service_id,)
        )
        service = cur.fetchone()
        service = {
            "id": service[0],
            "name": service[1],
            "descript": service[2],
            "notes": service[3],
            "update_user": service[4],
            "update_time": service[5]
        }
        return service

    @staticmethod
    def get_nearest_service_by_id(service_id):
        """Get id, name of nearest service by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM service ORDER BY ABS(id - %s) LIMIT 1",
            (service_id,)
        )
        service = cur.fetchone()
        return service

    @staticmethod
    def update_service(service_id, name, descript, notes, user):
        """Update new service."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE service
            SET name = %s,
                descript = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (name, descript, notes, user, service_id)
        )
        con.commit()
        # Update log table.
        sql_log.log("service", service_id, name, "update", "", user)

    @staticmethod
    def delete_service(serv_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM service WHERE id = %s", (serv_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM service WHERE id = %s", (serv_id,))
        con.commit()
        # Update log table.
        sql_log.log("service", serv_id, name, "delete", "", user)
