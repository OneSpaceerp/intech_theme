"""What every installed app is called, and the tile it wears.

The desk learns an app's name and logo from three places: `frappe.boot.app_data` (the apps
screen on /desk, the dock's top slot and a dock-less sidebar's header), the App rows of
`frappe.boot.desktop_icons` (the Desktop Icons grid), and two whitelisted methods
(`frappe.apps.get_apps` for the setup wizard, `frappe.utils.change_log.get_versions` for
the About dialog). All three are answered from `app_identity` here, so an app cannot look
like In Tech in one place and like its vendor in another.
"""

import frappe
from frappe.utils import cint

from intech_theme.branding import get_brand_name, get_settings, is_vendor_asset, rebrand_text
from intech_theme.palette import APP_IDENTITIES, app_icon_url, monogram_icon

# The theme itself never takes a tile.
SELF = "intech_theme"


def replacing_apps(settings=None) -> bool:
	settings = settings or get_settings()
	return bool(cint(settings.enable_white_label) and cint(settings.replace_app_icons))


def app_identity(app: str, fallback_title: str | None = None, index: int = 0, settings=None) -> dict:
	"""`{"title", "icon"}` for `app`: the site's own row first, then the shipped identity,
	then a monogram tile and the app's own title with any vendor name taken out."""
	settings = settings or get_settings()
	own = next((row for row in settings.app_identities if row.app == app), None)
	shipped = APP_IDENTITIES.get(app) or {}

	title = (own and own.title) or shipped.get("title")
	if title == "In Tech ERP":
		# The ERP is the product, so it carries whatever the site calls itself.
		title = f"{get_brand_name()} ERP"
	if not title:
		title = rebrand_text(fallback_title or app.replace("_", " ").title())

	icon = (own and own.icon) or app_icon_url(app) or monogram_icon(title, index)
	return {"title": title, "icon": icon}


def brand_app_data(app_data: list | None, settings=None):
	"""Rename and re-tile `frappe.boot.app_data` in place."""
	if not app_data:
		return
	for index, app in enumerate(app_data):
		name = app.get("app_name")
		if not name or name == SELF:
			continue
		identity = app_identity(name, app.get("app_title"), index, settings)
		app["app_title"] = identity["title"]
		app["app_logo_url"] = identity["icon"]


def brand_desktop_icons(icons: list | None, settings=None):
	"""Re-tile the App rows of `frappe.boot.desktop_icons` in place.

	Labels are left alone: a saved desktop layout finds its icons by label. The tile's caption
	is renamed on screen instead, from `intech_title`.
	"""
	if not icons:
		return
	for index, icon in enumerate(icons):
		if icon.get("icon_type") != "App" or not icon.get("app") or icon.get("app") == SELF:
			continue
		identity = app_identity(icon["app"], icon.get("label"), index, settings)
		if icon.get("icon_image") and not is_vendor_asset(icon.get("icon_image")):
			# someone attached their own picture to this tile: theirs wins
			identity["icon"] = icon["icon_image"]
		icon["logo_url"] = identity["icon"]
		icon["intech_title"] = identity["title"]


@frappe.whitelist()
def get_apps() -> list[dict]:
	"""`frappe.apps.get_apps`, with every app's title and logo replaced."""
	from frappe.apps import get_apps as original

	apps = original()
	settings = get_settings()
	if not replacing_apps(settings):
		return apps

	branded = []
	for index, app in enumerate(apps):
		app = dict(app)
		identity = app_identity(app.get("name"), app.get("title"), index, settings)
		app["title"] = identity["title"]
		app["logo"] = identity["icon"]
		if app.get("setup_wizard_text"):
			app["setup_wizard_text"] = rebrand_text(app["setup_wizard_text"])
		branded.append(app)
	return branded


@frappe.whitelist()
def get_versions() -> dict:
	"""`frappe.utils.change_log.get_versions`, for the About dialog."""
	from frappe.utils.change_log import get_versions as original

	versions = original()
	settings = get_settings()
	if not cint(settings.enable_white_label):
		return versions

	for index, (app, details) in enumerate(versions.items()):
		identity = app_identity(app, details.get("title"), index, settings)
		details["title"] = identity["title"]
		details["description"] = rebrand_text(details.get("description"))
		details["logo"] = identity["icon"]
	return versions
