#!/var/www/html/rack/rackTest/bin/python3.6
import os
import sys

sys.path.insert(0, "/var/www/html/rack/")
sys.path.insert(0, "/var/www/html/rack/rackTest/lib/python3.6/site-packages/")


def application(req_environ, start_response):
    for key in [
        "FLASK_SECRET_KEY", "LDAP_BASE", "LDAP_SERVER",
        "PSQL_SEARCH_USER_PASS", "PSQL_QUERY_USER_PASS",
        "PSQL_UPDATE_USER_PASS", "PSQL_DELETE_USER_PASS",
        "PSQL_LOGGING_USER_PASS", "PSQL_INSERT_USER_PASS"
    ]:
        os.environ[key] = req_environ.get(key, "")
    from app import application as _application
    return _application(req_environ, start_response)
