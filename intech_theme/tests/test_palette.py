"""Tests for the palette, the app identities and the shipped artwork. They need no bench:

python intech_theme/tests/test_palette.py
"""

import importlib.util
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("it_palette", ROOT / "palette.py")
palette = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(palette)

PUBLIC = ROOT / "public"


def asset_path(url: str) -> Path:
	assert url.startswith("/assets/intech_theme/"), url
	return PUBLIC / url[len("/assets/intech_theme/") :]


def luminance(hex_color: str) -> float:
	hex_color = hex_color.lstrip("#")
	channels = [int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4)]
	linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
	return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: str, b: str) -> float:
	la, lb = sorted((luminance(a), luminance(b)), reverse=True)
	return (la + 0.05) / (lb + 0.05)


class TestPalette(unittest.TestCase):
	def test_every_menu_palette_has_eight_hues(self):
		for name, hues in palette.MENU_PALETTES.items():
			self.assertEqual(len(hues), 8, name)
			for hue in hues:
				self.assertTrue(palette.is_hex_color(hue), f"{name}: {hue}")

	def test_white_glyphs_read_on_every_menu_hue(self):
		# The chips carry a white glyph; 3:1 is the floor for graphical objects (WCAG 1.4.11).
		for name, hues in palette.MENU_PALETTES.items():
			for hue in hues:
				self.assertGreaterEqual(contrast(hue, "#FFFFFF"), 3.0, f"{name}: {hue}")

	def test_brand_ink_reads_on_the_ice_surfaces(self):
		self.assertGreaterEqual(contrast(palette.BRAND["ink"], palette.BRAND["ice"]), 7.0)
		self.assertGreaterEqual(contrast(palette.BRAND["ink"], "#FFFFFF"), 7.0)

	def test_hex_validation(self):
		self.assertTrue(palette.is_hex_color("#2472AE"))
		self.assertTrue(palette.is_hex_color("#fff"))
		for bad in ("2472AE", "#2472AG", "red", "#12345", "", None, "#fff;background:url(x)"):
			self.assertFalse(palette.is_hex_color(bad), bad)


class TestAppIdentities(unittest.TestCase):
	def test_every_identity_has_a_shipped_tile(self):
		for app in palette.APP_IDENTITIES:
			url = palette.app_icon_url(app)
			self.assertIsNotNone(url, app)
			self.assertTrue(asset_path(url).exists(), f"{app}: {url} is not shipped")

	def test_no_identity_names_the_vendor(self):
		for app, identity in palette.APP_IDENTITIES.items():
			self.assertNotRegex(identity["title"], r"Frappe|ERPNext", app)

	def test_unknown_app_gets_a_monogram(self):
		self.assertIsNone(palette.app_icon_url("an_app_nobody_knows"))
		tile = palette.monogram_icon("Zebra Logistics", 3)
		self.assertTrue(tile.startswith("data:image/svg+xml"))
		self.assertIn(">Z</text>", unquote(tile))

	def test_monogram_never_carries_markup_from_a_title(self):
		tile = unquote(palette.monogram_icon("<script>alert(1)</script>"))
		self.assertNotIn("<script", tile)
		self.assertIn(">?</text>", tile)


class TestArtwork(unittest.TestCase):
	def test_backdrops_and_images_are_shipped(self):
		for name in (
			"images/backdrops/circuit.svg",
			"images/backdrops/circuit-corner.svg",
			"images/backdrops/waves.svg",
			"images/intech-mark-256.png",
			"images/intech-mark-light-256.png",
			"images/intech-tile-250.png",
			"images/intech-wordmark.png",
			"images/intech-wordmark-light.png",
			"images/intech-logo-stacked.png",
			"images/favicon-64.png",
		):
			self.assertTrue((PUBLIC / name).exists(), name)

	def test_every_asset_the_stylesheets_name_exists(self):
		pattern = re.compile(r'url\("(/assets/intech_theme/[^"]+)"\)')
		for css in (PUBLIC / "css").glob("*.css"):
			for url in pattern.findall(css.read_text(encoding="utf-8")):
				self.assertTrue(asset_path(url).exists(), f"{css.name}: {url}")


if __name__ == "__main__":
	unittest.main()
