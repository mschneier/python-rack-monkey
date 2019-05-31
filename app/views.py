"""Directs users to webpages and renders templates."""
from app import application as app
from bleach import clean
from email.message import EmailMessage
from flask import abort, flash, jsonify, Markup, redirect
from flask import render_template, request, session
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_paranoid import Paranoid
from .forms import AppForm, AppRelationForm, BuildingForm, AddDeviceForm
from .forms import DeleteForm, DomainForm, HardwareForm, LoginForm, OrgForm
from .forms import OsForm, RackForm, RoleForm, RoomForm, ServiceForm
from .forms import UpdateDeviceForm
from functools import wraps
from jinja2 import Environment, select_autoescape
import os
import psycopg2
from smtplib import SMTP
from werkzeug.contrib.fixers import ProxyFix
from EmployeeLookup import EmployeeLookup as lookup
from SqlApps import SqlApp as sql_app
from SqlBuildings import SqlBuilding as sql_building
from SqlConnection import SqlConnect as sql_connect
from SqlDevices import SqlDevice as sql_device
from SqlDomains import SqlDomain as sql_domain
from SqlHardwares import SqlHardware as sql_hardware
from SqlOrgs import SqlOrg as sql_org
from SqlOses import SqlOs as sql_os
from SqlRacks import SqlRack as sql_rack
from SqlReports import SqlReport as sql_report
from SqlRoles import SqlRole as sql_role
from SqlRooms import SqlRoom as sql_room
from SqlServices import SqlService as sql_service


# Get correct remote address from client.
app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)

# Gzip compress app.
compress = Compress(app)

# Limit requests by ip.
limiter = Limiter(
    app,
    key_func=get_remote_address,
)
RATE_LIMIT = "10 per minute"

# Session expiry time (3 days).
EXPIRY = 60 * 60 * 24 * 3

# Escape all form variables.
env = Environment(autoescape=True)

# Set secret key.
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
app.config["SESSION_COOKIE_SECURE"] = True

# Beef up security with Paranoid.
paranoid = Paranoid(app)
paranoid.redirect_view = "/"


def is_logged_in(f):
    """Check if user has logged in."""
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized. Please login.", category="danger")
            return redirect("/login")
    return wrap


def loginUser(username):
    """Login user."""
    # Automatically logout user in 3 days.
    session.permanent = True
    app.permanent_session_lifetime = EXPIRY
    session["logged_in"] = True
    session["username"] = username
    session["ip"] = request.environ["REMOTE_ADDR"]
    # Create message to flash.
    msg = "You are logged in " + username + "."
    return msg


@app.before_request
def before_request():
    """Renew session for every request."""
    # Renew session expire time when loading page.
    if "logged_in" in session:
        session.modified = True


@app.route("/")
def home():
    """Home page."""
    if "logged_in" in session:
        return redirect("/view/devices")
    else:
        return redirect("/login")


@app.route("/login/", methods=["GET", "POST"])
@limiter.limit(RATE_LIMIT)
def login():
    """Login page."""
    loginForm = LoginForm()
    if loginForm.validate_on_submit() and request.method == "POST":
        employee = request.form["username"].replace(" ", "")
        passwd = request.form["password"]

        LDAP = lookup.ldap_password_checker(employee, passwd)
        if LDAP:
            # If in right department.
            dept = lookup.ldap_lookup(employee, "departmentNumber")
            if ".EXEC" in dept or ".IT" in dept:
                msg = loginUser(employee)
                flash(msg, category="success")
                return redirect("/")
            else:
                flash("Not authorized.", category="danger")
                return redirect("/login/")
        # Bad attempt.
        else:
            flash("Bad username or password.", category="danger")
            return render_template(
                "login.html",
                title="Login",
                form=loginForm
            )
    # Page before submit.
    return render_template(
        "login.html",
        title="Login",
        form=loginForm,
    )


@is_logged_in
@app.route("/logout/")
def logout():
    """Logout user."""
    session.clear()
    flash("You are now logged out.", category="info")
    return redirect("/")


def display_devices(view):
    """Retrieve device info based on view."""
    customer = request.args.get("customer")
    role = request.args.get("role")
    hardware = request.args.get("hardware")
    os = request.args.get("os")
    try:
        customer = int(customer)\
            if customer and customer != "null" else customer
        role = int(role) if role and role != "null" else role
        hardware = int(hardware)\
            if hardware and hardware != "null" else hardware
        os = int(os) if os and os != "null" else os
    except ValueError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable filter."
        ), 400
    search = request.args.get("search")
    fltr = {
        "customer": customer,
        "role": role,
        "hardware": hardware,
        "os": os,
    }
    sort = request.args.get("sort")
    if not sort or sort == "null":
        sort = "device.name"
    try:
        if view == "default":
            devices = sql_device.get_devices(sort, fltr)
        elif view == "asset":
            devices = sql_device.get_devices_asset(sort, fltr)
        elif view == "extended":
            devices = sql_device.get_devices_extended(sort, fltr)
        elif view == "unracked":
            devices = sql_device.get_devices_unracked(sort, fltr)
        else:
            try:
                devices = sql_device.get_devices_search(
                    sort, fltr, search)
            except ValueError:
                return render_template(
                    "error_pages/400.html",
                    title="400",
                    msg="Unacceptable search."
                ), 400
        not_in_service = sql_device.get_not_in_service_names()
    except ValueError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    if view == "search":
        lenDevices = len(sql_device.get_devices_search(sort, {}, search))
    else:
        lenDevices = sql_device.get_no_devices()
    return render_template(
        "views/devices/%s.html" % (view),
        title="Devices: %s View" % (view.capitalize()),
        devices=devices,
        customers=sql_device.get_customers(),
        roles=sql_device.get_roles(),
        hardwares=sql_device.get_hardware(),
        oses=sql_device.get_os(),
        lenDevices=len(devices),
        lenAllDevices=lenDevices,
        not_in_service=not_in_service,
    )


@is_logged_in
@app.route("/view/devices/")
@app.route("/view/devices/default/")
def display_devices_default():
    """Show devices default view."""
    return display_devices("default")


@is_logged_in
@app.route("/view/devices/asset/")
def display_devices_asset():
    """Show device asset view."""
    return display_devices("asset")


@is_logged_in
@app.route("/view/devices/extended/")
def display_devices_extended():
    """Show device extended view."""
    return display_devices("extended")


@is_logged_in
@app.route("/view/devices/unracked/")
def display_devices_unracked():
    """Show device unracked view."""
    return display_devices("unracked")


@is_logged_in
@app.route("/view/devices/search/")
def display_devices_search():
    """Show searched for devices."""
    return display_devices("search")


