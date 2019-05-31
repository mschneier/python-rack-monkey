"""Python files that does the computation."""
from datetime import datetime, timedelta
import gc
import ldap3
import json
import os
import pytz


class EmployeeLookup:
    """Main class for searching for employee info."""

    def __init__(self):
        """Initialize."""
        gc.enable()  # Enable garbage collection.
        pass

    @staticmethod
    def placeholders():
        """For VPN return empty string."""
        return ""

    @staticmethod
    def check_ldap_server():
        """Make ldap connection."""
        ldap_server = ldap3.Server(
            os.environ["LDAP_SERVER"], use_ssl=True, get_info=True, port=636
        )
        ldap_connection = ldap3.Connection(ldap_server, auto_bind=True)
        return ldap_server, ldap_connection

    @classmethod
    def ldap_lookup(cls, user, attrib):
        """Search for employee information contained in LDAP."""
        connection = cls.check_ldap_server()[1]
        # Search if user has attribute.
        connection.search(
            os.environ["LDAP_BASE"],
            f"(&(objectclass=person)(uid={user}))",
            attributes=attrib
        )
        # Get first part of response.
        try:
            entry = connection.entries[0].entry_to_json()
        except IndexError:
            return "User doesn't exist."
        # Convert from json to string.
        entry = json.loads(entry)
        # Try to return result.
        try:
            return entry["attributes"][attrib][0]
        # If there is no result.
        except IndexError:
            return ""

    @classmethod
    def ldap_password_checker(cls, user, passwd):
        """Check if password matches for password_checker_result page."""
        server = cls.check_ldap_server()[0]
        # Form full hierachal directory.
        user = f"uid={user}," + os.environ["LDAP_BASE"]
        # Try to connect to server with user's credentials.
        try:
            ldap3.Connection(
                server, auto_bind=True, user=user,
                password=passwd.encode("utf-8")
            )
            return True
        except ldap3.core.exceptions.LDAPBindError:
            return False
