"""Sql operations for org table."""
import gc
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlOrg:
    """Org sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_org(
        name, account_no, customer, software, hardware, descript,
        home_page, notes, user
    ):
        """Insert new org."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO org (
                name, account_no, customer, software, hardware, descript,
                home_page, notes, meta_update_time, meta_update_user
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                DATE_TRUNC('second', NOW()::timestamp), %s
            )""", (
                name, account_no, customer, software, hardware, descript,
                home_page, notes, user
            )
        )
        con.commit()
        # Update log table.
        sql_log.log("org", "", name, "insert", "", user)

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name = 'org'"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_orgs(cls, sort="org.name"):
        """Retrieve all orgs."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT id, name, descript, customer, software, hardware, notes
            FROM org
            WHERE org.id > 2
            ORDER BY %s""" % (sort))
        keys = [
            "id", "name", "descript", "customer", "software", "hardware",
            "notes"
        ]
        orgs = [dict(zip(keys, org)) for org in cur.fetchall()]
        return orgs

    @staticmethod
    def get_one_org(org_id):
        """Get info on a org."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT name, descript, account_no, customer, software,
                hardware, home_page, notes, meta_update_user,
                meta_update_time, id
            FROM org
            WHERE org.id = %s""", (org_id,)
        )
        org = cur.fetchone()
        org = {
            "name": org[0],
            "descript": org[1],
            "account_no": org[2],
            "customer": org[3],
            "software": org[4],
            "hardware": org[5],
            "home_page": org[6],
            "notes": org[7],
            "update_user": org[8],
            "update_time": org[9],
            "id": org[10]
        }
        return org

    @staticmethod
    def get_nearest_org_by_id(org_id):
        """Get id, name of nearest org by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM org ORDER BY ABS(id - %s) LIMIT 1",
            (org_id,)
        )
        org = cur.fetchone()
        return org

    @staticmethod
    def update_org(
        org_id, name, account_no, customer, software, hardware, descript,
        home_page, notes, user
    ):
        """Update new org."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE org
            SET name = %s,
                account_no = %s,
                customer = %s,
                software = %s,
                hardware = %s,
                descript = %s,
                home_page = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (
                name, account_no, customer, software, hardware, descript,
                home_page, notes, user, org_id
            )
        )
        con.commit()
        # Update log table.
        sql_log.log("org", org_id, name, "update", "", user)

    @staticmethod
    def delete_org(org_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM org WHERE id = %s", (org_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM org WHERE id = %s", (org_id,))
        con.commit()
        # Update log table.
        sql_log.log("org", org_id, name, "delete", "", user)
