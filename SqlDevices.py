"""Sql opertations on device table."""
import gc
from psycopg2 import connect
import re
from urllib import parse
from SqlConnection import SqlConnect as connect
from SqlLogging import SqlLog as sql_log


class SqlDevice:
    """Device sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_device(
        dev_name, domain, rack_id, rack_pos, model, os, version, key, role,
        in_service, purchased, serial, asset, customer, service_level, notes,
        user
    ):
        """Insert new device."""
        con = connect.insert_connection()
        cur = con.cursor()
        if purchased:
            cur.execute(
                """INSERT INTO device (
                    name, domain, rack, rack_pos, hardware, os, os_version,
                    os_licence_key, role, in_service, purchased, serial_no,
                    asset_no, customer, service, notes, meta_update_time,
                    meta_update_user
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s
                )""", (
                    dev_name, domain, rack_id, rack_pos, model,
                    os, version, key, role, in_service, purchased, serial,
                    asset, customer, service_level, notes, user
                )
            )
        else:
            cur.execute(
                """INSERT INTO device (
                    name, domain, rack, rack_pos, hardware, os, os_version,
                    os_licence_key, role, in_service, serial_no,
                    asset_no, customer, service, notes, meta_update_time,
                    meta_update_user
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, DATE_TRUNC('second', NOW()::timestamp), %s
                )""", (
                    dev_name, domain, rack_id, rack_pos, model,
                    os, version, key, role, in_service, serial,
                    asset, customer, service_level, notes, user
                )
            )
        con.commit()
        # Update log table.
        sql_log.log("device", "", dev_name, "insert", "", user)

    @staticmethod
    def get_info_on_one_device(dev_id):
        """Get info on device by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT device.name, domain.id, device.rack, device.rack_pos,
                org.id, hardware.id, hardware.name, os.id, device.os_version,
                role.id, device.in_service, device.purchased,
                device.customer, device.service, device.notes,
                device.serial_no, device.asset_no, device.os_licence_key
            FROM device, domain, rack, org, hardware, os, role
            WHERE device.hardware = hardware.id
                AND device.domain = domain.id
                AND device.rack = rack.id
                AND hardware.manufacturer = org.id
                AND device.os = os.id
                AND device.role = role.id
                AND device.id = %s
            """, (dev_id,)
        )
        device = cur.fetchone()
        device = {
            "name": device[0],
            "domain": device[1],
            "rack": device[2],
            "pos": device[3],
            "man": device[4],
            "hard_id": device[5],
            "hardware": device[6],
            "os": device[7],
            "version": device[8],
            "role": device[9],
            "in_service": device[10],
            "purchased": device[11],
            "customer": device[12],
            "service": device[13],
            "notes": device[14],
            "serial": device[15],
            "asset": device[16],
            "licence": device[17]
        }
        return device

    @staticmethod
    def get_nearest_device_by_id(dev_id):
        """Get id, name of nearest device by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM device ORDER BY ABS(id - %s) LIMIT 1",
            (dev_id,)
        )
        device = cur.fetchone()
        return device

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name
                IN ('device', 'rack', 'room', 'role', 'hardware', 'os', 'customer')
            """
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        return sorts

    @staticmethod
    def sanitize_filter(fltr):
        """Build sql cmd."""
        if not fltr:
            fltr = {
                "customer": "", "role": "",
                "hardware": "", "os": ""
            }
        for param in ["customer", "role", "hardware", "os"]:
            if not fltr[param]:
                fltr[param] = "NULL"
            else:
                fltr[param] = str(fltr[param])
        return fltr

    @staticmethod
    def get_no_devices():
        """Return no. of devices."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM device"
        )
        devices = cur.fetchall()
        return len(devices)

    @staticmethod
    def get_customers():
        """Return list of customers."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT id, name FROM customer
            WHERE id IN (SELECT customer FROM device)"""
        )
        customers = [dict(zip(["id", "name"], c)) for c in cur.fetchall()]
        return sorted(customers, key=lambda dct: dct["name"])

    @staticmethod
    def get_roles():
        """Return list of roles."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM role WHERE id IN (SELECT role FROM device)"
        )
        roles = [dict(zip(["id", "name"], role)) for role in cur.fetchall()]
        return sorted(roles, key=lambda dct: dct["name"])

    @staticmethod
    def get_hardware():
        """Return list of hardware."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT id, name FROM hardware
            WHERE id IN (SELECT hardware FROM device)"""
        )
        hardware = [dict(zip(["id", "name"], h)) for h in cur.fetchall()]
        return sorted(hardware, key=lambda dct: dct["name"])

    @staticmethod
    def get_os():
        """Return list of os'es."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM os WHERE id IN (SELECT os FROM device)"
        )
        os = [dict(zip(["id", "name"], o)) for o in cur.fetchall()]
        return sorted(os, key=lambda dct: dct["name"])

    @staticmethod
    def get_orgs():
        """Return hardware manufacturers."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT DISTINCT org.id,
                CASE WHEN org.name LIKE 'unknown'
                    THEN CONCAT('-', org.name)
                    ELSE org.name
                END
            FROM org, hardware
            WHERE hardware > 0
                AND hardware.manufacturer = org.id
            ORDER BY 2"""
        )
        orgs = [dict(zip(["id", "name"], org)) for org in cur.fetchall()]
        return orgs

    @staticmethod
    def get_not_in_service_names():
        """Return names of unracked devices."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT device.name FROM device WHERE in_service = 0"
        )
        devices = cur.fetchall()
        devs = [device[0] for device in devices]
        return devs

    @staticmethod
    def get_licence_keys():
        """Return all os licence keys."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT os_licence_key FROM device WHERE LENGTH(os_licence_key) > 0"
        )
        keys = [key[0] for key in cur.fetchall()]
        return keys

    @staticmethod
    def get_serials():
        """Return all serial #s."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT serial_no FROM device WHERE LENGTH(serial_no) > 0"
        )
        serials = [serial[0] for serial in cur.fetchall()]
        return serials

    @staticmethod
    def get_assets():
        """Return all asset #s."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT asset_no FROM device WHERE LENGTH(asset_no) > 0"
        )
        assets = [asset[0] for asset in cur.fetchall()]
        return assets

    @staticmethod
    def get_names():
        """Return all device names."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM device WHERE LENGTH(name) > 0")
        names = [name[0] for name in cur.fetchall()]
        return names

    @staticmethod
    def get_device(dev_id):
        """Return info on one device."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT
                CASE WHEN domain.id>2
                    THEN CONCAT(device.name, '.', domain.name)
                    ELSE device.name
                END,
                rack.name, device.rack_pos,
                CASE WHEN (room.id<2) OR (building.id<2)
                    THEN ''
                    ELSE room.name
                END,
                CASE WHEN LENGTH(building.name_short)>0
                    THEN building.name_short
                    ELSE building.name
                END,
                org.name, hardware.name, hardware.size,
                CASE WHEN EXISTS(
                    SELECT os_version FROM device WHERE id = %s
                )
                    THEN CONCAT(os.name, ' ', device.os_version)
                    ELSE os.name
                END,
                device.os_licence_key, role.name, device.in_service,
                device.purchased,
                CASE WHEN '-' ~ device.purchased
                    THEN 0
                    ELSE ROUND(EXTRACT(
                            DAY FROM NOW() - device.purchased::timestamp
                        )::numeric / 365, 1)
                END,
                device.serial_no, device.asset_no, customer.name,
                service.name, device.notes, device.meta_update_user,
                device.meta_update_time, rack.id, device.id
            FROM device, rack, role, hardware, os, customer, room, building,
                row, service, domain, org
            WHERE device.rack = rack.id
                AND device.domain = domain.id
                AND rack.row = row.id
                AND row.room = room.id
                AND room.building = building.id
                AND device.hardware = hardware.id
                AND device.role = role.id
                AND device.os = os.id
                AND device.customer = customer.id
                AND device.service = service.id
                AND hardware.manufacturer = org.id
                AND device.id = %s""", (dev_id, dev_id)
        )
        try:
            dev = cur.fetchone()
            dev = {
                "name": dev[0],
                "rack": dev[1],
                "pos": dev[2],
                "room": dev[3],
                "building": dev[4],
                "maker": dev[5],
                "hardware": dev[6],
                "size": dev[7],
                "os": dev[8],
                "licence": dev[9],
                "role": dev[10],
                "in_service": dev[11],
                "purchased": dev[12],
                "age": dev[13],
                "serial": dev[14],
                "asset": dev[15],
                "customer": dev[16],
                "service": dev[17],
                "notes": dev[18],
                "update_user": dev[19],
                "update_time": dev[20],
                "rack_id": dev[21],
                "dev_id": dev[22]
            }
        except Exception:
            return ""
        # Add br tags to notes.
        dev["notes"] = dev["notes"].replace("\r\n", "<brk>")
        # Add rack links to notes.
        if dev["notes"]:
            notes = dev["notes"]
            notes = notes.replace("\n", "<br>").replace("\r", "<br>")
            links = re.findall(r"\[.*?\]", notes)
            links = [link.replace("[", "").replace("]", "").split("|")
                     for link in links]
            for link in links:
                url = link[0]
                link_text = link[1]
                if "https://rackmonkey" in url:
                    parsed = parse.urlparse(url)
                    if "device_id" in parsed.query:
                        id = parse.parse_qs(parsed.query)["id"][0]
                        dev_id = parse.parse_qs(parsed.query)["device_id"][0]
                        url = f"/view/racks/list/simple/?rack_list={id}&selected_dev={dev_id}"
                link = "<a href='{}'>{}</a>".format(url, link_text)
                notes = re.sub(r"\[.*?\]", link, notes, count=1)
            dev["notes"] = notes
        return dev

    @classmethod
    def get_devices(cls, sort="device.name", fltr={}):
        """Query for all devices"""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        fltr = cls.sanitize_filter(fltr)
        cur.execute(
            """SELECT device.name,
                CASE WHEN domain.id>2
                    THEN domain.name
                    ELSE ''
                END,
                rack.name, device.rack_pos,
                CASE WHEN (room.id<2) OR (building.id<2)
                    THEN ''
                    ELSE room.name
                END,
                CASE WHEN LENGTH(building.name_short)>0
                    THEN building.name_short
                    ELSE building.name
                END,
                role.name,
                CASE WHEN hardware.id > 1
                    THEN CONCAT(org.name, ' ', hardware.name)
                    ELSE hardware.name
                END,
                CASE WHEN EXISTS(SELECT os_version FROM device)
                    THEN CONCAT(os.name, ' ', device.os_version)
                    ELSE os.name
                END,
                customer.name, device.notes, device.id
            FROM device, rack, role, hardware, os, customer, room,
                building, row, service, domain, org
            WHERE device.rack = rack.id
                AND device.domain = domain.id
                AND rack.row = row.id
                AND row.room = room.id
                AND room.building = building.id
                AND device.hardware = hardware.id
                AND device.role = role.id
                AND device.os = os.id
                AND device.customer = customer.id
                AND device.service = service.id
                AND hardware.manufacturer = org.id
                AND ({} IS NULL OR device.customer = {})
                AND ({} IS NULL OR device.role = {})
                AND ({} IS NULL OR device.hardware = {})
                AND ({} IS NULL OR device.os = {}) ORDER BY {}""".format(
                fltr["customer"], fltr["customer"],
                fltr["role"], fltr["role"],
                fltr["hardware"], fltr["hardware"],
                fltr["os"], fltr["os"], sort
            )
        )
        keys = [
            "name", "domain", "rack", "pos", "room", "building", "role",
            "hardware", "os", "customer", "notes", "id"
        ]
        devs = [dict(zip(keys, dev)) for dev in cur.fetchall()]
        if sort == "device.name":
            return sorted(devs, key=lambda dct: dct["name"].lower())
        return devs

    @classmethod
    def get_devices_asset(cls, sort="device.name", fltr={}):
        """Show devices asset view."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        fltr = cls.sanitize_filter(fltr)
        cur.execute(
            """SELECT device.name,
                CASE WHEN domain.id>2
                    THEN domain.name
                    ELSE ''
                END,
                rack.name, device.rack_pos,
                CASE WHEN (room.id<2) OR (building.id<2)
                    THEN ''
                    ELSE room.name
                END,
                CASE WHEN LENGTH(building.name_short)>0
                    THEN building.name_short
                    ELSE building.name
                END,
                CASE WHEN hardware.id > 1
                    THEN CONCAT(org.name, ' ', hardware.name)
                    ELSE hardware.name
                END,
                device.serial_no, device.asset_no,
                CASE WHEN EXISTS(SELECT os_version FROM device)
                    THEN CONCAT(os.name, ' ', device.os_version)
                    ELSE os.name
                END,
                device.os_licence_key,
                CASE WHEN '-' ~ device.purchased
                    THEN 0
                    ELSE ROUND(EXTRACT(
                            DAY FROM NOW() - device.purchased::timestamp
                        )::numeric / 365, 1)
                END,
                device.purchased, device.notes, device.id
            FROM device, rack, role, hardware, os, customer, room,
                building, row, service, domain, org
            WHERE device.rack = rack.id
                AND device.domain = domain.id
                AND rack.row = row.id
                AND row.room = room.id
                AND room.building = building.id
                AND device.hardware = hardware.id
                AND device.role = role.id
                AND device.os = os.id
                AND device.customer = customer.id
                AND device.service = service.id
                AND hardware.manufacturer = org.id
                AND ({} IS NULL OR device.customer = {})
                AND ({} IS NULL OR device.role = {})
                AND ({} IS NULL OR device.hardware = {})
                AND ({} IS NULL OR device.os = {}) ORDER BY {}""".format(
                fltr["customer"], fltr["customer"],
                fltr["role"], fltr["role"],
                fltr["hardware"], fltr["hardware"],
                fltr["os"], fltr["os"], sort
            )
        )
        keys = [
            "name", "domain", "rack", "pos", "room", "building", "hardware",
            "serial", "asset", "os", "licence", "age", "purchased", "notes",
            "id"
        ]
        devs = [dict(zip(keys, dev)) for dev in cur.fetchall()]
        if sort == "device.name":
            return sorted(devs, key=lambda dct: dct["name"].lower())
        return devs

    @classmethod
    def get_devices_extended(cls, sort="device.name", fltr={}):
        """Get extended info on devices."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        fltr = cls.sanitize_filter(fltr)
        cur.execute(
            """SELECT device.name,
                CASE WHEN domain.id>2
                    THEN domain.name
                    ELSE ''
                END,
                rack.name, device.rack_pos,
                CASE WHEN (room.id<2) OR (building.id<2)
                    THEN ''
                    ELSE room.name
                END,
                CASE WHEN LENGTH(building.name_short)>0
                    THEN building.name_short
                    ELSE building.name
                END,
                role.name,
                CASE WHEN hardware.id > 1
                    THEN CONCAT(org.name, ' ', hardware.name)
                    ELSE hardware.name
                END,
                hardware.size,
                CASE WHEN EXISTS(SELECT os_version FROM device)
                    THEN CONCAT(os.name, ' ', device.os_version)
                    ELSE os.name
                END,
                device.serial_no, device.asset_no, customer.name,
                service.name, device.notes, device.id
            FROM device, rack, role, hardware, os, customer, room,
                building, row, service, domain, org
            WHERE device.rack = rack.id
                AND device.domain = domain.id
                AND rack.row = row.id
                AND row.room = room.id
                AND room.building = building.id
                AND device.hardware = hardware.id
                AND device.role = role.id
                AND device.os = os.id
                AND device.customer = customer.id
                AND device.service = service.id
                AND hardware.manufacturer = org.id
                AND ({} IS NULL OR device.customer = {})
                AND ({} IS NULL OR device.role = {})
                AND ({} IS NULL OR device.hardware = {})
                AND ({} IS NULL OR device.os = {}) ORDER BY {}""".format(
                fltr["customer"], fltr["customer"],
                fltr["role"], fltr["role"],
                fltr["hardware"], fltr["hardware"],
                fltr["os"], fltr["os"], sort
            )
        )
        keys = [
            "name", "domain", "rack", "pos", "room", "building", "role",
            "hardware", "size", "os", "serial", "asset", "customer",
            "service", "notes", "id"
        ]
        devs = [dict(zip(keys, dev)) for dev in cur.fetchall()]
        if sort == "device.name":
            return sorted(devs, key=lambda dct: dct["name"].lower())
        return devs

    @classmethod
    def get_devices_unracked(cls, sort="device.name", fltr={}):
        """Get info on unracked devices."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        fltr = cls.sanitize_filter(fltr)
        cur.execute(
            """SELECT device.name,
                CASE WHEN domain.id>2
                    THEN domain.name
                    ELSE ''
                END,
                building.name, role.name,
                CASE WHEN hardware.id > 1
                    THEN CONCAT(org.name, ' ', hardware.name)
                    ELSE hardware.name
                END,
                CASE WHEN EXISTS(SELECT os_version FROM device)
                    THEN CONCAT(os.name, ' ', device.os_version)
                    ELSE os.name
                END,
                device.serial_no, device.asset_no, customer.name,
                device.purchased, device.notes, device.id
            FROM device, building, rack, role, room, row, hardware,
                os, customer, domain, org
            WHERE building.meta_default_data <> 0
                AND device.meta_default_data = 0
                AND device.domain = domain.id
                AND device.rack = rack.id
                AND rack.row = row.id
                AND row.room = room.id
                AND room.building = building.id
                AND device.hardware = hardware.id
                AND device.role = role.id
                AND device.os = os.id
                AND device.customer = customer.id
                AND hardware.manufacturer = org.id
                AND ({} IS NULL OR device.customer = {})
                AND ({} IS NULL OR device.role = {})
                AND ({} IS NULL OR device.hardware = {})
                AND ({} IS NULL OR device.os = {})
                ORDER BY {}""".format(
                fltr["customer"], fltr["customer"],
                fltr["role"], fltr["role"],
                fltr["hardware"], fltr["hardware"],
                fltr["os"], fltr["os"], sort
            )
        )
        keys = [
            "name", "domain", "building", "role", "hardware", "os", "serial",
            "asset", "customer", "purchased", "notes", "id"
        ]
        devs = [dict(zip(keys, dev)) for dev in cur.fetchall()]
        if sort == "device.name":
            return sorted(devs, key=lambda dct: dct["name"].lower())
        return devs

    @classmethod
    def get_devices_search(cls, sort="device.name", fltr={}, search=""):
        """Get devices based on search."""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.search_connection()
        cur = con.cursor()
        fltr = cls.sanitize_filter(fltr)
        search = search.lower() if search else ""
        if any(char in search for char in [';', '%', '<', '>', '=', "'", '"']):
            raise ValueError
        if fltr:
            cur.execute(
                """SELECT device.name,
                    CASE WHEN domain.id>2
                        THEN domain.name
                        ELSE ''
                    END,
                    rack.name, device.rack_pos,
                    CASE WHEN (room.id<2) OR (building.id<2)
                        THEN ''
                        ELSE room.name
                    END,
                    CASE WHEN LENGTH(building.name_short)>0
                        THEN building.name_short
                        ELSE building.name
                    END,
                    role.name,
                    CASE WHEN hardware.id > 1
                        THEN CONCAT(org.name, ' ', hardware.name)
                        ELSE hardware.name
                    END,
                    CASE WHEN EXISTS(SELECT os_version FROM device)
                        THEN CONCAT(os.name, ' ', device.os_version)
                        ELSE os.name
                    END,
                    device.serial_no, device.asset_no, customer.name,
                    CASE WHEN '-' ~ device.purchased
                        THEN 0
                        ELSE ROUND(EXTRACT(
                                DAY FROM NOW() - device.purchased::timestamp
                            )::numeric / 365, 1)
                    END,
                    device.notes, device.id
                FROM device, rack, role, hardware, os, customer, room,
                    building, row, service, domain, org
                WHERE device.rack = rack.id
                    AND device.domain = domain.id
                    AND rack.row = row.id
                    AND row.room = room.id
                    AND room.building = building.id
                    AND device.hardware = hardware.id
                    AND device.role = role.id
                    AND device.os = os.id
                    AND device.customer = customer.id
                    AND device.service = service.id
                    AND hardware.manufacturer = org.id
                    AND ({} IS NULL OR device.customer = {})
                    AND ({} IS NULL OR device.role = {})
                    AND ({} IS NULL OR device.hardware = {})
                    AND ({} IS NULL OR device.os = {})
                    AND (lower(device.name) LIKE '%{}%'
                        OR lower(device.serial_no) LIKE '%{}%'
                        OR lower(device.asset_no) LIKE '%{}%'
                    ) ORDER BY {}""".format(
                    fltr["customer"], fltr["customer"],
                    fltr["role"], fltr["role"],
                    fltr["hardware"], fltr["hardware"],
                    fltr["os"], fltr["os"],
                    search, search, search, sort
                )
            )
        else:
            cur.execute(
                """SELECT device.name,
                    CASE WHEN domain.id>2
                        THEN domain.name
                        ELSE ''
                    END,
                    rack.name, device.rack_pos,
                    CASE WHEN (room.id<2) OR (building.id<2)
                        THEN ''
                        ELSE room.name
                    END,
                    CASE WHEN LENGTH(building.name_short)>0
                        THEN building.name_short
                        ELSE building.name
                    END,
                    role.name,
                    CASE WHEN hardware.id > 1
                        THEN CONCAT(org.name, ' ', hardware.name)
                        ELSE hardware.name
                    END,
                    CASE WHEN EXISTS(SELECT os_version FROM device)
                        THEN CONCAT(os.name, ' ', device.os_version)
                        ELSE os.name
                    END,
                    device.serial_no, device.asset_no, customer.name,
                    CASE WHEN '-' ~ device.purchased
                        THEN 0
                        ELSE ROUND(EXTRACT(
                                DAY FROM NOW() - device.purchased::timestamp
                            )::numeric / 365, 1)
                    END,
                    device.notes, device.id
                FROM device, rack, role, hardware, os, customer, room,
                    building, row, service, domain, org
                WHERE device.rack = rack.id
                    AND device.domain = domain.id
                    AND rack.row = row.id
                    AND row.room = room.id
                    AND room.building = building.id
                    AND device.hardware = hardware.id
                    AND device.role = role.id
                    AND device.os = os.id
                    AND device.customer = customer.id
                    AND device.service = service.id
                    AND hardware.manufacturer = org.id
                    AND (lower(device.name) LIKE '%{}%'
                        OR lower(device.serial_no) LIKE '%{}%'
                        OR lower(device.asset_no) LIKE '%{}%'
                    ) ORDER BY {}""".format(
                    search, search, search, sort
                )
            )
        keys = [
            "name", "domain", "rack", "pos", "room", "building", "role",
            "hardware", "os", "serial", "asset", "customer", "purchased",
            "notes", "id"
        ]
        devs = [dict(zip(keys, dev)) for dev in cur.fetchall()]
        if sort == "device.name":
            return sorted(devs, key=lambda dct: dct["name"].lower())
        return devs

    @staticmethod
    def update_device(
        dev_id, dev_name, domain, rack_id, rack_pos,
        model, os, version, key, role, in_service, purchased,
        serial, asset, customer, service_level, notes, user
    ):
        """Update device."""
        con = connect.update_connection()
        cur = con.cursor()
        cur.execute(
            """UPDATE device
            SET name = %s,
                domain = %s,
                rack = %s,
                rack_pos = %s,
                hardware = %s,
                os = %s,
                os_version = %s,
                os_licence_key = %s,
                role = %s,
                in_service = %s,
                purchased = %s,
                serial_no = %s,
                asset_no = %s,
                customer = %s,
                service = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """,
            (
                dev_name, domain, rack_id, rack_pos, model, os, version, key,
                role, in_service, purchased, serial, asset, customer,
                service_level, notes, user, dev_id
            )
        )
        con.commit()
        # Update log table.
        sql_log.log("device", dev_id, dev_name, "update", "", user)

    @staticmethod
    def delete_device(dev_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM device WHERE id = %s", (dev_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM device WHERE id = %s", (dev_id,))
        con.commit()
        # Update log table.
        sql_log.log("device", dev_id, name, "delete", "", user)
