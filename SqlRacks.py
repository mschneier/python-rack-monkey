"""Sql operations for rack table."""
import gc
import re
from SqlConnection import SqlConnect as connect
from SqlDevices import SqlDevice as sql_device
from SqlLogging import SqlLog as sql_log
from urllib import parse


class RangeDict(dict):
    def __getitem__(self, item):
        if type(item) != range:
            for key in self:
                if item in key:
                    return self[key]
        else:
            return super().__getitem__(item)


class SqlRack:
    """Rack sql functions."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def add_new_rack(rack_name, room, size, order, notes, user):
        """Insert new rack."""
        con = connect.insert_connection()
        cur = con.cursor()
        # Row is based on room id.
        cur.execute(
            """SELECT DISTINCT row.id
            FROM rack, room, row
            WHERE row.room = room.id
                AND rack.row = row.id
                AND room.id = %s
            """, (room,)
        )
        row = cur.fetchone()[0]
        if not row:
            raise ValueError
        cur.execute(
            """INSERT INTO rack (
                name, row, row_pos, size, numbering_direction, notes,
                meta_update_time, meta_update_user
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (
                rack_name, row, 0, size, order, notes, user
            )
        )
        con.commit()
        # Update log table.
        sql_log.log("rack", "", rack_name, "insert", "", user)

    @staticmethod
    def get_rack_info(rack_id):
        """Get info on rack for copy."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT rack.name, room.id, rack.size,
                rack.numbering_direction, rack.notes
            FROM rack, room, row
            WHERE row.room = room.id
                AND rack.row = row.id
                AND rack.id = %s
            """, (rack_id,)
        )
        rack = cur.fetchone()
        return rack

    @staticmethod
    def get_nearest_rack_by_id(rack_id):
        """Get id, name of nearest rack by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM rack ORDER BY ABS(id - %s) LIMIT 1",
            (rack_id,)
        )
        rack = cur.fetchone()
        return rack

    @staticmethod
    def sanitize(value):
        """HTML sanitize value."""
        value = value.replace("&", "&amp;").replace(
            "<", "&lt;").replace(">", "&gt;")
        return value

    @staticmethod
    def get_acceptable_sorts():
        """Return column names from tables used."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT CONCAT(table_name, '.', column_name)
            FROM information_schema.columns WHERE table_name
                IN ('rack', 'row', 'room')"""
        )
        sorts = [sort[0] for sort in cur.fetchall()]
        sorts.append("device_count")
        sorts.append("free_space")
        return sorts

    @classmethod
    def get_all_racks(cls, sort="rack.name"):
        """Query for all racks"""
        if sort not in cls.get_acceptable_sorts():
            raise ValueError
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT rack.*,
                row.name AS row_name,
                row.hidden_row AS row_hidden,
                room.id AS room,
                room.name AS room_name,
                building.name AS building_name,
                building.name_short AS building_name_short,
                count(device.id) AS device_count,
                rack.size - COALESCE(SUM(hardware.size), 0) AS free_space
            FROM row, room, building, rack
            LEFT OUTER JOIN device ON (rack.id = device.rack)
            LEFT OUTER JOIN hardware ON (device.hardware = hardware.id)
            WHERE rack.meta_default_data = 0
                AND rack.row = row.id
                AND row.room = room.id
                AND room.building = building.id
            GROUP BY rack.id, rack.name, rack.row, rack.row_pos,
                rack.hidden_rack, rack.size, rack.numbering_direction,
                rack.notes, rack.meta_default_data, rack.meta_update_time,
                rack.meta_update_user, row.name, row.hidden_row, room.id,
                room.name, building.name, building.name_short
            ORDER BY %s""" % (sort,))
        racks = cur.fetchall()
        racks = [list(rack) for rack in racks]
        for rack in racks:
            if "Wolfram" in rack[15]:
                rack[15] = "WRI"
        return racks

    @staticmethod
    def get_one_rack_normal_view(rack_id):
        """Show info on one rack normal view."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT rack.*, row.name, row.hidden_row, room.id, room.name,
                building.name, building.name_short, count(device.id),
                rack.size - COALESCE(SUM(hardware.size), 0)
            FROM row, room, building, rack
            LEFT OUTER JOIN device ON (rack.id = device.rack)
            LEFT OUTER JOIN hardware ON (device.hardware = hardware.id)
            WHERE rack.row = row.id
                AND row.room = room.id
                AND room.building = building.id
                AND rack.id > 5
                AND rack.id = %s
            GROUP BY rack.id, rack.name, rack.row, rack.row_pos,
                rack.hidden_rack, rack.numbering_direction, rack.size,
                rack.notes, rack.meta_default_data, rack.meta_update_time,
                rack.meta_update_user, row.name, row.hidden_row, room.id,
                room.name, building.name, building.name_short""",
            (rack_id,)
        )
        try:
            rack = list(cur.fetchone())
            if "Wolfram" in rack[15]:
                rack[15] = "WRI"
            # Format rack notes.
            if rack[7]:
                notes = rack[7]
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
                            dev_id = parse.parse_qs(parsed.query)[
                                "device_id"][0]
                            url = f"/view/racks/list/simple/?rack_list={id}&selected_dev={dev_id}"
                    link = "<a href='{}'>{}</a>".format(url, link_text)
                    notes = re.sub(r"\[.*?\]", link, notes, count=1)
                rack[7] = notes
            return rack
        except TypeError:
            return ""

    @staticmethod
    def get_occupied_slots(rack_id):
        """Get occupied slots in rack by id."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT device.rack_pos, hardware.size, rack.size
            FROM device, hardware, rack
            WHERE device.rack = rack.id
                AND rack.id = %s
                AND device.hardware = hardware.id
            """, (rack_id,)
        )
        slots = cur.fetchall()
        pos_dict = {}
        occupied = []
        try:
            rack_size = int(slots[0][2])
            for slot in slots:
                pos = slot[0]
                size = slot[1]
                pos_dict.update({
                    range(pos, pos + size): {
                        size
                    }
                })
            pos_dict = RangeDict(pos_dict)
            for row in range(1, rack_size + 1):
                if pos_dict[row]:
                    occupied.append(str(row))
        except IndexError:
            occupied.append(0)
        return occupied

    @staticmethod
    def get_all_rack_ids():
        """Return all rack id's."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT rack.id FROM rack")
        ids = [str(rack_id[0]) for rack_id in cur.fetchall()]
        return ids

    @classmethod
    def get_one_rack_summary_list_view(cls, rack_id, selected_dev):
        """List summary info of devices in rack."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT rack.size, device.name, hardware.size, device.rack_pos,
                hardware.name, rack.numbering_direction, rack.name,
                rack.id, room.name, device.id, org.name
            FROM rack, device, hardware, org, room, row
            WHERE device.rack = rack.id
                AND rack.id = %s
                AND device.hardware = hardware.id
                AND hardware.manufacturer = org.id
                AND rack.row = row.id
                AND row.room = room.id
            ORDER BY device.rack_pos""", (rack_id,)
        )
        info = cur.fetchall()
        try:
            rack_size = int(info[0][0])
        except IndexError:
            return ""
        num_dir = "top" if int(info[0][5]) else "bottom"
        rack_name = info[0][6]
        rack_id = info[0][7]
        room = info[0][8]
        # Position of all devices in rack.
        if num_dir == "top":
            rack_poses = [int(row[3]) for row in info]
        else:
            # If starting from bottom, add size-1 to get last pos used by dev.
            rack_poses = [int(row[3]) + int(row[2]) - 1 for row in info]
        # Build dict of positions that are occupied.
        devices = [(row[1], row[2], row[3], row[4], row[9], row[10])
                   for row in info]
        dev_dict = {}
        for device in devices:
            name = cls.sanitize(device[0])
            size = device[1]
            rack_pos = device[2]
            hardware = device[3]
            dev_id = str(device[4])
            manufacturer = device[5]
            dev_dict.update({
                range(rack_pos, rack_pos + size): {
                    "name": name, "size": size, "id": dev_id,
                    "pos": rack_pos, "hardware": hardware,
                    "manufacturer": manufacturer
                }
            })
        dev_dict = RangeDict(dev_dict)
        # Build html td strings for each row # in rack.
        row_data = ["<td class='row_num'>{}</td>".format(row)
                    for row in range(1, rack_size + 1)]
        # Build html td strings for devs in rack.
        not_in_service = sql_device().get_not_in_service_names()
        dev_data = []
        for row in range(1, rack_size + 1):
            if dev_dict[row]:
                if row in rack_poses:
                    name = dev_dict[row]["name"]
                    dev_id = dev_dict[row]["id"]
                    manufacturer = dev_dict[row]["manufacturer"].replace(
                        "'", "&#39;"
                    )
                    size = dev_dict[row]["size"]
                    hardware = dev_dict[row]["hardware"].replace(
                        "'", "&#39;"
                    )
                    if dev_id == selected_dev:
                        dev_class = "selected_dev"
                    elif name in not_in_service:
                        dev_class = "not_in_service"
                    else:
                        dev_class = "occupied"
                    dev_data.append(
                        """<td rowspan='{}' class='{}'>
                            <a href='/view/devices/one/{}'>{}</a>
                            <span title='{}'> ({}) </span>
                        </td>""".format(
                            size, dev_class, dev_id, name,
                            f"Hardware: {manufacturer} - {hardware}", hardware
                        )
                    )
                else:
                    dev_data.append("")
            else:
                dev_data.append(f"""
                <td>
                    <a href='/add/device/new/?pos={row}&sel_rack={rack_id}'>
                        <img src="/static/pictures/edit/add_circle.png"
                          alt="Add Device in rack {rack_name} in slot {row}"
                          title="Add Device in rack {rack_name} in slot {row}"
                          class="edit_pic">
                    </a>
                </td>
                """)
        # Reverse data if numbered from bottom.
        if num_dir == "bottom":
            row_data.reverse()
            dev_data.reverse()
        table = ""
        for row in range(rack_size):
            table += "<tr>{}{}</tr>".format(row_data[row], dev_data[row])
        return table, rack_name, rack_id, room

    @classmethod
    def get_one_rack_extended_list_view(cls, rack_id):
        """List summary info of devices in rack."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT rack.size, device.name, hardware.size, device.rack_pos,
                hardware.name, rack.numbering_direction, rack.name,
                rack.id, room.name, device.id, customer.name, role.name,
                device.serial_no, device.asset_no
            FROM rack, device, hardware, room, row, customer, role
            WHERE device.rack = rack.id
                AND rack.id = %s
                AND device.hardware = hardware.id
                AND rack.row = row.id
                AND row.room = room.id
                AND device.customer = customer.id
                AND device.role = role.id
            ORDER BY device.rack_pos""", (rack_id,)
        )
        info = cur.fetchall()
        try:
            rack_size = int(info[0][0])
        except IndexError:
            return ""
        num_dir = "top" if int(info[0][5]) else "bottom"
        rack_name = info[0][6]
        rack_id = info[0][7]
        room = info[0][8]
        # Position of all devices in rack.
        if num_dir == "top":
            rack_poses = [int(row[3]) for row in info]
        else:
            # If starting from bottom, add size-1 to get last pos used by dev.
            rack_poses = [int(row[3]) + int(row[2]) - 1 for row in info]
        # Build dict of positions that are occupied.
        devices = [(
            row[1], row[2], row[3], row[4], row[9],
            row[10], row[11], row[12], row[13]
        ) for row in info]
        dev_dict = {}
        for device in devices:
            name = cls.sanitize(device[0])
            size = device[1]
            rack_pos = device[2]
            hardware = device[3]
            dev_id = str(device[4])
            customer = device[5]
            role = device[6]
            serial = cls.sanitize(device[7]) if device[7] else "N/A"
            asset = cls.sanitize(device[8]) if device[8] else "N/A"
            dev_dict.update({
                range(rack_pos, rack_pos + size): {
                    "name": name, "size": size, "id": dev_id,
                    "pos": rack_pos, "hardware": hardware,
                    "customer": customer, "role": role,
                    "serial": serial, "asset": asset
                }
            })
        dev_dict = RangeDict(dev_dict)
        # Build html td strings for each row # in rack.
        row_data = ["<td class='row_num'>{}</td>".format(row)
                    for row in range(1, rack_size + 1)]
        # Build html td strings for devs in rack.
        not_in_service = sql_device().get_not_in_service_names()
        dev_data = []
        for row in range(1, rack_size + 1):
            if dev_dict[row]:
                if row in rack_poses:
                    name = dev_dict[row]["name"]
                    if name in not_in_service:
                        dev_data.append(
                            """<td rowspan='{}' class='not_in_service'>
                                <a href='/view/devices/one/{}'>{}</a> ({}) -
                                Customer: {} - Role: {} - Serial: {} - Asset: {}
                            </td>""".format(
                                dev_dict[row]["size"], dev_dict[row]["id"],
                                dev_dict[row]["name"], dev_dict[row]["hardware"],
                                dev_dict[row]["customer"], dev_dict[row]["role"],
                                dev_dict[row]["serial"], dev_dict[row]["asset"]
                            )
                        )
                    else:
                        dev_data.append(
                            """<td rowspan='{}' class='occupied'>
                                <a href='/view/devices/one/{}'>{}</a> ({}) -
                                Customer: {} - Role: {} - Serial: {} - Asset: {}
                            </td>""".format(
                                dev_dict[row]["size"], dev_dict[row]["id"],
                                dev_dict[row]["name"], dev_dict[row]["hardware"],
                                dev_dict[row]["customer"], dev_dict[row]["role"],
                                dev_dict[row]["serial"], dev_dict[row]["asset"]
                            )
                        )
                else:
                    dev_data.append("")
            else:
                dev_data.append("<td></td>")
        # Reverse data if numbered from bottom.
        if num_dir == "bottom":
            row_data.reverse()
            dev_data.reverse()
        table = ""
        for row in range(rack_size):
            table += "<tr>{}{}</tr>".format(row_data[row], dev_data[row])
        return table, rack_name, rack_id, room

    @staticmethod
    def update_rack(rack_id, rack_name, room, size, order, notes, user):
        """Insert new rack."""
        con = connect.update_connection()
        cur = con.cursor()
        # Row is based on room id.
        cur.execute(
            """SELECT DISTINCT row.id
            FROM rack, room, row
            WHERE row.room = room.id
                AND rack.row = row.id
                AND room.id = %s
            """, (room,)
        )
        row = cur.fetchone()[0]
        if not row:
            raise ValueError
        cur.execute(
            """UPDATE rack
            SET name = %s,
                row = %s,
                row_pos = 0,
                size = %s,
                numbering_direction = %s,
                notes = %s,
                meta_update_time = DATE_TRUNC('second', NOW()::timestamp),
                meta_update_user = %s
            WHERE id = %s
            """, (rack_name, row, size, order, notes, user)
        )
        con.commit()
        # Update log table.
        sql_log.log("rack", rack_id, rack_name, "update", "", user)

    @staticmethod
    def delete_rack(rack_id, user):
        """Delete by id."""
        con = connect.delete_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM rack WHERE id = %s", (rack_id,))
        name = cur.fetchone()[0]
        cur.execute("DELETE FROM rack WHERE id = %s", (rack_id,))
        con.commit()
        # Update log table.
        sql_log.log("rack", rack_id, name, "delete", "", user)
