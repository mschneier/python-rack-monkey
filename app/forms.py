"""Create forms."""
from flask_wtf import FlaskForm
from SqlApps import SqlApp as sql_app
from SqlBuildings import SqlBuilding as sql_building
from SqlConnection import SqlConnect as connect
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
from wtforms import DateField, PasswordField, RadioField, SelectField
from wtforms import SelectMultipleField, StringField, TextAreaField
from wtforms.fields.html5 import IntegerField, URLField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.validators import NumberRange, Required, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget


class MultiCheckboxField(SelectMultipleField):
	widget = ListWidget(prefix_label=False)
	option_widget = CheckboxInput()


def is_alpha(form, field):
    """Validate if field is alpha."""
    field = field.data
    if not field.isalpha():
        raise ValidationError("Must only contain alpha characters.")


def dup_key(form, field):
    """Check if key is already used."""
    field = field.data
    keys = [key.lower() for key in sql_device.get_licence_keys()]
    if field.lower() in keys:
        raise ValidationError("Licence key is already used.")


def is_available(form, field):
    """Check if slot is available and hardware fits."""
    slot = str(field.data)
    rack = str(form.rack_name.data)
    model = str(form.model.data)
    try:
        int(slot)
    except ValueError:
        raise ValidationError("Rack position must be an integer.")
    con = connect.query_connection()
    cur = con.cursor()
    cur.execute("SELECT size FROM rack WHERE id = %s", (rack,))
    max_size = int(cur.fetchone()[0])
    if int(slot) > max_size:
        raise ValidationError("Rack pos out of rack range.")
    cur.execute("SELECT size FROM hardware WHERE id = %s", (model,))
    size = int(cur.fetchone()[0])
    occupied = list(map(str, sql_rack.get_occupied_slots(rack)))
    if slot in occupied:
        raise ValidationError("Slot is filled.")
    for i in range(int(slot), int(slot) + size):
        if str(i) in occupied:
            raise ValidationError(
                "Slot is available but model is too big for space."
            )


def is_available_update(form, field):
    """Check if slot is available and hardware fits if not original slot."""
    slot = str(field.data)
    dev_id = str(form.dev_id.data)
    rack = str(form.rack_name.data)
    model = str(form.model.data)
    con = connect.query_connection()
    cur = con.cursor()
    cur.execute("SELECT size FROM hardware WHERE id = %s", (model,))
    size = str(cur.fetchone()[0])
    try:
        int(slot)
    except ValueError:
        raise ValidationError("Rack position must be an integer.")
    cur.execute(
        """SELECT device.rack, device.rack_pos, hardware.size
        FROM device, hardware
        WHERE device.id = %s AND device.hardware = hardware.id""", (dev_id,)
    )
    original = cur.fetchone()
    if not (rack == str(original[0]) and
            slot == str(original[1]) and size == str(original[2])):
        cur.execute("SELECT size FROM rack WHERE id = %s", (rack,))
        max_size = int(cur.fetchone()[0])
        if int(slot) > max_size:
            raise ValidationError("Rack pos out of rack range.")
        cur.execute("SELECT size FROM hardware WHERE id = %s", (model,))
        size = int(cur.fetchone()[0])
        occupied = list(map(str, sql_rack.get_occupied_slots(rack)))
        if slot in occupied:
            raise ValidationError("Slot is filled.")
        for i in range(int(slot), int(slot) + size):
            if str(i) in occupied:
                raise ValidationError(
                    "Slot is available but model is too big for space."
                )


def check_model_manufacuterer(form, field):
    """Check if model is made by that manufacturer."""
    model = int(field.data)
    man = form.org.data
    con = connect.query_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT id FROM hardware WHERE manufacturer = %s", (man,)
    )
    models = [int(m[0]) for m in cur.fetchall()]
    if model not in models:
        raise ValidationError(
            "This model is not made by the selected manufacturer."
        )


