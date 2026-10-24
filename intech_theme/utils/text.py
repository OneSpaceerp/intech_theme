"""Vendor-name replacement for on-screen text.

This module is deliberately free of any `frappe` import: the translation generator in
`tools/` and the unit tests run it without a bench.
"""

import re

DEFAULT_BRAND = "In Tech"
DEFAULT_BRAND_AR = "In Tech"

# A vendor name counts only as a standalone word of prose. The guards keep identifiers
# (`ERPNextTestSuite`), paths (`/assets/frappe/`), emails and domains (`Frappe.io`) intact,
# because those are addresses, not words, and rewriting them breaks whatever they point at.
#
# The guards test for ASCII neighbours only. Chinese and Japanese run a product name
# straight into the next word with no space, and those neighbours must not shield it.
_BEFORE = r"(?<![A-Za-z0-9_/.@#])"
_AFTER = r"(?![A-Za-z0-9_@]|[./][A-Za-z0-9_])"

# Translated prose inflects names: Hungarian writes "ERPNextet", Uzbek "Frappega". The
# loose guard lets a name carry such a suffix. It is for translated sentences only.
_AFTER_LOOSE = r"(?![0-9_@]|[./][A-Za-z0-9_])"

_PUBLISHER = re.compile(
	_BEFORE + r"Frappe Technologies(?:,? Pvt\.? Ltd\.?)?(?:,? and [Cc]ontributors)?" + r"(?![A-Za-z0-9_@])"
)

_NAMES = r"(?:Frappe Framework|Frappe Cloud|Frappe Mail|Frappe School|Frappe Support|ERPNext|Frappe)"

# Longest names first: "Frappe Framework" has to go before the bare "Frappe" does.
_PRODUCTS = re.compile(_BEFORE + _NAMES + _AFTER)
_PRODUCTS_LOOSE = re.compile(_BEFORE + _NAMES + _AFTER_LOOSE)

_SUFFIXED = {
	"Frappe Cloud": "{brand} Cloud",
	"Frappe Mail": "{brand} Mail",
	"Frappe School": "{brand} Academy",
	"Frappe Support": "{brand} Support",
}

VENDOR_WORD = re.compile(_BEFORE + r"(?:ERPNext|Frappe)" + _AFTER)

# Hosts that lead back to the vendor. Used for links, never for prose.
VENDOR_HOSTS = (
	"frappe.io",
	"frappeframework.com",
	"frappecloud.com",
	"frappe.cloud",
	"frappe.school",
	"erpnext.com",
	"erpnext.org",
	"github.com/frappe",
)

VENDOR_URL = re.compile(
	r"https?://[^\s\"'<>)]*(?:" + "|".join(re.escape(host) for host in VENDOR_HOSTS) + r")[^\s\"'<>)]*",
	re.IGNORECASE,
)


def has_vendor_name(text: str | None) -> bool:
	"""True if `text` holds a vendor name that `rebrand` would change."""
	if not text or not isinstance(text, str):
		return False
	return bool(VENDOR_WORD.search(text) or _PUBLISHER.search(text))


def rebrand(text: str | None, brand: str = DEFAULT_BRAND, loose: bool = False) -> str | None:
	"""Return `text` with every vendor product name replaced by `brand`.

	Safe to run more than once and on text that holds no vendor name at all. Pass
	`loose=True` for translated sentences, where a name may carry a grammatical suffix.
	"""
	if not text or not isinstance(text, str):
		return text

	# Cheap rejection: nearly every string in the system holds neither word.
	if "Frappe" not in text and "ERPNext" not in text:
		return text

	def _product(match: re.Match) -> str:
		return _SUFFIXED.get(match.group(0), "{brand}").format(brand=brand)

	text = _PUBLISHER.sub(brand, text)
	text = (_PRODUCTS_LOOSE if loose else _PRODUCTS).sub(_product, text)

	if not brand:
		return text

	# "Frappe ERPNext" and the like would otherwise read "In Tech In Tech".
	doubled = re.escape(brand)
	text = re.sub(rf"{doubled}(?:\s+{doubled})+", brand, text)

	# "A Frappe instance" must not become "A In Tech instance".
	if brand[0].lower() in "aeiou":
		text = re.sub(rf"\b([Aa])(?= {doubled})", r"\1n", text)
	return text


def is_vendor_url(url: str | None) -> bool:
	"""True if `url` points at one of the vendor's own sites."""
	if not url or not isinstance(url, str):
		return False
	lowered = url.lower()
	return any(host in lowered for host in VENDOR_HOSTS)


def replace_vendor_urls(text: str | None, replacement: str = "") -> str | None:
	"""Swap vendor URLs written out in prose for `replacement`."""
	if not text or not isinstance(text, str) or "http" not in text:
		return text
	return VENDOR_URL.sub(replacement, text)
