"""Sql operations for domain table."""
import gc
from psycopg2 import connect
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlDomain:
    """Domain sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_domain(name, descript, notes, user):
        """Insert new domain."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO domain (
                name, descript, notes,
                meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s)
            """, (name, descript, notes, user)
        )
        con.commit()
        # Update log table.
        sql_log.log("domain", "", name, "insert", "", user)

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name = 'domain'"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_domains(cls, sort="domain.name"):
        """Retrieve all apps."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT id, name, descript, notes
            FROM domain WHERE id > 2 ORDER BY %s""" % (sort))
        keys = ["id", "name", "descript", "notes"]
        domains = [dict(zip(keys, domain)) for domain in cur.fetchall()]
        return domains

    @staticmethod
    def get_all_domains_full():
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT id, name FROM domain ORDER BY 2")
        domains = [
            dict(zip(["id", "name"], domain)) for domain in cur.fetchall()
        ]
        return domains

    @staticmethod
    def get_one_domain(domain_id):
        """Get info on a domain."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT name, descript, notes,
                meta_update_user, meta_update_time, id
            FROM domain WHERE id = %s""", (domain_id,)
        )
        domain = cur.fetchone()
        domain = {
            "name": domain[0],
            "descript": domain[1],
            "notes": domain[2],
            "update_user": domain[3],
            "update_time": domain[4]
        }
        return domain

    @staticmethod
    def get_nearest_domain_by_id(dom_id):
        """Get id, name of nearest domain by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM domain ORDER BY ABS(id - %s) LIMIT 1",
            (dom_id,)
        )
        domain = cur.fetchone()
        return domain

    @staticmethod
    def update_domain(dom_id, name, descript, notes, user):
        """Update new domain."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE domain
            SET name = %s,
                descript =%s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (name, descript, notes, user, dom_id)
        )
        con.commit()
        # Update log table.
        sql_log.log("domain", dom_id, name, "update", "", user)

    @staticmethod
    def delete_domain(dom_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM domain WHERE id = %s", (dom_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM domain WHERE id = %s", (dom_id,))
        con.commit()
        # Update log table.
        sql_log.log("domain", dom_id, name, "delete", "", user)
