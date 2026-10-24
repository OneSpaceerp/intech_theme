"""The In Tech palette, app identities and desk backdrops.

Every colour the theme paints comes from here, so the stylesheets, the boot payload, the
icon generator and the tests can never disagree about what "In Tech blue" is.

This module imports nothing from `frappe`: `tools/build_app_icons.py` and the unit tests
load it without a bench.

The brand colours were sampled from the supplied logo (`intech_logo.jpg`):

    ink      #1E2448   the "T" and the INTECH wordmark
    deep     #245490   the darkest circuit trace
    primary  #2472AE   the middle traces
    azure    #1E90D2   the brightest traces
    steel    #7898B8   the shadowed edge of the app tile
    mist     #ABC7DA   the app tile's body
    ice      #C3DFEC   the app tile's highlight
"""

BRAND = {
	"ink": "#1E2448",
	"deep": "#245490",
	"primary": "#2472AE",
	"azure": "#1E90D2",
	"steel": "#7898B8",
	"mist": "#ABC7DA",
	"ice": "#C3DFEC",
}

# Eight hues per menu palette. Sidebar and dock entries take them in turn, so neighbouring
# entries never share a colour. Every hue clears 3:1 against white (icon chips are filled,
# and the glyph on them is white), and the spectrum leads with the brand's own blues.
MENU_PALETTES = {
	"In Tech Spectrum": [
		"#1E90D2",  # azure
		"#2472AE",  # primary
		"#6D5BD0",  # indigo
		"#0F9D9A",  # teal
		"#D9480F",  # ember
		"#2B8A3E",  # green
		"#C2255C",  # raspberry
		"#B7791F",  # amber
	],
	"Ocean": [
		"#1E90D2",
		"#2472AE",
		"#245490",
		"#0B7285",
		"#1971C2",
		"#3B5BDB",
		"#0C8599",
		"#364FC7",
	],
	"Vivid": [
		"#E8590C",
		"#7048E8",
		"#0CA678",
		"#D6336C",
		"#1C7ED6",
		"#C96F00",
		"#AE3EC9",
		"#2F9E44",
	],
	"Brand Mono": [
		"#2472AE",
		"#245490",
		"#1E90D2",
		"#2472AE",
		"#245490",
		"#1E90D2",
		"#2472AE",
		"#245490",
	],
}
DEFAULT_MENU_PALETTE = "In Tech Spectrum"

SIDEBAR_STYLES = {
	"Navy": "navy",  # the brand ink, white text
	"Gradient": "gradient",  # ink to deep blue, with the circuit motif
	"Light": "light",  # ice surface, ink text
}
DEFAULT_SIDEBAR_STYLE = "Navy"

# `/desk` backdrops. Each is pure CSS plus an inline SVG, so none costs a download.
DESK_BACKDROPS = {
	"Circuit": "circuit",  # the logo's traces, drawn large across the page
	"Aurora": "aurora",  # soft brand-coloured light
	"Mesh": "mesh",  # a gradient mesh in the four blues
	"Waves": "waves",  # layered waves along the foot of the page
	"Image": "image",  # an uploaded picture, under a brand-tinted scrim
	"None": "none",
}
DEFAULT_DESK_BACKDROP = "Circuit"