@is_logged_in
@app.route("/view/devices/one/<int:dev_id>")
def display_one_device(dev_id):
    """Show info on one device based on id."""
    try:
        dev = sql_device.get_device(dev_id)
        dev["notes"] = clean(
            dev["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No app with this id",
        )
    return render_template(
        "views/devices/single_dev.html",
        device=dev,
        title="Device #%s" % (dev_id)
    )


@is_logged_in
@app.route("/view/racks/")
@app.route("/view/racks/all/")
def display_all_racks():
    """Show racks."""
    sort = request.args.get("sort")\
        if request.args.get("sort") else "rack.name"
    try:
        racks = sql_rack.get_all_racks(sort)
    except ValueError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    return render_template(
        "views/racks/all_racks.html",
        racks=racks,
        title="Racks: All",
        lenRacks=len(racks),
    )


@is_logged_in
@app.route("/view/racks/one/normal/<int:rack_id>")
def display_one_rack_normal(rack_id):
    """Show one rack normal view."""
    rack = list(sql_rack.get_one_rack_normal_view(rack_id))
    if rack:
        rack[7] = clean(rack[7], tags=["a", "b", "br", "em", "i"], strip=True)
    return render_template(
        "views/racks/single_rack.html",
        rack=rack,
        title="Rack #%s" % (rack_id),
    )


@is_logged_in
@app.route("/view/racks/list/simple/")
def display_rack_simple_list():
    """Show rack(s) simple device list."""
    selected_dev = request.args.get("selected_dev")
    rack_list = request.args.get("rack_list")
    try:
        rack_list = [int(rack) for rack in rack_list.split(",") if rack]
    except ValueError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Rack ids should be numeric."
        ), 400
    racks = []
    for rack in rack_list:
        try:
            table, rack_name, rack_id, room = sql_rack(
            ).get_one_rack_summary_list_view(rack, selected_dev)
            racks.append({
                "table": Markup(table), "rack_name": rack_name,
                "id": rack_id, "room": room
            })
        except ValueError:
            continue
    title = "Racks"
    for rack in rack_list:
        title += " #%s" % (rack)
    return render_template(
        "views/racks/rack_dev_list.html",
        racks=racks,
        title=title
    )


@is_logged_in
@app.route("/view/racks/list/extended/<int:rack_id>")
def display_rack_extended(rack_id):
    """Show rack w/ extended dev info."""
    racks = []
    try:
        table, rack_name, rack_id, room = sql_rack(
        ).get_one_rack_extended_list_view(rack_id)
        racks.append({
            "table": Markup(table), "rack_name": rack_name,
            "id": rack_id, "room": room
        })
    except ValueError:
        racks = []
    return render_template(
        "views/racks/rack_dev_list.html",
        racks=racks,
        title="Rack #%s" % (str(rack_id))
    )


@is_logged_in
@app.route("/view/apps/")
@app.route("/view/apps/all/")
def display_all_apps():
    """Show all apps."""
    sort = request.args.get("sort") if request.args.get("sort") else "app.name"
    try:
        apps = sql_app.get_all_apps(sort)
    except ValueError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    return render_template(
        "views/apps/all_apps.html",
        apps=apps,
        apps_len=len(apps),
        title="Apps"
    )


