"""The brand, as the rest of the app reads it.

Everything that needs the brand name, a logo or a white-label switch asks here, so the
`In Tech Theme Settings` document stays the single place those answers come from.
"""

import frappe
from frappe.utils import cint

from intech_theme.palette import (
	BRAND,
	DEFAULT_DESK_BACKDROP,
	DEFAULT_MENU_PALETTE,
	DEFAULT_SIDEBAR_STYLE,
)
from intech_theme.utils.text import DEFAULT_BRAND, is_vendor_url, rebrand

SETTINGS_DOCTYPE = "In Tech Theme Settings"
DEFAULT_PRODUCT = "Al Mandoos ERP"
DEFAULT_PRODUCT_AR = "المندوس لإدارة المؤسسات"

ASSETS = "/assets/intech_theme/images"
DEFAULT_LOGO = f"{ASSETS}/intech-mark-256.png"
DEFAULT_LOGO_DARK = f"{ASSETS}/intech-mark-light-256.png"
DEFAULT_TILE = f"{ASSETS}/intech-tile-250.png"
DEFAULT_FAVICON = f"{ASSETS}/favicon-64.png"
DEFAULT_SPLASH = f"{ASSETS}/intech-logo-stacked.png"
WORDMARK = f"{ASSETS}/intech-wordmark.png"
WORDMARK_LIGHT = f"{ASSETS}/intech-wordmark-light.png"

# The apps whose logo, wordmark and favicon files count as the vendor's. Any app the site
# installs has its tile replaced through the app identities; this list is for the stray
# files the framework points at directly (`/assets/frappe/images/frappe-favicon.svg`).
VENDOR_APPS = ("frappe", "erpnext", "hrms", "crm", "helpdesk", "lms", "insights", "payments")

# Used when the settings document cannot be read at all: mid-install, mid-migrate, or before
# the DocType's table exists. The brand must still be right in those moments.
DEFAULTS = frappe._dict(
	brand_name=DEFAULT_BRAND,
	brand_name_ar="",
	product_name=DEFAULT_PRODUCT,
	product_name_ar=DEFAULT_PRODUCT_AR,
	tagline="Intelligent business, connected.",
	app_logo="",
	app_logo_dark="",
	favicon="",
	splash_image="",
	copyright_text="",
	support_url="",
	email_footer_text="",
	enable_white_label=1,
	scrub_interface_text=1,
	replace_app_icons=1,
	hide_vendor_help_links=1,
	hide_vendor_promotions=1,
	hide_update_notifications=1,
	disable_vendor_telemetry=1,
	primary_color=BRAND["primary"],
	accent_color=BRAND["azure"],
	ink_color=BRAND["ink"],
	sidebar_style=DEFAULT_SIDEBAR_STYLE,
	colorful_menus=1,
	menu_palette=DEFAULT_MENU_PALETTE,
	force_dark_mode=0,
	font_family="Inter",
	show_language_switcher=1,
	desk_backdrop=DEFAULT_DESK_BACKDROP,
	desk_background_image="",
	backdrop_dim=35,
	show_desk_greeting=1,
	glass_tiles=1,
	backdrop_on_workspaces=0,
	app_identities=[],
	login_headline="Run your whole business from one place",
	login_subline="Finance, people, stock and sales — connected, secure and always up to date.",
	login_background="",
)


def get_settings() -> frappe._dict:
	"""The settings document's values, falling back to the defaults field by field."""
	values = frappe._dict(DEFAULTS)
	try:
		doc = frappe.get_cached_doc(SETTINGS_DOCTYPE)
	except Exception:
		# No table yet, or no site context worth trusting. The defaults are the brand.
		return values

	for key in DEFAULTS:
		value = doc.get(key)
		if key == "app_identities":
			values[key] = [
				frappe._dict(app=row.app.strip(), title=row.title, icon=row.icon)
				for row in (value or [])
				if row.app
			]
		elif value not in (None, ""):
			values[key] = value
	return values


def white_label_enabled() -> bool:
	return bool(cint(get_settings().enable_white_label))


def get_brand_name(lang: str | None = None) -> str:
	settings = get_settings()
	lang = (lang or getattr(frappe.local, "lang", None) or "en").split("-")[0]
	if lang == "ar" and settings.brand_name_ar:
		return settings.brand_name_ar
	return settings.brand_name or DEFAULT_BRAND


def get_product_name(lang: str | None = None) -> str:
	settings = get_settings()
	lang = (lang or getattr(frappe.local, "lang", None) or "en").split("-")[0]
	if lang == "ar" and settings.product_name_ar:
		return settings.product_name_ar
	return settings.product_name or DEFAULT_PRODUCT


def get_logo() -> str:
	return get_settings().app_logo or DEFAULT_LOGO


def get_logo_dark() -> str:
	settings = get_settings()
	return settings.app_logo_dark or (settings.app_logo if settings.app_logo else DEFAULT_LOGO_DARK)


def get_favicon() -> str:
	return get_settings().favicon or DEFAULT_FAVICON


def get_splash() -> str:
	settings = get_settings()
	return settings.splash_image or settings.app_logo or DEFAULT_SPLASH


def get_copyright() -> str:
	settings = get_settings()
	if settings.copyright_text:
		return settings.copyright_text
	return f"© {frappe.utils.nowdate()[:4]} {settings.brand_name or DEFAULT_BRAND}"


def rebrand_text(text: str | None, lang: str | None = None) -> str | None:
	"""`rebrand` with the site's own brand name for the language in use."""
	return rebrand(text, get_brand_name(lang))


def vendor_asset_app(url) -> str | None:
	"""The vendor app that ships `url` as its logo, wordmark or favicon, if one does."""
	if isinstance(url, list | tuple):
		url = url[0] if url else None
	if not url or not isinstance(url, str):
		return None
	path = url.split("?", 1)[0]
	name = path.rsplit("/", 1)[-1].lower()
	# Module icons live beside the logos (`/assets/erpnext/icons/desktop_icons/...`) and each
	# one means something, so only the files that are a vendor's mark count.
	if not any(marker in name for marker in ("logo", "favicon", "wordmark", "splash")):
		return None
	for app in VENDOR_APPS:
		if path.startswith(f"/assets/{app}/"):
			return app
	return None


def is_vendor_asset(url) -> bool:
	return vendor_asset_app(url) is not None


__all__ = [
	"DEFAULTS",
	"DEFAULT_LOGO",
	"DEFAULT_TILE",
	"SETTINGS_DOCTYPE",
	"get_brand_name",
	"get_copyright",
	"get_favicon",
	"get_logo",
	"get_logo_dark",
	"get_settings",
	"get_splash",
	"is_vendor_asset",
	"is_vendor_url",
	"rebrand_text",
	"vendor_asset_app",
	"white_label_enabled",
]
