"""Sql operations for generating reports."""
import gc
from SqlConnection import SqlConnect as connect


class SqlReport():
    """Main class for making sql queries."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def get_num_racks_and_size():
        """Get # of racks and their total size."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT SUM(size) FROM rack WHERE id > 5"""
        )
        size = cur.fetchone()[0]
        cur.execute(
            """SELECT COUNT(name) FROM rack WHERE id > 5"""
        )
        num = cur.fetchone()[0]
        return num, size

    @staticmethod
    def get_num_devices():
        """Get # of devs."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT COUNT(name) FROM device"""
        )
        num = cur.fetchone()[0]
        return num

    @staticmethod
    def get_size_of_devices():
        """Get size of all racked devs."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT SUM(hardware.size)
            FROM device, building, rack, role, room, row, hardware,
                os, customer, domain
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
                AND device.customer = customer.id"""
        )
        unrackedSize = int(cur.fetchone())
        cur.execute(
            """SELECT SUM(hardware.size) FROM device, hardware
            WHERE device.hardware = hardware.id"""
        )
        totalSize = int(cur.fetchone())
        rackedSize = totalSize - unrackedSize
        return rackedSize

    @staticmethod
    def get_top_customer_count():
        """Get # of devices and size used by top ten customers."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT COUNT(customer.name), customer.name, SUM(hardware.size),
                customer.id
            FROM customer, device, hardware
            WHERE device.customer = customer.id
                AND device.hardware = hardware.id
            GROUP BY customer.name, customer.id
            ORDER BY 1 DESC
            LIMIT 10"""
        )
        customers = cur.fetchall()
        return customers

    @staticmethod
    def get_top_role_count():
        """Get # of devices and size used in top ten roles."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT COUNT(role.name), role.name, SUM(hardware.size), role.id
            FROM role, device, hardware
            WHERE device.role = role.id
                AND device.hardware = hardware.id
            GROUP BY role.name, role.id
            ORDER BY 1 DESC
            LIMIT 10"""
        )
        roles = cur.fetchall()
        return roles

    @staticmethod
    def get_top_hardware_count():
        """Get # of devices and size used in top ten hardware models."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT COUNT(device.name), hardware.name, SUM(hardware.size),
                hardware.id
            FROM device, hardware
            WHERE device.hardware = hardware.id
            GROUP BY hardware.name, hardware.id
            ORDER BY 1 DESC
            LIMIT 10"""
        )
        hardwares = cur.fetchall()
        return hardwares

    @staticmethod
    def get_top_os_count():
        """Get # of devices and size used with top ten os versions."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT COUNT(os.name), CONCAT(os.name, ' ', device.os_version),
                SUM(hardware.size), os.id
            FROM os, device, hardware
            WHERE device.os = os.id
                AND device.hardware = hardware.id
            GROUP BY os.name, os.id, device.os_version
            ORDER BY 1 DESC
            LIMIT 10"""
        )
        oses = cur.fetchall()
        return oses

    @staticmethod
    def get_dup_serials():
        """Get devices w/ same serial #."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT device.serial_no,
                CASE WHEN hardware.id > 1
                    THEN CONCAT(org.name, ' ', hardware.name)
                    ELSE hardware.name
                END, device.name, device.id
            FROM device, hardware, org
            WHERE device.hardware = hardware.id
                AND hardware.manufacturer = org.id
                AND LENGTH(device.serial_no) > 0
                AND device.serial_no IN (
                    SELECT device.serial_no FROM device
                    GROUP BY device.serial_no HAVING COUNT(*) > 1
                )
            ORDER BY device.serial_no, device.name
            """
        )
        serials = cur.fetchall()
        return serials

    @staticmethod
    def get_dup_assets():
        """Get devices w/ same asset #."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT device.asset_no,
                CASE WHEN hardware.id > 1
                    THEN CONCAT(org.name, ' ', hardware.name)
                    ELSE hardware.name
                END, device.name, device.id
            FROM device, hardware, org
            WHERE device.hardware = hardware.id
                AND hardware.manufacturer = org.id
                AND LENGTH(device.asset_no) > 0
                AND device.asset_no IN (
                    SELECT device.asset_no FROM device
                    GROUP BY device.asset_no HAVING COUNT(*) > 1
                )
            ORDER BY device.asset_no, device.name
            """
        )
        assets = cur.fetchall()
        return assets

    @staticmethod
    def get_dup_licence_keys():
        """Get devices w/ same licence #."""
        con = connect.query_connection()
        cur = con.cursor()
        cur.execute(
            """SELECT device.asset_no,
                CASE WHEN hardware.id > 1
                    THEN CONCAT(org.name, ' ', hardware.name)
                    ELSE hardware.name
                END, device.name, device.id
            FROM device, hardware, org
            WHERE device.hardware = hardware.id
                AND hardware.manufacturer = org.id
                AND LENGTH(device.asset_no) > 0
                AND device.asset_no IN (
                    SELECT device.asset_no FROM device
                    GROUP BY device.asset_no HAVING COUNT(*) > 1
                )
            ORDER BY device.asset_no, device.name
            """
        )
        keys = cur.fetchall()
        return keys