@is_logged_in
@app.route("/view/apps/single/<int:app_id>")
def display_one_app(app_id):
    """Show info on one app."""
    try:
        app = sql_app.get_one_app(app_id)
        app["notes"] = clean(
            app["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No app with this id",
        )
    return render_template(
        "views/apps/single_app.html",
        app=app,
        title=f"App #{str(app_id)}"
    )


@is_logged_in
@app.route("/view/config/")
def display_config_tables():
    """Show table of config tables."""
    return render_template("/views/config.html", title="Config Tables")


@is_logged_in
@app.route("/view/buildings/")
@app.route("/view/buildings/all/")
def display_all_buildings():
    """Show all buildings."""
    sort = request.args.get("sort") if request.args.get(
        "sort") else "building.name"
    try:
        buildings = sql_building.get_all_buildings(sort)
    except ValueError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    buildings = sql_building.get_all_buildings(sort)
    return render_template(
        "/views/buildings/all_buildings.html",
        buildings=buildings,
        buildings_len=len(buildings),
        title="Buildings"
    )


@is_logged_in
@app.route("/view/buildings/single/<int:build_id>")
def display_one_building(build_id):
    """Show info on one app."""
    try:
        building = sql_building.get_one_building(build_id)
        building["notes"] = clean(
            building["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No building with this id",
        )
    return render_template(
        "views/buildings/single_building.html",
        building=building,
        title=f"Building #{str(build_id)}"
    )


@is_logged_in
@app.route("/view/rooms/")
@app.route("/view/rooms/all/")
def display_all_rooms():
    """Show all rooms."""
    sort = request.args.get("sort") if request.args.get(
        "sort") else "room.name"
    try:
        rooms = sql_room.get_all_rooms(sort)
    except Exception:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    rooms = sql_room.get_all_rooms(sort)
    return render_template(
        "/views/rooms/all_rooms.html",
        rooms=rooms,
        rooms_len=len(rooms),
        title="Rooms"
    )


@is_logged_in
@app.route("/view/rooms/single/<int:room_id>")
def display_one_room(room_id):
    """Show info on one room."""
    try:
        room = sql_room.get_one_room(room_id)
        room["notes"] = clean(
            room["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No room with this id",
        )
    return render_template(
        "views/rooms/single_room.html",
        room=room,
        title=f"Room #{str(room_id)}"
    )


@is_logged_in
@app.route("/view/domains/")
@app.route("/view/domains/all/")
def display_all_domains():
    """Show all domains."""
    sort = request.args.get("sort") if request.args.get(
        "sort") else "domain.name"
    try:
        domains = sql_domain.get_all_domains(sort)
    except Exception:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    return render_template(
        "/views/domains/all_domains.html",
        domains=domains,
        domains_len=len(domains),
        title="Domains"
    )


@is_logged_in
@app.route("/view/domains/single/<int:domain_id>")
def display_one_domain(domain_id):
    """Show info on one room."""
    try:
        domain = sql_domain.get_one_domain(domain_id)
        domain["notes"] = clean(
            domain["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except ValueError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No domain with this id",
        )
    return render_template(
        "views/domains/single_domain.html",
        domain=domain,
        title=f"Domain #{str(domain_id)}"
    )


@is_logged_in
@app.route("/view/hardware/")
@app.route("/view/hardware/all/")
def display_all_hardware():
    """Show all domains."""
    sort = request.args.get("sort") if request.args.get(
        "sort") else "hardware.name"
    try:
        hardwares = sql_hardware.get_all_hardware(sort)
    except Exception:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    return render_template(
        "/views/hardware/all_hardware.html",
        hardwares=hardwares,
        hardwares_len=len(hardwares),
        title="Hardware"
    )


@is_logged_in
@app.route("/view/hardware/single/<int:hardware_id>")
def display_one_hardware(hardware_id):
    """Show info on one hardware model."""
    try:
        hardware = sql_hardware.get_one_hardware(hardware_id)
        hardware["notes"] = clean(
            hardware["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No hardware with this id",
        )
    return render_template(
        "views/hardware/single_hardware.html",
        hardware=hardware,
        title=f"Hardware #{str(hardware_id)}"
    )


@is_logged_in
@app.route("/view/oses/")
@app.route("/view/oses/all/")
def display_all_oses():
    """Show all oses."""
    sort = request.args.get("sort") if request.args.get(
        "sort") else "os.name"
    try:
        oses = sql_os.get_all_oses(sort)
    except Exception:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    return render_template(
        "/views/oses/all_oses.html",
        oses=oses,
        oses_len=len(oses),
        title="Oses"
    )


@is_logged_in
@app.route("/view/oses/single/<int:os_id>")
def display_one_os(os_id):
    """Show info on one os."""
    try:
        os = sql_os.get_one_os(os_id)
        os["name"] = clean(
            os["name"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No os with this id",
        )
    return render_template(
        "views/oses/single_os.html",
        os=os,
        title=f"OS #{str(os_id)}"
    )


@is_logged_in
@app.route("/view/orgs/")
@app.route("/view/orgs/all/")
def display_all_orgs():
    """Show all orgs."""
    sort = request.args.get("sort") if request.args.get(
        "sort") else "org.name"
    try:
        orgs = sql_org.get_all_orgs(sort)
    except Exception:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    return render_template(
        "views/orgs/all_orgs.html",
        orgs=orgs,
        orgs_len=len(orgs),
        title="Orgs"
    )


@is_logged_in
@app.route("/view/orgs/single/<int:org_id>")
def display_one_org(org_id):
    """Show info on one org."""
    try:
        org = sql_org.get_one_org(org_id)
        org["notes"] = clean(
            org["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No org with this id",
        )
    return render_template(
        "views/orgs/single_org.html",
        org=org,
        title=f"Org #{str(org_id)}"
    )


@is_logged_in
@app.route("/view/roles/")
@app.route("/view/roles/all/")
def display_all_roles():
    """Show all roles."""
    sort = request.args.get("sort") if request.args.get(
        "sort") else "role.name"
    try:
        roles = sql_role.get_all_roles(sort)
    except ValueError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    return render_template(
        "views/roles/all_roles.html",
        roles=roles,
        roles_len=len(roles),
        title="Roles"
    )


@is_logged_in
@app.route("/view/roles/single/<int:role_id>")
def display_one_role(role_id):
    """Show info on one role."""
    try:
        role = sql_role.get_one_role(role_id)
        role["notes"] = clean(
            role["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No role with this id",
        )
    return render_template(
        "views/roles/single_role.html",
        role=role,
        title="Role #%s" % (int(role_id))
    )


@is_logged_in
@app.route("/view/services/")
@app.route("/view/services/all/")
def display_all_services():
    """Show all services."""
    sort = request.args.get("sort") if request.args.get(
        "sort") else "service.name"
    try:
        services = sql_service.get_all_services(sort)
    except ValueError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg="Unacceptable sort."
        ), 400
    return render_template(
        "views/services/all_services.html",
        services=services,
        services_len=len(services),
        title="Services"
    )


@is_logged_in
@app.route("/view/services/single/<int:service_id>")
def display_one_service(service_id):
    """Show info on one service."""
    try:
        service = sql_service.get_one_service(service_id)
        service["notes"] = clean(
            service["notes"], tags=["a", "b", "br", "em", "i"], strip=True
        )
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No service level with this id",
        )
    return render_template(
        "views/services/single_service.html",
        service=service,
        title="Service #%s" % (int(service_id))
    )


@is_logged_in
@app.route("/view/reports/")
@app.route("/view/reports/main/")
def display_main_stats():
    """Display main counting stats."""
    racks, rackSize = sql_report.get_num_racks_and_size()
    devices = sql_report.get_num_devices()
    unracked = len(sql_device.get_devices_unracked())
    racked = int(devices) - int(unracked)
    free = int(rackSize) - racked
    return render_template(
        "views/reports/main_report.html",
        racks=racks,
        rackSize=rackSize,
        devices=devices,
        unracked=unracked,
        racked=racked,
        free=free,
        title="Main Report"
    )


@is_logged_in
@app.route("/view/reports/device_count/")
def display_device_count_report():
    """Display counting stats on devices."""
    customers = sql_report.get_top_customer_count()
    roles = sql_report.get_top_role_count()
    hardwares = sql_report.get_top_hardware_count()
    oses = sql_report.get_top_os_count()
    return render_template(
        "views/reports/device_count.html",
        customers=customers,
        roles=roles,
        hardwares=hardwares,
        oses=oses,
        title="Device Count"
    )


@is_logged_in
@app.route("/view/reports/dups/")
def display_dups_report():
    """Display dups."""
    serials = sql_report.get_dup_serials()
    assets = sql_report.get_dup_assets()
    keys = sql_report.get_dup_licence_keys()
    return render_template(
        "views/reports/dups.html",
        serials=serials,
        assets=assets,
        keys=keys,
        title="Duplicates"
    )


@is_logged_in
@app.route("/view/assets/check_asset/", methods=["GET", "POST"])
def list_all_assets():
    """Check if asset # is already in use."""
    method = request.form["type"]
    new_asset = request.form["asset"].lower()
    assets = [a.lower() for a in sql_device.get_assets()]
    if method == "new":
        if new_asset in assets:
            response = jsonify("This asset # is already in use.")
        else:
            response = jsonify("true")
        return response
    else:
        dev_id = request.form["id"]
        con = sql_connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT asset_no FROM device WHERE id = %s", (dev_id,))
        org_asset = str(cur.fetchone()[0]).lower()
        if new_asset != org_asset:
            if new_asset in assets:
                response = jsonify("This asset # is already in use.")
            else:
                response = jsonify("true")
            return response
        else:
            return jsonify("true")


@is_logged_in
@app.route("/view/device_names/check_name/", methods=["GET", "POST"])
def list_all_dev_names():
    """Check if device name already exists."""
    method = request.form["type"]
    new_name = request.form["name"].lower()
    names = [n.lower() for n in sql_device.get_names()]
    if method == "new":
        if new_name in names:
            response = jsonify("This name is already in use.")
        else:
            response = jsonify("true")
        return response
    else:
        dev_id = request.form["id"]
        con = sql_connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT name FROM device WHERE id = %s", (dev_id,))
        org_name = str(cur.fetchone()[0]).lower()
        if new_name != org_name:
            if new_name in names:
                response = jsonify("This device name is already in use.")
            else:
                response = jsonify("true")
            return response
        else:
            return jsonify("true")


@is_logged_in
@app.route("/view/oses/check_key/", methods=["GET", "POST"])
def list_all_keys():
    """Check if licence key is already in use."""
    method = request.form["type"]
    new_key = request.form["key"].lower()
    keys = [k.lower() for k in sql_device.get_licence_keys()]
    if method == "new":
        if new_key in keys:
            response = jsonify("This licence key is already in use.")
        else:
            response = jsonify("true")
        return response
    else:
        dev_id = request.form["id"]
        con = sql_connect.query_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT os_licence_key FROM device WHERE id = %s", (dev_id,))
        org_key = str(cur.fetchone()[0]).lower()
        if new_key != org_key:
            if new_key in keys:
                response = jsonify("This licence key is already in use.")
            else:
                response = jsonify("true")
            return response
        else:
            return jsonify("true")


@is_logged_in
@app.route("/view/serials/check_serial/", methods=["GET", "POST"])
def list_all_serials():
    """Check if serial # is already in use."""
    method = request.form["type"]
    new_serial = request.form["serial"].lower()
    serials = [s.lower() for s in sql_device.get_serials()]
    if method == "new":
        if new_serial in serials:
            response = jsonify("This serial # is already in use.")
        else:
            response = jsonify("true")
        return response
    else:
        dev_id = request.form["id"]
        con = sql_connect.query_connection()
        cur = con.cursor()
        cur.execute("SELECT serial_no FROM device WHERE id = %s", (dev_id,))
        org_serial = str(cur.fetchone()[0]).lower()
        if new_serial != org_serial:
            if new_serial in serials:
                response = jsonify("This serial # is already in use.")
            else:
                response = jsonify("true")
            return response
        else:
            return jsonify("true")


@is_logged_in
@app.route("/add/device/new/", methods=["GET", "POST"])
def add_device():
    """Add device."""
    devForm = AddDeviceForm()
    # Add prompts for user to select option for required fields.
    devForm.domain.choices.insert(0, (0, "Select A Domain"))
    devForm.rack_name.choices.insert(0, (0, "Select A Rack"))
    devForm.org.choices.insert(0, (0, "Select A Manufacturer"))
    devForm.os.choices.insert(0, (0, "Select An Operating System"))
    devForm.role.choices.insert(0, (0, "Select Device Role"))
    devForm.customer.choices.insert(0, (0, "Select A Customer"))
    devForm.service_level.choices.insert(0, (0, "Select The Service Level"))
    racks = [
        [rack[0], rack[1], rack[5]] for rack in sql_rack.get_all_racks()
    ]
    hardwares = [[
        hardware["id"], hardware["name"],
        hardware["manufacturer"], hardware["size"]]
        for hardware in sql_hardware.get_all_hardware()
    ]
    rack_ids = sql_rack.get_all_rack_ids()
    occupieds = [
        [rack_id, " ".join(
            map(str, sql_rack.get_occupied_slots(rack_id)))]
        for rack_id in rack_ids
    ]
    pos = request.args.get("pos")
    if devForm.validate_on_submit():
        dev_name = request.form["dev_name"]
        domain = request.form["domain"]
        rack_id = request.form["rack_name"]
        rack_pos = request.form["rack_pos"]
        model = request.form["model"]
        os = request.form["os"]
        version = request.form["version"]
        key = request.form.get("key")
        role = request.form["role"]
        in_service = 1 if request.form.get("in_service") else 0
        purchased = request.form.get("purchased")
        serial = request.form.get("serial")
        asset = request.form.get("asset")
        customer = request.form["customer"]
        service_level = request.form["service_level"]
        notes = request.form.get("notes")
        user = session["username"]
        sql_device.add_new_device(
            dev_name, domain, rack_id, rack_pos, model, os,
            version, key, role, in_service, purchased, serial, asset,
            customer, service_level, notes, user
        )
        flash(f"Device {dev_name} added.", category="info")
        return redirect("/view/devices/")
    return render_template(
        "add/device/new.html",
        occupieds=occupieds,
        racks=racks,
        pos=pos,
        hardwares=hardwares,
        form=devForm,
        title="Add New Device"
    )


@is_logged_in
@app.route("/add/device/copy/<int:device_id>", methods=["GET", "POST"])
def add_device_copy(device_id):
    """Add new device based off of a copy."""
    devForm = AddDeviceForm()
    domains = [
        [domain["id"], domain["name"]]
        for domain in sql_domain.get_all_domains_full()
    ]
    racks = [
        [rack[0], rack[1], rack[5]] for rack in sql_rack.get_all_racks()
    ]
    orgs = [[org["id"], org["name"]] for org in sql_device.get_orgs()]
    hardwares = [[
        hardware["id"], hardware["name"],
        hardware["manufacturer"], hardware["size"]]
        for hardware in sql_hardware.get_all_hardware()
    ]
    oses = [[os["id"], os["name"]] for os in sql_os.get_all_oses()]
    roles = [[role["id"], role["name"]] for role in sql_role.get_all_roles()]
    customers = [
        [customer["id"], customer["name"]]
        for customer in sql_device.get_customers()
    ]
    services = [
        [service["id"], service["name"]]
        for service in sql_service.get_all_services()
    ]
    rack_ids = sql_rack.get_all_rack_ids()
    occupieds = [
        [rack_id, " ".join(
            map(str, sql_rack.get_occupied_slots(rack_id)))]
        for rack_id in rack_ids
    ]
    device = sql_device.get_info_on_one_device(device_id)
    if devForm.validate_on_submit():
        dev_name = request.form["dev_name"]
        domain = request.form["domain"]
        rack_id = request.form["rack_name"]
        rack_pos = request.form["rack_pos"]
        model = request.form["model"]
        os = request.form["os"]
        version = request.form["version"]
        key = request.form.get("key")
        role = request.form["role"]
        in_service = 1 if request.form.get("in_service") else 0
        purchased = request.form.get("purchased")
        serial = request.form.get("serial")
        asset = request.form.get("asset")
        customer = request.form["customer"]
        service_level = request.form["service_level"]
        notes = request.form.get("notes")
        user = session["username"]
        sql_device.add_new_device(
            dev_name, domain, rack_id, rack_pos, model, os,
            version, key, role, in_service, purchased, serial, asset,
            customer, service_level, notes, user
        )
        flash(f"Device {dev_name} added.", category="info")
        return redirect("/view/devices/")
    try:
        return render_template(
            "add/device/copy.html",
            domains=domains,
            occupieds=occupieds,
            racks=racks,
            orgs=orgs,
            hardwares=hardwares,
            oses=oses,
            roles=roles,
            customers=customers,
            services=services,
            form=devForm,
            sel_name=device["name"],
            sel_dom=device["domain"],
            sel_rack=device["rack"],
            sel_pos=device["pos"],
            sel_man=device["man"],
            sel_hard_id=device["hard_id"],
            sel_hard_name=device["hardware"],
            sel_os=device["os"],
            sel_version=device["version"],
            sel_role=device["role"],
            sel_in_service=device["in_service"],
            sel_purchased=device["purchased"],
            sel_cust=device["customer"],
            sel_service=device["service"],
            sel_notes=device["notes"],
            title=f"Add Copy of {device['name']}"
        )
    except TypeError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_device.get_nearest_device_by_id(device_id)
        ), 400


@is_logged_in
@app.route("/add/rack/new/", methods=["GET", "POST"])
def add_new_rack():
    """Add new rack."""
    form = RackForm()
    # Add prompt for user to select option for required fields.
    form.room.choices.insert(0, (0, "Select A Room"))
    if form.validate_on_submit():
        rack_name = request.form["rack_name"]
        room = request.form["room"]
        size = request.form["size"]
        order = request.form["order"]
        notes = request.form.get("notes")
        user = session["username"]
        try:
            sql_rack.add_new_rack(
                rack_name, room, size, order, notes, user
            )
            flash(f"Rack {rack_name} added.", category="info")
            return redirect("/view/racks/all/")
        except ValueError:
            return render_template(
                "error_pages/400.html",
                title="400",
                msg="Bad room choice."
            ), 400
    return render_template(
        "add/rack/new.html",
        form=form,
        title="Add new rack",
    )


@is_logged_in
@app.route("/add/rack/copy/<int:rack_id>", methods=["GET", "POST"])
def add_copy_rack(rack_id):
    """Add copy of a rack."""
    form = RackForm()
    if form.validate_on_submit():
        rack_name = request.form["rack_name"]
        room = request.form["room"]
        size = request.form["size"]
        order = request.form["order"]
        notes = request.form.get("notes")
        user = session["username"]
        try:
            sql_rack.add_new_rack(
                rack_name, room, size, order, notes, user
            )
            flash(f"Rack {rack_name} added.", category="info")
            return redirect("/view/racks/all/")
        except ValueError:
            return render_template(
                "error_pages/400.html",
                title="400",
                msg="Bad room choice."
            ), 400
    rooms = [
        [room["id"], room["name"], room["building"]]
        for room in sql_room.get_all_rooms()
    ]
    rack = sql_rack.get_rack_info(rack_id)
    try:
        return render_template(
            "/add/rack/copy.html",
            form=form,
            rooms=rooms,
            sel_name=rack[0],
            sel_room=rack[1],
            sel_size=rack[2],
            sel_dir=int(rack[3]),
            sel_note=rack[4],
            title=f"Add Copy of {rack[0]}"
        )
    except TypeError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_rack.get_nearest_rack_by_id(rack_id)
        ), 400


@is_logged_in
@app.route("/add/app/new/", methods=["GET", "POST"])
def add_new_app():
    """Add new app."""
    form = AppForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form["description"]
        note = request.form.get("notes").replace("<", "&lt;").replace(
            ">", "&gt;") if request.form.get("notes") else ""
        user = session["username"]
        sql_app.add_new_app(name, desc, note, user)
        flash(f"App {name} added.", category="info")
        return redirect("/view/apps/all/")
    return render_template(
        "/add/apps/new.html",
        form=form,
        title="Add New App"
    )


@is_logged_in
@app.route("/add/app/relation/<int:app_id>", methods=["GET", "POST"])
def add_new_relation(app_id):
    """Add new relationship."""
    form = AppRelationForm()
    # Add prompt for user to select option for required fields.
    form.relationship.choices.insert(0, (0, "Select A Relationship"))
    form.device.choices.insert(0, (0, "Select A Device"))
    if form.validate_on_submit():
        relation = request.form["relationship"]
        device = request.form["device"]
        user = session["username"]
        sql_app.add_app_device_relation(
            app_id, device, relation, user
        )
        flash("Relationship added.", category="info")
        return redirect(f"/view/apps/single/{app_id}")
    devices = [[dev[0], dev[1]] for dev in sql_app.get_all_devices()]
    relations = sql_app.get_all_relations()
    name = sql_app.get_one_app(app_id)["name"]
    return render_template(
        "/add/apps/relation.html",
        form=form,
        name=name,
        relations=relations,
        devices=devices,
        title="Add New Relation For App"
    )


@is_logged_in
@app.route("/add/building/new/", methods=["GET", "POST"])
def add_new_building():
    """Add new building."""
    form = BuildingForm()
    if form.validate_on_submit():
        name = request.form["name"]
        short = request.form.get("short")
        notes = request.form.get("notes")
        user = session["username"]
        sql_building.add_new_building(name, short, notes, user)
        flash(f"Added new building {name}.", category="info")
        return redirect("/view/buildings/all/")
    return render_template(
        "/add/config/building.html",
        form=form,
        title="Add New Building"
    )


@is_logged_in
@app.route("/add/room/new/", methods=["GET", "POST"])
def add_new_room():
    """Add new room."""
    form = RoomForm()
    # Add prompt for user to select option for required fields.
    form.building.choices.insert(0, (0, "Select A Building"))
    if form.validate_on_submit():
        name = request.form["name"]
        build = request.form["building"]
        notes = request.form.get("notes")
        user = session["username"]
        sql_room.add_new_room(name, build, notes, user)
        flash(f"Added new room {name}.", category="info")
        return redirect("/view/rooms/all/")
    return render_template(
        "/add/config/room.html",
        form=form,
        title="Add New Room"
    )


@is_logged_in
@app.route("/add/domain/new/", methods=["GET", "POST"])
def add_new_domain():
    """Add new domain."""
    form = DomainForm()
    if form.validate_on_submit():
        name = request.form["name"]
        descript = request.form.get("description")
        notes = request.form.get("notes")
        user = session["username"]
        sql_domain.add_new_domain(name, descript, notes, user)
        flash(f"Added new domain {name}.", category="info")
        return redirect("/view/domains/all/")
    return render_template(
        "/add/config/domain.html",
        form=form,
        title="Add New Domain"
    )


@is_logged_in
@app.route("/add/hardware/new/", methods=["GET", "POST"])
def add_new_hardware():
    """Add new hardware."""
    form = HardwareForm()
    # Add prompt for user to select option for required fields.
    form.manufacturer.choices.insert(0, (0, "Select A Manufacturer"))
    if form.validate_on_submit():
        name = request.form["name"]
        org = request.form["manufacturer"]
        size = request.form["size"]
        image = request.form.get("image")
        support = request.form.get("support")
        spec = request.form.get("spec")
        notes = request.form.get("notes").replace("<", "&lt;").replace(
            ">", "&gt;") if request.form.get("notes") else ""
        user = session["username"]
        sql_hardware.add_new_hardware(
            name, org, size, image, support, spec, notes, user
        )
        flash(f"Added new hardware {name}.", category="info")
        return redirect("/view/hardware/all/")
    return render_template(
        "/add/config/hardware.html",
        form=form,
        title="Add New Hardware"
    )


@is_logged_in
@app.route("/add/os/new/", methods=["GET", "POST"])
def add_new_os():
    """Add new os."""
    form = OsForm()
    # Add prompt for user to select option for required fields.
    form.developer.choices.insert(0, (0, "Select A Developer"))
    if form.validate_on_submit():
        name = request.form["name"]
        org = request.form["developer"]
        notes = request.form.get("notes")
        user = session["username"]
        sql_os.add_new_os(name, org, notes, user)
        flash(f"Added new os {name}.", category="info")
        return redirect("/view/oses/all/")
    return render_template(
        "/add/config/os.html",
        form=form,
        title="Add New OS"
    )


@is_logged_in
@app.route("/add/org/new/", methods=["GET", "POST"])
def add_new_org():
    """Add new org."""
    form = OrgForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form.get("description")
        acct = request.form.get("account")
        types = form.types.data
        cust = 1 if "customer" in types else 0
        soft = 1 if "software" in types else 0
        hard = 1 if "hardware" in types else 0
        home = request.form.get("homepage")
        notes = request.form.get("notes").replace("<", "&lt;").replace(
            ">", "&gt;") if request.form.get("notes") else ""
        user = session["username"]
        flash(f"Added new org {name}.", category="info")
        sql_org.add_new_org(
            name, acct, cust, soft, hard, desc, home, notes, user
        )
    return render_template(
        "/add/config/org.html",
        form=form,
        title="Add New Org"
    )


@is_logged_in
@app.route("/add/role/new/", methods=["GET", "POST"])
def add_new_role():
    """Add new role."""
    form = RoleForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form.get("description")
        notes = request.form.get("notes")
        user = session["username"]
        sql_role.add_new_role(name, desc, notes, user)
        flash(f"Added new role {name}.", category="info")
        return redirect("/view/roles/all/")
    return render_template(
        "/add/config/role.html",
        form=form,
        title="Add New Role"
    )


@is_logged_in
@app.route("/add/service/new/", methods=["GET", "POST"])
def add_new_service_level():
    """Add new service level."""
    form = ServiceForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form.get("description")
        notes = request.form.get("notes").replace("<", "&lt;").replace(
            ">", "&gt;") if request.form.get("notes") else ""
        user = session["username"]
        sql_service.add_new_service(name, desc, notes, user)
        flash(f"Added new service {name}.", category="info")
        return redirect("/view/services/all/")
    return render_template(
        "/add/config/service.html",
        form=form,
        title="Add New Service"
    )


@is_logged_in
@app.route("/update/device/<int:device_id>", methods=["GET", "POST"])
def update_device(device_id):
    """Update device."""
    form = UpdateDeviceForm()
    form.dev_id.data = device_id
    domains = [
        [domain["id"], domain["name"]]
        for domain in sql_domain.get_all_domains_full()
    ]
    racks = [
        [rack[0], rack[1], rack[5]] for rack in sql_rack.get_all_racks()
    ]
    orgs = [[org["id"], org["name"]] for org in sql_device.get_orgs()]
    hardwares = [[
        hardware["id"], hardware["name"],
        hardware["manufacturer"], hardware["size"]]
        for hardware in sql_hardware.get_all_hardware()
    ]
    oses = [[os["id"], os["name"]] for os in sql_os.get_all_oses()]
    roles = [[role["id"], role["name"]] for role in sql_role.get_all_roles()]
    customers = [
        [customer["id"], customer["name"]]
        for customer in sql_device.get_customers()
    ]
    services = [
        [service["id"], service["name"]]
        for service in sql_service.get_all_services()
    ]
    rack_ids = sql_rack.get_all_rack_ids()
    occupieds = [
        [rack_id, " ".join(
            map(str, sql_rack.get_occupied_slots(rack_id))
        )] for rack_id in rack_ids
    ]
    if form.validate_on_submit():
        dev_name = request.form["dev_name"]
        domain = request.form["domain"]
        rack_id = request.form["rack_name"]
        rack_pos = request.form["rack_pos"]
        model = request.form["model"]
        os = request.form["os"]
        version = request.form["version"]
        key = request.form.get("key")
        role = request.form["role"]
        in_service = 1 if request.form.get("in_service") else 0
        purchased = request.form.get("purchased")
        serial = request.form.get("serial")
        asset = request.form.get("asset")
        customer = request.form["customer"]
        service_level = request.form["service_level"]
        notes = request.form.get("notes")
        user = session["username"]
        sql_device.update_device(
            device_id, dev_name, domain, rack_id, rack_pos, model, os,
            version, key, role, in_service, purchased, serial, asset,
            customer, service_level, notes, user
        )
        flash(f"Device {dev_name} updated.", category="info")
        return redirect(f"/view/devices/one/{device_id}")
    device = sql_device.get_info_on_one_device(device_id)
    try:
        return render_template(
            "update/device.html",
            domains=domains,
            occupieds=occupieds,
            racks=racks,
            orgs=orgs,
            hardwares=hardwares,
            oses=oses,
            roles=roles,
            customers=customers,
            services=services,
            form=form,
            sel_name=device["name"],
            sel_dom=device["domain"],
            sel_rack=device["rack"],
            sel_pos=device["pos"],
            sel_man=device["man"],
            sel_hard_id=device["hard_id"],
            sel_hard_name=device["hardware"],
            sel_os=device["os"],
            sel_version=device["version"],
            sel_role=device["role"],
            sel_in_service=device["in_service"],
            sel_purchased=device["purchased"],
            sel_cust=device["customer"],
            sel_service=device["service"],
            sel_notes=device["notes"],
            sel_serial=device["serial"],
            sel_asset=device["asset"],
            sel_key=device["licence"],
            title=f"Update Device {device['name']}"
        )
    except TypeError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_device.get_nearest_device_by_id(device_id)
        ), 400


@is_logged_in
@app.route("/update/rack/<int:rack_id>", methods=["GET", "POST"])
def update_rack(rack_id):
    """Update rack."""
    form = RackForm()
    if form.validate_on_submit():
        rack_name = request.form["rack_name"]
        room = request.form["room"]
        size = request.form["size"]
        order = request.form["order"]
        notes = request.form.get("notes")
        user = session["username"]
        sql_rack.update_rack(
            rack_id, rack_name, room, size, order, notes, user
        )
        flash(f"Updated rack {rack_name}.", category="info")
        return redirect(f"/view/racks/one/normal/{rack_id}")
    rooms = [
        [room["id"], room["name"], room["building"]]
        for room in sql_room.get_all_rooms()
    ]
    rack = sql_rack.get_rack_info(rack_id)
    try:
        return render_template(
            "/update/rack.html",
            form=form,
            rooms=rooms,
            sel_name=rack[0],
            sel_room=rack[1],
            sel_size=rack[2],
            sel_dir=int(rack[3]),
            sel_note=rack[4],
            title=f"Update rack {rack[0]}"
        )
    except TypeError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_rack.get_nearest_rack_by_id(rack_id)
        ), 400


@is_logged_in
@app.route("/update/app/<int:app_id>", methods=["GET", "POST"])
def update_app(app_id):
    """Update app."""
    form = AppForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form["description"]
        note = request.form.get("notes").replace("<", "&lt;").replace(
            ">", "&gt;") if request.form.get("notes") else ""
        user = session["username"]
        sql_app.update_app(
            app_id, name, desc, note, user
        )
        flash(f"Updated app {name}.", category="info")
        return redirect(f"/view/apps/single/{app_id}")
    app = sql_app.get_one_app(app_id)
    try:
        return render_template(
            "/update/app.html",
            form=form,
            sel_name=app["name"],
            sel_desc=app["descript"],
            sel_notes=app["notes"],
            title=f"Update app {app['name']}"
        )
    except TypeError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_app.get_nearest_app_by_id(app_id)
        )


@is_logged_in
@app.route("/update/building/<int:build_id>", methods=["GET", "POST"])
def update_building(build_id):
    """Update building."""
    form = BuildingForm()
    if form.validate_on_submit():
        name = request.form["name"]
        short = request.form.get("short")
        notes = request.form.get("notes")
        user = session["username"]
        sql_building.update_building(
            build_id, name, short, notes, user
        )
        flash(f"Updated building {name}.", category="info")
        return redirect(f"/view/buildings/single/{build_id}")
    building = sql_building.get_one_building(build_id)
    try:
        return render_template(
            "/update/building.html",
            form=form,
            sel_name=building["name"],
            sel_short=building["name_short"],
            sel_notes=building["notes"],
            title=f"Update building {building[0]}"
        )
    except IndexError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_building.get_nearest_building_by_id(build_id)
        )


