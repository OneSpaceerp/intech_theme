"""Write the brand into the site-wide settings the framework reads it from, and take it back out.

Runs on install, after every migrate, and whenever In Tech Theme Settings is saved. Every step is
idempotent: running it twice changes nothing the second time.

Before a value is first overwritten, what was there is parked under a default of our own,
so uninstalling hands the site back exactly as it was rather than as Frappe ships it.
"""

import frappe
from frappe.utils import cint

from intech_theme.branding import (
	DEFAULTS,
	SETTINGS_DOCTYPE,
	get_copyright,
	get_favicon,
	get_logo,
	get_settings,
	get_splash,
	is_vendor_url,
)
from intech_theme.utils.text import has_vendor_name

PREVIOUS = "intech:prev:{doctype}:{field}"


def after_install():
	seed_settings()
	apply_branding()
	# Frappe's install flow commits after this hook, but not every caller does. These writes
	# are what makes the site read as In Tech before anyone opens the settings.
	frappe.db.commit()  # nosemgrep: frappe-manual-commit


def after_migrate():
	seed_settings()
	apply_branding()


def before_uninstall():
	restore_branding()


def seed_settings():
	"""Fill in every setting the administrator has not set. Never overwrites a choice."""
	if not frappe.db.exists("DocType", SETTINGS_DOCTYPE):
		return

	settings = frappe.get_single(SETTINGS_DOCTYPE)
	changed = False
	for fieldname, value in DEFAULTS.items():
		field = settings.meta.get_field(fieldname)
		if not field or field.fieldtype in ("Table", "Attach Image"):
			continue
		current = settings.get(fieldname)
		if field.fieldtype == "Select":
			options = [o.strip() for o in (field.options or "").split("\n")]
			if current not in (None, "") and current not in options:
				# a value a later release no longer offers: land on the default, don't fail
				current = None
		if current in (None, ""):
			settings.set(fieldname, value)
			changed = True

	if changed:
		settings.flags.ignore_permissions = True
		settings.flags.intech_seeding = True
		settings.save(ignore_permissions=True)


def apply_branding():
	"""Sync the framework's own settings with In Tech Theme Settings."""
	settings = get_settings()
	if not cint(settings.enable_white_label):
		return

	_sync_system_settings(settings)
	_sync_website_settings(settings)
	_sync_navbar_settings(settings)

	frappe.clear_cache()


def _set_single(doctype: str, values: dict):
	"""Set fields on a Single without running its controller.

	These documents validate things that have nothing to do with branding (password policy,
	outgoing mail, redirects). A brand sync must not fail on a site whose mail server happens
	to be down, so the values go straight to the Singles table.
	"""
	if not frappe.db.exists("DocType", doctype):
		return

	meta = frappe.get_meta(doctype)
	for fieldname, value in values.items():
		if not meta.has_field(fieldname):
			# gone or renamed in this framework version: skip it, don't fail
			continue
		current = frappe.db.get_single_value(doctype, fieldname)
		if current == value:
			continue
		key = PREVIOUS.format(doctype=doctype, field=fieldname)
		if frappe.db.get_default(key) is None:
			frappe.db.set_default(key, "" if current is None else str(current))
		frappe.db.set_single_value(doctype, fieldname, value)


def _sync_system_settings(settings):
	values = {"app_name": settings.brand_name}

	if cint(settings.hide_update_notifications):
		# Both put the vendor's product names and release notes in front of users.
		values["disable_system_update_notification"] = 1
		values["disable_change_log_notification"] = 1

	if cint(settings.hide_vendor_promotions):
		values["disable_product_suggestion"] = 1

	if cint(settings.disable_vendor_telemetry):
		values["enable_telemetry"] = 0

	_set_single("System Settings", values)


def _sync_website_settings(settings):
	_set_single(
		"Website Settings",
		{
			"app_name": settings.brand_name,
			"app_logo": get_logo(),
			"favicon": get_favicon(),
			"splash_image": get_splash(),
			"copyright": get_copyright().lstrip("© ").strip(),
			# shown in place of the "Built on ..." line in the website footer
			"footer_powered": settings.brand_name,
		},
	)


def _sync_navbar_settings(settings):
	_set_single("Navbar Settings", {"app_logo": get_logo()})

	if not cint(settings.hide_vendor_help_links) or not frappe.db.exists("DocType", "Navbar Item"):
		return

	items = frappe.get_all(
		"Navbar Item",
		filters={"parent": "Navbar Settings", "hidden": 0},
		fields=["name", "item_label", "route"],
	)
	for item in items:
		# a row is the vendor's if it is named after them or leads to one of their sites
		if has_vendor_name(item.item_label) or is_vendor_url(item.route):
			frappe.db.set_value("Navbar Item", item.name, "hidden", 1, update_modified=False)
			frappe.db.set_default(f"intech:hid:{item.name}", "1")


def restore_branding():
	"""Put back every value `_set_single` replaced, and every help link it hid."""
	parked = frappe.get_all(
		"DefaultValue",
		filters={"parent": "__default", "defkey": ["like", "intech:%"]},
		fields=["defkey", "defvalue"],
	)
	for row in parked:
		key = row.defkey
		if key.startswith("intech:prev:"):
			_, _, doctype, field = key.split(":", 3)
			if frappe.db.exists("DocType", doctype) and frappe.get_meta(doctype).has_field(field):
				frappe.db.set_single_value(doctype, field, row.defvalue or None)
		elif key.startswith("intech:hid:"):
			name = key.split(":", 2)[2]
			if frappe.db.exists("Navbar Item", name):
				frappe.db.set_value("Navbar Item", name, "hidden", 0, update_modified=False)
		frappe.db.delete("DefaultValue", {"parent": "__default", "defkey": key})

	frappe.clear_cache()