def dup_dev_name(form, field):
    """Check if device name is already used."""
    field = field.data
    names = [name.lower() for name in sql_device.get_names()]
    if field.lower() in names:
        raise ValidationError("Device name is already in use.")


def dup_dev_name_update(form, field):
    """Check if name is unique if not the same."""
    new_name = str(field.data)
    dev_id = str(form.dev_id.data)
    con = connect.query_connection()
    cur = con.cursor()
    cur.execute("SELECT name FROM device WHERE id = %s", (dev_id,))
    org_name = str(cur.fetchone()[0])
    if new_name != org_name:
        names = [name.lower() for name in sql_device.get_names()]
        if new_name in names:
            raise ValidationError("Device name is already in use.")


def dup_asset(form, field):
    """Check if asset # is already used."""
    field = field.data
    assets = [asset.lower() for asset in sql_device.get_assets()]
    if field.lower() in assets:
        raise ValidationError("Asset # is already used.")


def dup_serial(form, field):
    """Check if serial # is already used."""
    field = field.data
    serials = [serial.lower() for serial in sql_device.get_serials()]
    if field.lower() in serials:
        raise ValidationError("Serial # is already used.")


def short_name_check(form, field):
    """Check if short name is actually shorter."""
    short = field.data
    full = form.name.data
    if len(short) > len(full):
        raise ValidationError("Short name must be shorter than full name.")


class LoginForm(FlaskForm):
    """Form for logins."""

    username = StringField(
        "username",
        [Length(min=2, max=99), DataRequired(
            "Please fill in your username."), is_alpha]
    )
    password = PasswordField(
        "password",
        [Length(max=999), DataRequired("Please fill in your password.")]
    )


class AddDeviceForm(FlaskForm):
    """Form to add devices."""

    dev_name = StringField(
        "dev_name",
        [Length(max=99), DataRequired("Please fill out the device name."),
        dup_dev_name]
    )
    domain = SelectField(
        "domain",
        coerce=int,
        choices=[
            (dom["id"], dom["name"])
            for dom in sql_domain.get_all_domains_full()
        ],
        validators=[DataRequired("Pleae select the domain.")]
    )
    rack_name = SelectField(
        "rack_name",
        coerce=int,
        choices=[
            (rack["id"], rack["name"])
            for rack in sql_rack.get_all_racks()
        ],
        validators=[DataRequired("Please select the rack.")]
    )
    rack_pos = IntegerField(
        "rack_pos",
        [DataRequired("Please select the slot."),
         NumberRange(min=1, max=99), is_available]
    )
    org = SelectField(
        "manufacturer",
        coerce=int,
        choices=[
            (org["id"], org["name"]) for org in sql_device.get_orgs()
        ],
        validators=[DataRequired("Please select the manufacturer.")]
    )
    model = SelectField(
        "model",
        coerce=int,
        choices=[
            (model["id"], model["name"])
            for model in sql_hardware.get_all_hardware()
        ],
        validators=[
            DataRequired("Please select a hardware model."),
            check_model_manufacuterer
        ]
    )
    os = SelectField(
        "os",
        coerce=int,
        choices=[
            (os["id"], os["name"]) for os in sql_os.get_all_oses()
        ],
        validators=[DataRequired("Please select the OS.")]
    )
    version = StringField("version", [Length(max=99)])
    key = StringField("key", [Length(max=200), dup_key])
    role = SelectField(
        "role",
        coerce=int,
        choices=[
            (role["id"], role["name"]) for role in sql_role.get_all_roles()
        ],
        validators=[DataRequired("Please select the device's role.")]
    )
    purchased = DateField(
        "purchased",
        format="%Y-%m-%d",
        validators=[Optional()]
    )
    serial = StringField("serial", [Length(max=99), dup_serial])
    asset = StringField("asset", [Length(max=99), dup_asset])
    customer = SelectField(
        "customer",
        coerce=int,
        choices=[
            (customer["id"], customer["name"])
            for customer in sql_device.get_customers()
        ],
        validators=[DataRequired("Please select the customer.")]
    )
    service_level = SelectField(
        "service_level",
        coerce=int,
        choices=[
            (service["id"], service["name"])
            for service in sql_service.get_all_services()
        ],
        validators=[DataRequired("Please select the service level.")]
    )
    notes = TextAreaField("notes", [Length(max=500)])