@is_logged_in
@app.route("/update/domain/<int:dom_id>", methods=["GET", "POST"])
def update_domain(dom_id):
    """Update domain."""
    form = DomainForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form.get("description")
        notes = request.form.get("notes")
        user = session["username"]
        flash(f"Updated domain {name}.", category="info")
        sql_domain.update_domain(dom_id, name, desc, notes, user)
        return redirect(f"/view/domains/single/{dom_id}")
    domain = sql_domain.get_one_domain(dom_id)
    try:
        return render_template(
            "/update/domain.html",
            form=form,
            sel_name=domain["name"],
            sel_desc=domain["descript"],
            sel_note=domain["notes"],
            title=f"Update domain {domain['name']}"
        )
    except IndexError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_domain.get_nearest_domain_by_id(dom_id)
        )


@is_logged_in
@app.route("/update/hardware/<int:hard_id>", methods=["GET", "POST"])
def update_hardware(hard_id):
    """Update hardware."""
    form = HardwareForm()
    if form.validate_on_submit():
        name = request.form["name"]
        org = request.form["manufacturer"]
        size = request.form["size"]
        image = request.form.get("image")
        support = request.form.get("support")
        spec = request.form.get("spec")
        notes = request.form.get("notes")
        user = session["username"]
        sql_hardware.update_hardware(
            hard_id, name, org, size, image, support, spec, notes, user
        )
        flash(f"Updated hardware {name}.", category="info")
        return redirect(f"/view/hardware/singe/{hard_id}")
    hardware = sql_hardware.get_one_hardware(hard_id)
    manufacturers = sql_hardware.get_all_manufacturers()
    try:
        return render_template(
            "/update/hardware.html",
            form=form,
            manufacturers=manufacturers,
            sel_name=hardware["name"],
            sel_org=hardware["manufacturer"],
            sel_size=hardware["size"],
            sel_image=hardware["image"],
            sel_supp=hardware["support"],
            sel_spec=hardware["spec"],
            sel_note=hardware["notes"],
            title=f"Update hardware {hardware['name']}"
        )
    except IndexError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_hardware.get_nearest_hardware_by_id(hard_id)
        )


