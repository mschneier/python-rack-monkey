"""Log changes."""
import gc
from SqlConnection import SqlConnect as connect


class SqlLog:
    """Log changes to tables."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def log(table, id_changed, name_changed, change_type, desc, user):
        """Log changes to tables."""
        con = connect.logging_connection()
        cur = con.cursor()
        # Get id on insert change.
        if change_type == "insert":
            cur.execute(
                f'SELECT id FROM "{table}" ORDER BY id DESC LIMIT 1',
            )
            id_changed = cur.fetchone()
        cur.execute(
            """INSERT INTO logging (
                table_changed, id_changed, name_changed, change_type,
                descript, update_time, update_user
            ) VALUES (
                %s, %s, %s, %s, %s,
                DATE_TRUNC('second', NOW()::timestamp), %s
            )""", (
                table, id_changed, name_changed, change_type, desc, user
            )
        )
        con.commit()