# What each app is called and how its tile looks on the apps screen, the dock and the
# sidebar header. `glyph` names a drawing in tools/build_app_icons.py; `colors` is the tile's
# gradient. An app missing from here gets a monogram tile in the brand blues (see
# `monogram_icon`), so a newly installed app never shows its vendor's logo either.
#
# The ERP itself wears the In Tech mark, redrawn as a tile like the others: it is the product
# the site is selling.
APP_IDENTITIES = {
	"erpnext": {"title": "In Tech ERP", "glyph": "intech", "colors": ("#1E90D2", "#1E2448")},
	"frappe": {"title": "Platform", "glyph": "platform", "colors": ("#245490", "#1E2448")},
	"hrms": {"title": "People", "glyph": "people", "colors": ("#0F9D9A", "#0B5F73")},
	"crm": {"title": "CRM", "glyph": "crm", "colors": ("#D9480F", "#A61E4D")},
	"helpdesk": {"title": "Helpdesk", "glyph": "helpdesk", "colors": ("#6D5BD0", "#3B2C8F")},
	"lms": {"title": "Learning", "glyph": "learning", "colors": ("#2B8A3E", "#145A32")},
	"insights": {"title": "Insights", "glyph": "insights", "colors": ("#1E90D2", "#245490")},
	"payments": {"title": "Payments", "glyph": "payments", "colors": ("#B7791F", "#7C4A03")},
	"drive": {"title": "Drive", "glyph": "drive", "colors": ("#1C7ED6", "#1E2448")},
	"wiki": {"title": "Knowledge Base", "glyph": "wiki", "colors": ("#0B7285", "#1E2448")},
	"builder": {"title": "Site Builder", "glyph": "builder", "colors": ("#C2255C", "#5F1A37")},
	"gameplan": {"title": "Teamspace", "glyph": "teamspace", "colors": ("#7048E8", "#1E2448")},
	"raven": {"title": "Chat", "glyph": "chat", "colors": ("#0CA678", "#0B5F73")},
	"print_designer": {"title": "Print Studio", "glyph": "print", "colors": ("#495057", "#1E2448")},
	"india_compliance": {"title": "Compliance", "glyph": "shield", "colors": ("#2472AE", "#1E2448")},
	"webshop": {"title": "Store", "glyph": "store", "colors": ("#E8590C", "#7C2D12")},
	"education": {"title": "Education", "glyph": "learning", "colors": ("#3B5BDB", "#1E2448")},
	"healthcare": {"title": "Healthcare", "glyph": "health", "colors": ("#E03131", "#7A1F1F")},
	"lending": {"title": "Lending", "glyph": "payments", "colors": ("#0C8599", "#1E2448")},
	"erpnext_pos": {"title": "Point of Sale", "glyph": "store", "colors": ("#1E90D2", "#1E2448")},
	"posawesome": {"title": "Point of Sale", "glyph": "store", "colors": ("#1E90D2", "#1E2448")},
}

ICON_DIR = "/assets/intech_theme/icons/apps"
BRAND_TILE = "/assets/intech_theme/images/intech-tile-250.png"


def app_icon_url(app: str) -> str | None:
	"""URL of the shipped tile for `app`, or None when the app has no tile of its own."""
	identity = APP_IDENTITIES.get(app)
	if not identity:
		return None
	return f"{ICON_DIR}/{app}.svg"


def menu_palette(name: str | None) -> list[str]:
	return list(MENU_PALETTES.get(name or "", MENU_PALETTES[DEFAULT_MENU_PALETTE]))


def monogram_icon(title: str | None, index: int = 0) -> str:
	"""A tile for an app the theme does not know, as an inline SVG data URI.

	The letter is the app's own initial; the colour is taken from the spectrum by `index`, so
	two unknown apps side by side do not look like one.
	"""
	from urllib.parse import quote

	letter = ((title or "?").strip()[:1] or "?").upper()
	if not letter.isalnum():
		letter = "?"
	hues = MENU_PALETTES[DEFAULT_MENU_PALETTE]
	top = hues[index % len(hues)]
	svg = (
		'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">'
		'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
		f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{BRAND["ink"]}"/>'
		"</linearGradient></defs>"
		'<rect width="96" height="96" rx="24" fill="url(#g)"/>'
		'<path d="M62 18h16M70 18v8M18 74h12" stroke="#fff" stroke-opacity=".22" '
		'stroke-width="3" stroke-linecap="round" fill="none"/>'
		'<text x="48" y="62" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" '
		f'font-size="44" font-weight="700" fill="#fff">{letter}</text></svg>'
	)
	return "data:image/svg+xml;charset=utf-8," + quote(svg)


def is_hex_color(value: str | None) -> bool:
	if not value or not isinstance(value, str):
		return False
	value = value.strip()
	if not value.startswith("#") or len(value) not in (4, 7):
		return False
	return all(c in "0123456789abcdefABCDEF" for c in value[1:])