@is_logged_in
@app.route("/update/org/<int:org_id>", methods=["GET", "POST"])
def update_org(org_id):
    """Update org."""
    form = OrgForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form.get("description")
        acct = request.form.get("account")
        types = form.types.data
        cust = 1 if "customer" in types else 0
        soft = 1 if "software" in types else 0
        hard = 1 if "hardware" in types else 0
        home = request.form.get("homepage")
        notes = request.form.get("notes")
        user = session["username"]
        flash(f"Updated org {name}.", category="info")
        sql_org.update_org(
            org_id, name, acct, cust, soft, hard,
            desc, home, notes, user
        )
        return redirect(f"/view/orgs/single/{org_id}")
    org = sql_org.get_one_org(org_id)
    try:
        return render_template(
            "/update/org.html",
            form=form,
            sel_name=org["name"],
            sel_desc=org["descript"],
            sel_acct=org["account_no"],
            sel_cust=int(org["customer"]),
            sel_soft=int(org["software"]),
            sel_hard=int(org["hardware"]),
            sel_home=org["home_page"],
            sel_note=org["notes"],
            title=f"Update org {org['notes']}"
        )
    except IndexError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_org.get_nearest_org_by_id(org_id)
        )


@is_logged_in
@app.route("/update/os/<int:os_id>", methods=["GET", "POST"])
def update_os(os_id):
    """Update os."""
    form = OsForm()
    if form.validate_on_submit():
        name = request.form["name"]
        org = request.form["developer"]
        notes = request.form.get("notes")
        user = session["username"]
        flash(f"Updated os {name}.", category="info")
        sql_os.update_os(os_id, name, org, notes, user)
    os = sql_os.get_one_os(os_id)
    devs = [[dev["id"], dev["name"]] for dev in sql_os.get_all_developers()]
    try:
        return render_template(
            "/update/os.html",
            form=form,
            devs=devs,
            sel_name=os["name"],
            sel_org=os["maker"],
            sel_note=os["notes"],
            title=f"Update os {os['name']}"
        )
    except IndexError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_os.get_nearest_os_by_id(os_id)
        )


