"""Desk boot: hand the client its theme, and take the vendor out of the payload.

Everything the desk bundle needs rides on `frappe.boot.intech`, so opening the desk costs no
request of its own and the first paint is already In Tech. Saving In Tech Theme Settings makes
every open desk call `get_client_settings` and repaint (see `public/js/intech-boot.js`).
"""

import frappe
from frappe.utils import cint

from intech_theme import __version__
from intech_theme.api.apps import brand_app_data, brand_desktop_icons, replacing_apps
from intech_theme.branding import (
	DEFAULT_TILE,
	WORDMARK,
	WORDMARK_LIGHT,
	get_brand_name,
	get_copyright,
	get_favicon,
	get_logo,
	get_logo_dark,
	get_product_name,
	get_settings,
	is_vendor_asset,
)
from intech_theme.palette import (
	BRAND,
	DESK_BACKDROPS,
	SIDEBAR_STYLES,
	is_hex_color,
	menu_palette,
)

# Keys under which the boot payload carries an image the user will see.
LOGO_KEYS = frozenset({"logo", "logo_url", "app_logo_url", "brand_logo"})

FONTS = ("Inter", "Poppins", "Manrope", "IBM Plex Sans", "Cairo", "System")


def extend_bootinfo(bootinfo):
	settings = get_settings()
	bootinfo.intech = client_settings(settings)

	if not cint(settings.enable_white_label):
		return

	logo = get_logo()
	bootinfo.app_logo_url = logo

	if replacing_apps(settings):
		brand_app_data(bootinfo.get("app_data"), settings)
		brand_desktop_icons(bootinfo.get("desktop_icons"), settings)

	# Anything still pointing at a vendor's mark - the dock, a module's sidebar - gets ours.
	for key in ("app_data", "apps_data", "desktop_icons", "dock", "module_sidebars"):
		_replace_vendor_logos(bootinfo.get(key), logo)


def _color(value, fallback):
	return value if is_hex_color(value) else fallback


@frappe.whitelist()
def get_client_settings() -> dict:
	"""The desk's theme, fetched again after In Tech Theme Settings is saved."""
	return client_settings(get_settings())


def client_settings(settings) -> dict:
	"""The slice of In Tech Theme Settings the desk bundle needs. Nothing here is secret."""
	white_label = cint(settings.enable_white_label)
	backdrop = DESK_BACKDROPS.get(settings.desk_backdrop, "circuit")
	if backdrop == "image" and not settings.desk_background_image:
		backdrop = "circuit"

	return {
		"version": __version__,
		"brand_name": get_brand_name(),
		"product_name": get_product_name(),
		"tagline": settings.tagline,
		"logo": get_logo(),
		"logo_dark": get_logo_dark(),
		"tile": DEFAULT_TILE,
		"wordmark": WORDMARK,
		"wordmark_light": WORDMARK_LIGHT,
		"favicon": get_favicon(),
		"copyright": get_copyright(),
		"support_url": settings.support_url,
		# white label
		"white_label": white_label,
		"scrub_text": int(white_label and cint(settings.scrub_interface_text)),
		"replace_app_icons": int(white_label and cint(settings.replace_app_icons)),
		"hide_help_links": int(white_label and cint(settings.hide_vendor_help_links)),
		"hide_promotions": int(white_label and cint(settings.hide_vendor_promotions)),
		# palette
		"colors": {
			"primary": _color(settings.primary_color, BRAND["primary"]),
			"accent": _color(settings.accent_color, BRAND["azure"]),
			"ink": _color(settings.ink_color, BRAND["ink"]),
			"deep": BRAND["deep"],
			"steel": BRAND["steel"],
			"mist": BRAND["mist"],
			"ice": BRAND["ice"],
		},
		"sidebar_style": SIDEBAR_STYLES.get(settings.sidebar_style, "navy"),
		"colorful_menus": cint(settings.colorful_menus),
		"menu_colors": menu_palette(settings.menu_palette),
		"force_dark": cint(settings.force_dark_mode),
		"font_family": settings.font_family if settings.font_family in FONTS else "Inter",
		# the English / Arabic switcher, and the language the interface is in now
		"show_language_switcher": cint(settings.show_language_switcher),
		"language": (getattr(frappe.local, "lang", None) or "en").split("-")[0],
		# /desk
		"desk_backdrop": backdrop,
		"desk_background_image": settings.desk_background_image or "",
		"backdrop_dim": min(max(cint(settings.backdrop_dim), 0), 80),
		"show_desk_greeting": cint(settings.show_desk_greeting),
		"glass_tiles": cint(settings.glass_tiles),
		"backdrop_on_workspaces": cint(settings.backdrop_on_workspaces),
		# Every installed app's In Tech name and tile. The server re-tiles what it can reach;
		# `apps_data` is added to the boot after this hook runs, so the browser finishes it
		# from this map (see intech-whitelabel.js).
		"apps": _app_identities(settings) if white_label and cint(settings.replace_app_icons) else {},
		"full_name": frappe.utils.get_fullname(frappe.session.user) if frappe.session.user != "Guest" else "",
		"can_edit_theme": int("System Manager" in frappe.get_roles()),
	}


def _app_identities(settings) -> dict:
	from intech_theme.api.apps import SELF, app_identity

	identities = {}
	for index, app in enumerate(frappe.get_installed_apps()):
		if app == SELF:
			continue
		title = (frappe.get_hooks("app_title", app_name=app) or [None])[0]
		identities[app] = app_identity(app, title, index, settings)
	return identities


def _replace_vendor_logos(node, logo: str, depth: int = 0):
	"""Walk a boot subtree in place, swapping vendor logo files for the brand's."""
	if depth > 8 or node is None:
		return
	if isinstance(node, dict):
		for key, value in node.items():
			if key in LOGO_KEYS:
				if is_vendor_asset(value):
					node[key] = logo
			elif isinstance(value, dict | list):
				_replace_vendor_logos(value, logo, depth + 1)
	elif isinstance(node, list):
		for item in node:
			_replace_vendor_logos(item, logo, depth + 1)