class UpdateDeviceForm(FlaskForm):
    """Form to update devices."""

    dev_id = IntegerField()
    dev_name = StringField(
        "dev_name",
        [Length(max=99), DataRequired("Please fill out the device name."),
        dup_dev_name_update]
    )
    domain = SelectField(
        "domain",
        coerce=int,
        choices=[
            (dom["id"], dom["name"])
            for dom in sql_domain.get_all_domains_full()
        ],
        validators=[DataRequired("Pleae select the domain.")]
    )
    rack_name = SelectField(
        "rack_name",
        coerce=int,
        choices=[
            (rack["id"], rack["name"])
            for rack in sql_rack.get_all_racks()
        ],
        validators=[DataRequired("Please select the rack.")]
    )
    rack_pos = IntegerField(
        "rack_pos",
        [DataRequired("Please select the slot."),
         NumberRange(min=1, max=99), is_available_update]
    )
    org = SelectField(
        "manufacturer",
        coerce=int,
        choices=[
            (org["id"], org["name"]) for org in sql_device.get_orgs()
        ],
        validators=[DataRequired("Please select the manufacturer.")]
    )
    model = SelectField(
        "model",
        coerce=int,
        choices=[
            (model["id"], model["name"])
            for model in sql_hardware.get_all_hardware()
        ],
        validators=[
            DataRequired("Please select a hardware model."),
            check_model_manufacuterer
        ]
    )
    os = SelectField(
        "os",
        coerce=int,
        choices=[
            (os["id"], os["name"]) for os in sql_os.get_all_oses()
        ],
        validators=[DataRequired("Please select the OS.")]
    )
    version = StringField("version", [Length(max=99)])
    key = StringField("key", [Length(max=200), dup_key])
    role = SelectField(
        "role",
        coerce=int,
        choices=[
            (role["id"], role["name"]) for role in sql_role.get_all_roles()
        ],
        validators=[DataRequired("Please select the device's role.")]
    )
    purchased = DateField(
        "purchased",
        format="%Y-%m-%d",
        validators=[Optional()]
    )
    serial = StringField("serial", [Length(max=99), dup_serial])
    asset = StringField("asset", [Length(max=99), dup_asset])
    customer = SelectField(
        "customer",
        coerce=int,
        choices=[
            (customer["id"], customer["name"])
            for customer in sql_device.get_customers()
        ],
        validators=[DataRequired("Please select the customer.")]
    )
    service_level = SelectField(
        "service_level",
        coerce=int,
        choices=[
            (service["id"], service["name"])
            for service in sql_service.get_all_services()
        ],
        validators=[DataRequired("Please select the service level.")]
    )
    notes = TextAreaField("notes", [Length(max=500)])


class RackForm(FlaskForm):
    """Form to add racks."""

    rack_name = StringField(
        "rack_name",
        [Length(max=99), DataRequired("Please pick a name.")]
    )
    room = SelectField(
        "room",
        coerce=int,
        choices=[
            (room["id"], room["name"] + " in " + room["building"])
            for room in sql_room.get_all_rooms()
        ],
        validators=[DataRequired("Please select the room.")]
    )
    size = IntegerField(
        "size",
        [NumberRange(min=1, max=99),
         DataRequired("Please pick a size.")]
    )
    order = RadioField(
        "order",
        choices=[("1", "Top"), ("0", "Bottom")],
        validators=[DataRequired("Please select numbering order.")]
    )
    notes = TextAreaField("notes", [Length(max=500)])


class AppForm(FlaskForm):
    """Form to add app."""

    name = StringField(
        "name",
        [DataRequired("Please select a name."), Length(max=99)]
    )
    description = TextAreaField("description", [Length(max=500)])
    notes = TextAreaField("notes", [Length(max=500)])