@is_logged_in
@app.route("/update/role/<int:role_id>", methods=["GET", "POST"])
def update_role(role_id):
    """Update role."""
    form = RoleForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form.get("description")
        notes = request.form.get("notes")
        user = session["username"]
        flash(f"Updated role {name}.", category="info")
        sql_role.update_role(role_id, name, desc, notes, user)
        return redirect(f"/view/roles/single/{role_id}")
    role = sql_role.get_one_role(role_id)
    try:
        return render_template(
            "/update/role.html",
            form=form,
            sel_name=role["name"],
            sel_desc=role["descript"],
            sel_note=role["notes"],
            title=f"Update role {role['name']}"
        )
    except IndexError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_role.get_nearest_role_by_id(role_id)
        )


@is_logged_in
@app.route("/update/room/<int:room_id>", methods=["GET", "POST"])
def update_room(room_id):
    """Update room."""
    form = RoomForm()
    if form.validate_on_submit():
        name = request.form["name"]
        build = request.form["building"]
        notes = request.form.get("notes")
        user = session["username"]
        flash(f"Updated room {name}.", category="info")
        sql_room.update_room(room_id, name, build, notes, user)
        return redirect(f"/view/rooms/single/{room_id}")
    room = sql_room.get_one_room(room_id)
    buildings = [
        [build["id"], build["name"]]
        for build in sql_building.get_all_buildings()
    ]
    try:
        return render_template(
            "/update/room.html",
            form=form,
            buildings=buildings,
            sel_name=room["name"],
            sel_build=room["build_id"],
            sel_note=room["notes"],
            title=f"Update room {room['name']}"
        )
    except IndexError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_room.get_nearest_room_by_id(room_id)
        )


