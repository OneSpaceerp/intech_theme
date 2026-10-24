#!/usr/bin/env python3
"""Draw the app tiles in `intech_theme/public/icons/apps/`.

One SVG per app in `palette.APP_IDENTITIES`: a rounded square in the app's gradient, the
logo's circuit traces in one corner, and a white line glyph. Re-run after editing the
identities:

    python tools/build_app_icons.py

Standard library only; no bench needed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("palette", ROOT / "intech_theme" / "palette.py")
palette = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(palette)

OUT = ROOT / "intech_theme" / "public" / "icons" / "apps"

# Line drawings on a 96-unit canvas, stroked white. Kept to a 28..68 box so every glyph sits
# at the same optical size.
GLYPHS = {
	"platform": """
		<path d="M48 26 70 37 48 48 26 37Z"/>
		<path d="M26 48 48 59 70 48"/>
		<path d="M26 59 48 70 70 59"/>""",
	"people": """
		<circle cx="40" cy="38" r="8"/>
		<path d="M26 66c0-9 6-15 14-15s14 6 14 15"/>
		<circle cx="60" cy="40" r="6"/>
		<path d="M58 52c7 0 12 5 12 13"/>""",
	"crm": """
		<circle cx="48" cy="48" r="20"/>
		<circle cx="48" cy="48" r="11"/>
		<circle cx="48" cy="48" r="3" fill="#fff"/>
		<path d="M62 34 72 24"/>""",
	"helpdesk": """
		<path d="M28 52v-6a20 20 0 0 1 40 0v6"/>
		<rect x="26" y="50" width="9" height="14" rx="3"/>
		<rect x="61" y="50" width="9" height="14" rx="3"/>
		<path d="M66 64c0 5-5 7-12 7h-4"/>""",
	"learning": """
		<path d="M24 40 48 30 72 40 48 50Z"/>
		<path d="M34 45v11c0 4 6 8 14 8s14-4 14-8V45"/>
		<path d="M72 40v14"/>""",
	"insights": """
		<path d="M28 68h40"/>
		<path d="M34 68V52"/>
		<path d="M45 68V42"/>
		<path d="M56 68V48"/>
		<path d="M67 68V32"/>
		<path d="M30 44 44 34l10 7 14-13"/>""",
	"payments": """
		<rect x="24" y="32" width="48" height="32" rx="6"/>
		<path d="M24 42h48"/>
		<path d="M32 55h12"/>""",
	"drive": """
		<path d="M26 36a4 4 0 0 1 4-4h12l5 6h19a4 4 0 0 1 4 4v20a4 4 0 0 1-4 4H30a4 4 0 0 1-4-4Z"/>
		<path d="M38 52h20"/>""",
	"wiki": """
		<path d="M48 34c-6-4-14-5-22-4v32c8-1 16 0 22 4 6-4 14-5 22-4V30c-8-1-16 0-22 4Z"/>
		<path d="M48 34v32"/>""",
	"builder": """
		<rect x="26" y="28" width="44" height="40" rx="5"/>
		<path d="M26 38h44"/>
		<path d="M40 38v30"/>
		<path d="M48 48h14M48 56h10"/>""",
	"teamspace": """
		<rect x="24" y="30" width="28" height="20" rx="5"/>
		<rect x="44" y="46" width="28" height="20" rx="5"/>
		<path d="M32 50v8l6-6"/>""",
	"chat": """
		<path d="M26 34a6 6 0 0 1 6-6h32a6 6 0 0 1 6 6v20a6 6 0 0 1-6 6H44l-10 9v-9h-2a6 6 0 0 1-6-6Z"/>
		<path d="M36 42h24M36 50h16"/>""",
	"print": """
		<path d="M34 40V26h28v14"/>
		<rect x="24" y="40" width="48" height="20" rx="5"/>
		<path d="M34 54h28v14H34Z"/>""",
	"shield": """
		<path d="M48 24 70 32v14c0 14-9 23-22 28-13-5-22-14-22-28V32Z"/>
		<path d="m38 48 7 7 13-13"/>""",
	"store": """
		<path d="M24 30h7l6 26h26l6-18H36"/>
		<circle cx="40" cy="64" r="3.5"/>
		<circle cx="60" cy="64" r="3.5"/>""",
	"health": """
		<path d="M42 26h12v16h16v12H54v16H42V54H26V42h16Z"/>""",
}

# The In Tech mark itself, redrawn for the ERP's tile: the slanted T with its node, and the
# circuit traces fanning out on either side in the logo's two blues. It brings its own
# traces, so the corner set below is left off this one tile.
INTECH_MARK = """
	<g fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.8">
		<g stroke="#8FD3FF">
			<path d="M43 53 26 59.4"/><circle cx="23" cy="60.5" r="3"/>
			<path d="M45 62 31 67.2"/><circle cx="28" cy="68.3" r="3"/>
			<path d="M47 71 37 74.7"/><circle cx="34" cy="75.8" r="3"/>
		</g>
		<g stroke="#C3DFEC">
			<path d="M64 41 75 36.9"/><circle cx="78" cy="35.8" r="3"/>
			<path d="M66 50 79 45.1"/><circle cx="82" cy="44" r="3"/>
			<path d="M68 59 78 55.3"/><circle cx="81" cy="54.2" r="3"/>
			<path d="M52 24 63 19.9"/><circle cx="66" cy="18.8" r="3"/>
		</g>
		<path d="M20 47 76 26" stroke="#fff" stroke-width="8"/>
		<path d="M45 41 52 76" stroke="#fff" stroke-width="6"/>
		<path d="M54 38 61 73" stroke="#fff" stroke-width="6"/>
	</g>
	<circle cx="38" cy="32" r="5.2" fill="#fff"/>"""

# The logo's circuit traces, small, in the tile's top right corner.
TRACES = """
	<g stroke="#fff" stroke-opacity=".28" stroke-width="2.4" fill="none" stroke-linecap="round">
		<path d="M60 14h14l8 8"/><circle cx="84" cy="24" r="2.6"/>
		<path d="M66 22h6l6 6"/><circle cx="80" cy="30" r="2.2"/>
	</g>"""


def tile(identity: dict) -> str:
	top, bottom = identity["colors"]
	if identity["glyph"] == "intech":
		traces, glyph = "", ""
		mark = INTECH_MARK
	else:
		traces, glyph, mark = TRACES, GLYPHS[identity["glyph"]], ""
	return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" role="img" aria-label="{identity["title"]}">
	<defs>
		<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
			<stop offset="0" stop-color="{top}"/>
			<stop offset="1" stop-color="{bottom}"/>
		</linearGradient>
		<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
			<stop offset="0" stop-color="#fff" stop-opacity=".22"/>
			<stop offset=".55" stop-color="#fff" stop-opacity="0"/>
		</linearGradient>
	</defs>
	<rect width="96" height="96" rx="24" fill="url(#bg)"/>
	<rect width="96" height="96" rx="24" fill="url(#sheen)"/>{traces}{mark}
	<g stroke="#fff" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round">{glyph}
	</g>
</svg>
"""


def main() -> int:
	OUT.mkdir(parents=True, exist_ok=True)
	written = 0
	for app, identity in palette.APP_IDENTITIES.items():
		(OUT / f"{app}.svg").write_text(tile(identity), encoding="utf-8")
		written += 1
	print(f"wrote {written} tiles to {OUT}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