class AppRelationForm(FlaskForm):
    """Form to add app relation."""

    relationship = SelectField(
        "relationship",
        coerce=int,
        choices=[
            (rel[0], rel[1]) for rel in sql_app.get_all_relations()
        ],
        validators=[DataRequired("Please select a relationship.")]
    )
    device = SelectField(
        "device",
        coerce=int,
        choices=[
            (dev[0], dev[1]) for dev in sql_app.get_all_devices()
        ],
        validators=[DataRequired("Please select a device.")]
    )


class BuildingForm(FlaskForm):
    """Form to add building."""

    name = StringField(
        "name",
        [DataRequired("Please pick a name."), Length(max=99)]
    )
    short = StringField("short", [Optional(), short_name_check])
    notes = TextAreaField("notes", [Length(max=500)])


class RoomForm(FlaskForm):
    """Form to add room."""

    name = StringField(
        "name",
        [DataRequired("Please pick a name."), Length(max=99)]
    )
    building = SelectField(
        "building",
        coerce=int,
        choices=[
            (build["id"], build["name"])
            for build in sql_building.get_all_buildings()
        ],
        validators=[DataRequired("Please select a building")]
    )
    notes = TextAreaField("notes", [Length(max=500)])


class DomainForm(FlaskForm):
    """Form to add domain."""

    name = StringField(
        "name",
        [DataRequired("Please select a name."), Length(max=99)]
    )
    description = TextAreaField("description", [Length(max=500)])
    notes = TextAreaField("notes", [Length(max=500)])


class HardwareForm(FlaskForm):
    """Form to add hardware."""
    name = StringField(
        "name",
        [DataRequired("Please select a name."), Length(max=99)]
    )
    manufacturer = SelectField(
        "manufacturer",
        coerce=int,
        choices=[
            (man[0], man[1])
            for man in sql_hardware.get_all_manufacturers()
        ],
        validators=[DataRequired("Please select a manufacturer.")]
    )
    size = IntegerField(
        "size",
        [DataRequired("Please pick a size."),
         NumberRange(min=1, max=20)]
    )
    image = StringField("image", [Length(max=199)])
    support = URLField("support", [Length(max=199)])
    spec = URLField("support", [Length(max=199)])
    notes = TextAreaField("notes", [Length(max=500)])


class OsForm(FlaskForm):
    """Form to add os."""

    name = StringField(
        "name", [DataRequired("Please enter a name."), Length(max=99)]
    )
    developer = SelectField(
        "developer",
        coerce=int,
        choices=[
            (org["id"], org["name"]) for org in sql_os.get_all_developers()
        ],
        validators=[DataRequired("Please select a manufacturer.")]
    )
    notes = TextAreaField("notes", [Length(max=500)])


class OrgForm(FlaskForm):
    """Form to add org."""

    name = StringField(
        "name", [DataRequired("Please enter a name."), Length(max=99)]
    )
    description = TextAreaField("description", [Length(max=500)])
    types = MultiCheckboxField(
        "types",
        [Required("Please select the type of organization.")],
        choices=[
            ("customer", "Customer"),
            ("hardware", "Makes Hardware"),
            ("software", "Makes Software")
        ]
    )
    account = StringField("account", [Length(max=99)])
    homepage = URLField("homepage", [Length(max=199)])
    notes = TextAreaField("notes", [Length(max=500)])


class RoleForm(FlaskForm):
    """Form to add domain."""

    name = StringField(
        "name",
        [DataRequired("Please select a name."), Length(max=99)]
    )
    description = TextAreaField("description", [Length(max=500)])
    notes = TextAreaField("notes", [Length(max=500)])


class ServiceForm(FlaskForm):
    """Form to add domain."""

    name = StringField(
        "name",
        [DataRequired("Please select a name."), Length(max=99)]
    )
    description = TextAreaField("description", [Length(max=500)])
    notes = TextAreaField("notes", [Length(max=500)])
