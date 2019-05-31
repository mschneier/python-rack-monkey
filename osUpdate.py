"""
 1. sudo bash
 2. . ~/.bashrc
 3. python3.6 /var/www/html/rack/osUpdate.py
"""
from psycopg2 import connect
from os import environ


def update_os():
    """Update OS and version for device in rack_monkey."""
    con = connect(
        database="rack_monkey", user="os_update", host="127.0.0.1",
        password=environ["OS_UPDATE_PASSWORD"]
    )
    cur = con.cursor()
    dev_name, os_name, ver, dev_id = ["", "", "", ""]
    while not len(dev_name):
        dev_name = input("Name of device w/o domain: ")
        while not dev_id:
            cur.execute("SELECT id FROM device WHERE name = %s", (dev_name,))
            dev_id = cur.fetchone()
            if not dev_id:
                print("There isn't any device with that name.")
                dev_name = input("Name of device: ")
        dev_id = dev_id[0]
    cur.execute("SELECT name FROM os ORDER BY name")
    oses = [os[0] for os in cur.fetchall()]
    while os_name not in oses:
        os_name = input("Name of OS: ")
        if os_name not in oses:
            print("Valid OS'es: " + ", ".join(oses))
    while not len(ver):
        ver = input("OS Version: ")
    username = environ["SUDO_USER"]
    cur.execute(
        """UPDATE device
        SET os = (SELECT id FROM os WHERE name = %s),
            os_version = %s,
            meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
            meta_update_user = %s
        WHERE id = %s""",
        (os_name, ver, username, dev_id)
    )
    con.commit()
    con.close()
    con = connect(
        database="rack_monkey", user="logging", host="127.0.0.1",
        password=environ["PSQL_LOGGING_USER_PASS"]
    )
    cur = con.cursor()
    cur.execute(
        """INSERT INTO logging (
                table_changed, id_changed, name_changed, change_type,
                descript, update_time, update_user
        ) VALUES (
            %s, %s, %s, %s, %s,
            DATE_TRUNC('second', NOW()::timestamp), %s
        )""", (
            "device", dev_id, dev_name, "update", "", username
        )
    )
    con.commit()
    con.close()
    print(f"Updated device {dev_name} on rack_monkey with OS {os_name} {ver}")


if __name__ == "__main__":
    update_os()
