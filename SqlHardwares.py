"""Sql operations for hardware table."""
import gc
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlHardware:
    """Hardware sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def get_all_manufacturers():
        """Get all manufacturers."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM org WHERE hardware > 0 ORDER BY name"
        )
        mans = cur.fetchall()
        return mans

    @staticmethod
    def add_new_hardware(
        name, org, size, image, support, spec, notes, user
    ):
        """Insert new hardware."""
        con = connect.insert_connection()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO hardware (
                name, manufacturer, size, image, support_url, spec_url,
                notes, meta_update_time, meta_update_user
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                DATE_TRUNC('second', NOW()::timestamp), %s
            )""", (name, org, size, image, support, spec, notes, user)
        )
        con.commit()
        # Update log table.
        sql_log.log("hardware", "", name, "insert", "", user)

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name
                IN ('hardware', 'org')"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @classmethod
    def get_all_hardware(cls, sort="hardware.name"):
        """Retrieve all hardwares."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT hardware.id, hardware.name,
                CASE WHEN org.name LIKE 'unknown'
                    THEN CONCAT('-', org.name)
                    ELSE org.name
                END,
                hardware.size, hardware.support_url,
                hardware.spec_url, hardware.notes
            FROM hardware, org
            WHERE hardware.manufacturer = org.id
            ORDER BY %s""" % (sort))
        keys = [
            "id", "name", "manufacturer", "size", "support", "spec", "notes"
        ]
        hardware = [dict(zip(keys, hard)) for hard in cur.fetchall()]
        for hard in hardware:
            hard["notes_short"] = hard["notes"][:20]
        return hardware

    @staticmethod
    def get_one_hardware(hardware_id):
        """Get info on a hardware."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT hardware.id, hardware.name, org.name,
                hardware.size, hardware.image,
                hardware.support_url, hardware.spec_url,
                hardware.notes, hardware.meta_update_user,
                hardware.meta_update_time
            FROM hardware, org
            WHERE hardware.id = %s
                AND hardware.manufacturer = org.id""", (hardware_id,)
        )
        hardware = cur.fetchone()
        hardware = {
            "id": hardware[0],
            "name": hardware[1],
            "manufacturer": hardware[2],
            "size": hardware[3],
            "image": hardware[4],
            "support": hardware[5],
            "spec": hardware[6],
            "notes": hardware[7],
            "update_user": hardware[8],
            "update_time": hardware[9]
        }
        return hardware

    @staticmethod
    def get_nearest_hardware_by_id(hardware_id):
        """Get id, name of nearest hardware by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM hardware ORDER BY ABS(id - %s) LIMIT 1",
            (hardware_id,)
        )
        hardware = cur.fetchone()
        return hardware

    @staticmethod
    def update_hardware(
        hard_id, name, org, size, image, support, spec, notes, user
    ):
        """Update new hardware."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE hardware
            SET name = %s,
                manufacturer = %s,
                size = %s,
                image = %s,
                support_url = %s,
                spec_url = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (
                name, org, size, image, support,
                spec, notes, user, hard_id
            )
        )
        con.commit()
        # Update log table.
        sql_log.log("hardware", hard_id, name, "update", "", user)

    @staticmethod
    def delete_hardware(hard_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM hardware WHERE id = %s", (hard_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM hardware WHERE id = %s", (hard_id,))
        con.commit()
        # Update log table.
        sql_log.log("hardware", hard_id, name, "delete", "", user)
