"""Brand the pages the server renders: the desk shell, login, portal, error and message pages."""

import re

import frappe
from frappe.utils import cint

from intech_theme.branding import (
	get_brand_name,
	get_copyright,
	get_favicon,
	get_logo,
	get_settings,
	get_splash,
	rebrand_text,
)
from intech_theme.palette import BRAND, DESK_BACKDROPS, SIDEBAR_STYLES, is_hex_color
from intech_theme.utils.text import has_vendor_name

# Never pages: API calls, static files, uploads, the socket.
SKIP_PREFIXES = ("/api", "/assets", "/files", "/private", "/socket.io")

# The desk shell carries the whole boot payload as inline JSON. That payload is handled
# field by field in `api/boot.py`; a blanket text pass over it would rename keys the client
# looks things up by. The desk gets the theme attributes and nothing else.
DESK_PREFIXES = ("/desk", "/app")

BUILT_ON_COMMENT = re.compile(r"<!--\s*Built on Frappe\..*?-->", re.IGNORECASE | re.DOTALL)
GENERATOR_META = re.compile(r"<meta[^>]+name=[\"']generator[\"'][^>]*>", re.IGNORECASE)
HTML_TAG = re.compile(r"<html\b", re.IGNORECASE)
HEAD_CLOSE = re.compile(r"</head>", re.IGNORECASE)

# Responses larger than this are downloads or reports, not pages.
MAX_PAGE_BYTES = 4 * 1024 * 1024


def update_website_context(context):
	"""Give every web template the brand, ahead of the vendor apps' own context."""
	settings = get_settings()
	if not cint(settings.enable_white_label):
		return None

	return {
		"app_name": get_brand_name(),
		"brand_name": get_brand_name(),
		"favicon": get_favicon(),
		"splash_image": get_splash(),
		"intech_logo": get_logo(),
		"intech_copyright": get_copyright(),
		"intech_support_url": settings.support_url,
		"intech_login_headline": settings.login_headline,
		"intech_login_subline": settings.login_subline,
	}


def theme_attributes(settings) -> str:
	"""The `<html>` attributes the stylesheets key off, so the first paint is already right."""
	sidebar = SIDEBAR_STYLES.get(settings.sidebar_style, "navy")
	backdrop = DESK_BACKDROPS.get(settings.desk_backdrop, "circuit")
	if backdrop == "image" and not settings.desk_background_image:
		backdrop = "circuit"
	attributes = {
		"data-intech": "1",
		"data-intech-sidebar": sidebar,
		"data-intech-backdrop": backdrop,
		"data-intech-menus": "colorful" if cint(settings.colorful_menus) else "plain",
		"data-intech-glass": "1" if cint(settings.glass_tiles) else "0",
	}
	return " ".join(f'{key}="{frappe.utils.escape_html(value)}"' for key, value in attributes.items())


def theme_style(settings) -> str:
	"""Inline custom properties for the colours an administrator may change."""

	def color(value, fallback):
		return value if is_hex_color(value) else fallback

	declarations = {
		"--it-primary": color(settings.primary_color, BRAND["primary"]),
		"--it-accent": color(settings.accent_color, BRAND["azure"]),
		"--it-ink": color(settings.ink_color, BRAND["ink"]),
	}
	if settings.login_background:
		declarations["--it-login-image"] = f"url('{_css_url(settings.login_background)}')"
	if settings.desk_background_image:
		declarations["--it-desk-image"] = f"url('{_css_url(settings.desk_background_image)}')"
	body = ";".join(f"{key}:{value}" for key, value in declarations.items())
	return f'<style id="intech-vars">:root{{{body}}}</style>'


def web_payload(settings) -> str:
	"""What the website and login scripts need, inline, so a guest page makes no request.

	Presentation only - names, images and copy a visitor is about to see anyway.
	"""
	from intech_theme.branding import DEFAULT_TILE, WORDMARK, WORDMARK_LIGHT

	payload = {
		"brand_name": get_brand_name(),
		"logo": get_logo(),
		"tile": DEFAULT_TILE,
		"wordmark": WORDMARK,
		"wordmark_light": WORDMARK_LIGHT,
		"tagline": settings.tagline or "",
		"login_headline": settings.login_headline or "",
		"login_subline": settings.login_subline or "",
		"has_login_image": 1 if settings.login_background else 0,
		"copyright": get_copyright(),
	}
	# `</` cannot appear inside the JSON, so the element cannot be closed from within.
	data = frappe.as_json(payload, indent=None).replace("</", "<\\/")
	return f'<script id="intech-web" type="application/json">{data}</script>'


def _css_url(value: str) -> str:
	# An attached file's URL, never markup: anything that could close the string goes.
	return re.sub(r"[\"'()\\<>\s]", "", value or "")


def after_request(response=None, request=None):
	"""Theme a server-rendered page, and take vendor names out of it, as it is sent."""
	try:
		_process_response(response, request)
	except Exception:
		# Branding is never worth a failed page. Log it and send the page as it was.
		frappe.log_error(title="In Tech: page branding failed")


def _is_page(response, request) -> bool:
	if response is None or request is None:
		return False
	if request.method != "GET" or request.path.startswith(SKIP_PREFIXES):
		return False
	if response.mimetype != "text/html" or response.direct_passthrough or response.is_streamed:
		return False
	length = response.content_length
	return length is None or length <= MAX_PAGE_BYTES


def _process_response(response, request):
	if not _is_page(response, request):
		return

	html = response.get_data(as_text=True)
	if not html or "data-intech=" in html:
		return

	settings = get_settings()
	themed = HTML_TAG.sub(f"<html {theme_attributes(settings)}", html, count=1)
	is_desk = request.path.startswith(DESK_PREFIXES)
	head = theme_style(settings) + ("" if is_desk else web_payload(settings))
	# a function, not a string, so a backslash in a URL is never read as a group reference
	themed = HEAD_CLOSE.sub(lambda _match: head + "</head>", themed, count=1)

	if cint(settings.enable_white_label) and not is_desk:
		themed = _rebrand_page(themed)

	if themed != html:
		response.set_data(themed)


def _rebrand_page(html: str) -> str:
	html = BUILT_ON_COMMENT.sub("", html, count=1)
	html = GENERATOR_META.sub("", html, count=1)
	if has_vendor_name(html):
		html = rebrand_text(html)
	return html