@is_logged_in
@app.route("/update/service/<int:service_id>", methods=["GET", "POST"])
def update_service(service_id):
    """Update service."""
    form = ServiceForm()
    if form.validate_on_submit():
        name = request.form["name"]
        desc = request.form.get("description")
        notes = request.form.get("notes")
        user = session["username"]
        flash(f"Updated service {name}.")
        sql_service.update_service(
            service_id, name, desc, notes, user
        )
        return redirect(f"/view/services/single{service_id}")
    service = sql_service.get_one_service(service_id)
    try:
        return render_template(
            "/update/service.html",
            form=form,
            sel_name=service["name"],
            sel_desc=service["descript"],
            sel_note=service["notes"],
            title=f"Update service {service['name']}"
        )
    except IndexError:
        return render_template(
            "error_pages/400.html",
            title="400",
            msg=sql_service.get_nearest_service_by_id(service_id)
        )


@is_logged_in
@app.route("/delete/device/<int:device_id>", methods=["GET", "POST"])
def delete_device(device_id):
    """Delete device."""
    form = DeleteForm()
    try:
        name = sql_device.get_device(device_id)["name"]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No device exists with this id.",
        ), 404,
    if form.validate_on_submit():
        sql_device.delete_device(device_id, session["username"])
        flash(f"Deleted device {name}", category="info")
        return redirect("/view/devices/")
    return render_template(
        "delete/delete.html",
        category="device",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/rack/<int:rack_id>", methods=["GET", "POST"])
def delete_rack(rack_id):
    """Delete rack."""
    form = DeleteForm()
    try:
        name = sql_rack.get_one_rack_normal_view(rack_id)[0]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No rack exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_rack.delete_rack(rack_id, session["username"])
            flash(f"Deleted rack {name}", category="info")
            return redirect("/view/racks/")
        except psycopg2.Error:
            flash("Devices in rack must be moved first.", category="danger")
            return redirect(f"/view/racks/list/extended/{rack_id}")
    return render_template(
        "delete/delete.html",
        category="rack",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/app/<int:app_id>", methods=["GET", "POST"])
def delete_app(app_id):
    """Delete app."""
    form = DeleteForm()
    try:
        name = sql_app.get_one_app(app_id)["name"]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No app exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_app.delete_app("app", app_id, session["username"])
            flash(f"Deleted app {name}", category="info")
            return redirect("/view/apps/")
        except psycopg2.Error:
            flash("Relationships must be deleted first.", category="danger")
            return redirect(f"/view/apps/single/{app_id}")
    return render_template(
        "delete/delete.html",
        category="app",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/relationship/<int:rel_id>", methods=["GET", "POST"])
def delete_relationship(rel_id):
    """Delete app device relationship."""
    form = DeleteForm()
    try:
        name = sql_app.get_relation_name(rel_id)
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No relationship exists with this id.",
        ),
    if form.validate_on_submit():
        sql_app.delete_app("device_app", rel_id, session["username"])
        flash(f"Deleted relationship #{name}", category="info")
        return redirect(f"/view/apps/single/{name}")
    return render_template(
        "delete/delete.html",
        category="relationship",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/building/<int:build_id>", methods=["GET", "POST"])
def delete_building(build_id):
    """Delete building."""
    form = DeleteForm()
    try:
        name = sql_building.get_one_building(build_id)["name"]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No building exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_building.delete_building(build_id, session["username"])
            flash(f"Deleted building {name}", category="info")
            return redirect("/view/buildings/")
        except psycopg2.Error:
            flash("Rooms in building must be deleted first.", category="danger")
            return redirect(f"/view/buildings/single/{build_id}")
    return render_template(
        "delete/delete.html",
        category="building",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/room/<int:room_id>", methods=["GET", "POST"])
def delete_room(room_id):
    """Delete room."""
    form = DeleteForm()
    try:
        name = sql_room.get_one_room(room_id)["name"]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No room exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_room.delete_room(room_id, session["username"])
            flash(f"Deleted room {name}", category="info")
            return redirect("/view/rooms/")
        except psycopg2.Error:
            flash("Racks in room must be moved first.", category="danger")
            return redirect(f"/view/rooms/single/{room_id}")
    return render_template(
        "delete/delete.html",
        category="room",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/domain/<int:domain_id>", methods=["GET", "POST"])
def delete_domain(domain_id):
    """Delete domain."""
    form = DeleteForm()
    try:
        name = sql_domain.get_one_domain(domain_id)["name"]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No domain exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_domain.delete_domain(domain_id, session["username"])
            flash(f"Deleted domain {name}", category="info")
            return redirect("/view/domains")
        except psycopg2.Error:
            flash("Devices with this domain must be changed.", category="danger")
            return redirect("/view/devices/")
    return render_template(
        "delete/delete.html",
        category="domain",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/hardware/<int:hardware_id>", methods=["GET", "POST"])
def delete_hardware(hardware_id):
    """Delete hardware."""
    form = DeleteForm()
    try:
        name = sql_hardware.get_one_hardware(hardware_id)["name"]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No hardware exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_hardware.delete_hardware(hardware_id, session["username"])
            flash(f"Deleted hardware {name}", category="info")
            return redirect("/view/hardware")
        except psycopg2.Error:
            flash("Devices are still using this hardware.", category="danger")
            return redirect(f"/view/devices/?hardware={hardware_id}")
    return render_template(
        "delete/delete.html",
        category="hardware",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/os/<int:os_id>", methods=["GET", "POST"])
def delete_os(os_id):
    """Delete os."""
    form = DeleteForm()
    try:
        name = sql_os.get_one_os(os_id)["name"]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No OS exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_os.delete_os(os_id, session["username"])
            flash(f"Deleted os {name}", category="info")
            return redirect("/view/oses/")
        except psycopg2.Error:
            flash("Devices are still using this os.", category="danger")
            return redirect(f"/view/devices/?os={os_id}")
    return render_template(
        "delete/delete.html",
        category="os",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/org/<int:org_id>", methods=["GET", "POST"])
def delete_org(org_id):
    """Delete org."""
    form = DeleteForm()
    try:
        org = sql_org.get_one_org(org_id)
        name = org["name"]
        software = int(org["software"])
        hardware = int(org["hardware"])
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No org exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_org.delete_org(org_id, session["username"])
            flash(f"Deleted org {name}", category="info")
            return redirect("/view/orgs/")
        except psycopg2.Error:
            if software and hardware:
                flash(
                    "An OS or hardware model by this org is still in use.",
                    category="info"
                )
            elif software:
                flash("An OS by this org is still in use.", category="info")
            else:
                flash(
                    "A hardware model by this org is still in use",
                    category="info"
                )
            return redirect(f"/view/orgs/single/{org_id}")
    return render_template(
        "delete/delete.html",
        category="org",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/role/<int:role_id>", methods=["GET", "POST"])
def delete_role(role_id):
    """Delete role."""
    form = DeleteForm()
    try:
        name = sql_role.get_one_role(role_id)["name"]
    except IndexError:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No role exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_role.delete_role(role_id, session["username"])
            flash(f"Deleted role {name}", category="info")
            return redirect("/view/roles")
        except psycopg2.Error:
            flash("Devices are still using this role.", category="danger")
            return redirect(f"/view/devices/?role={role_id}")
    return render_template(
        "delete/delete.html",
        category="role",
        form=form,
        name=name,
    )


@is_logged_in
@app.route("/delete/service/<int:service_id>", methods=["GET", "POST"])
def delete_service(service_id):
    """Delete service."""
    form = DeleteForm()
    try:
        name = sql_service.get_one_service(service_id)["name"]
    except Exception:
        return render_template(
            "error_pages/404.html",
            title="404",
            msg="No service level exists with this id.",
        ), 404
    if form.validate_on_submit():
        try:
            sql_service.delete_service(service_id, session["username"])
            flash(f"Deleted service {name}", category="info")
            return redirect("/view/services")
        except psycopg2.Error:
            flash("Devices are still on this service level.", category="danger")
            return redirect("/view/devices/extended/?sort=device.service")
    return render_template(
        "delete/delete.html",
        category="service",
        form=form,
        name=name,
    )


# Error pages.
@app.errorhandler(500)
def error(e):
    """Python failed or username doesn't exist."""
    return render_template(
        "error_pages/500.html",
        title="500",
    ), 500


@app.errorhandler(429)
def data_limited(e):
    """User made too many requests to data limited page."""
    return render_template(
        "error_pages/429.html",
        title="429",
    ), 429


@app.errorhandler(404)
def page_not_found(e):
    """Page not found."""
    return render_template(
        "error_pages/404.html",
        title="404",
    ), 404


@app.errorhandler(400)
def bad_request(e):
    """Bad request."""
    return render_template(
        "error_pages/400.html",
        title="400",
    ), 400
