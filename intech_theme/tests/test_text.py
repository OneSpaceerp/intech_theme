"""Tests for the vendor-name replacement. They need no bench:

python -m unittest intech_theme.tests.test_text   (from the repository root, with
intech_theme/utils importable), or simply  python intech_theme/tests/test_text.py
"""

import importlib.util
import unittest
from pathlib import Path

# Load by path so the tests run without `frappe` installed.
_path = Path(__file__).resolve().parent.parent / "utils" / "text.py"
_spec = importlib.util.spec_from_file_location("it_text", _path)
text = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(text)

rebrand = text.rebrand


class TestRebrand(unittest.TestCase):
	def test_product_names(self):
		self.assertEqual(rebrand("ERPNext"), "In Tech")
		self.assertEqual(rebrand("Frappe"), "In Tech")
		self.assertEqual(rebrand("Frappe Framework"), "In Tech")
		self.assertEqual(rebrand("Welcome to Frappe!"), "Welcome to In Tech!")
		self.assertEqual(rebrand("ERPNext Settings"), "In Tech Settings")
		self.assertEqual(rebrand("Sent via ERPNext."), "Sent via In Tech.")

	def test_suffixed_products(self):
		self.assertEqual(rebrand("Update from Frappe Cloud"), "Update from In Tech Cloud")
		self.assertEqual(rebrand("Frappe Support"), "In Tech Support")
		self.assertEqual(rebrand("Frappe School"), "In Tech Academy")

	def test_publisher(self):
		self.assertEqual(rebrand("&copy; Frappe Technologies Pvt. Ltd. and contributors"), "&copy; In Tech")
		self.assertEqual(rebrand("Frappe Technologies"), "In Tech")

	def test_no_doubled_brand(self):
		self.assertEqual(rebrand("Frappe ERPNext"), "In Tech")

	def test_article_agrees_with_brand(self):
		self.assertEqual(rebrand("A Frappe Framework instance"), "An In Tech instance")
		self.assertEqual(rebrand("install a Frappe app"), "install an In Tech app")
		# only the article directly in front of the brand changes
		self.assertEqual(rebrand("A site on ERPNext"), "A site on In Tech")
		self.assertEqual(rebrand("Data Frappe"), "Data In Tech")

	def test_identifiers_paths_and_addresses_are_left_alone(self):
		for untouched in (
			"ERPNextTestSuite",
			"/assets/frappe/images/frappe-logo.svg",
			"/assets/erpnext/images/erpnext-logo.svg",
			"frappe.call('frappe.client.get')",
			"hello@Frappe.io",
			"https://Frappe.io/pricing",
			"import frappe",
			"erpnext.accounts.utils",
			"docs.ERPNext.com",
			"#Frappe",
		):
			self.assertEqual(rebrand(untouched), untouched, untouched)

	def test_text_without_vendor_names_is_returned_as_is(self):
		for value in ("", None, "Sales Invoice", "A frappé, please"):
			self.assertEqual(rebrand(value), value)

	def test_non_strings_pass_through(self):
		self.assertEqual(rebrand(42), 42)
		self.assertEqual(rebrand(["ERPNext"]), ["ERPNext"])

	def test_idempotent(self):
		once = rebrand("ERPNext is built on Frappe Framework by Frappe Technologies.")
		self.assertEqual(once, "In Tech is built on In Tech by In Tech.")
		self.assertEqual(rebrand(once), once)

	def test_custom_brand(self):
		self.assertEqual(rebrand("ERPNext Settings", "إن تك"), "إن تك Settings")
		self.assertEqual(rebrand("A Frappe app", "Zed"), "A Zed app")

	def test_empty_brand_strips_names(self):
		self.assertEqual(rebrand("ERPNext", ""), "")

	def test_names_touching_cjk_text(self):
		self.assertEqual(rebrand("ERPNext設定"), "In Tech設定")
		self.assertEqual(rebrand("請求登入Frappe雲失敗"), "請求登入In Tech雲失敗")

	def test_loose_mode_allows_grammatical_suffixes(self):
		self.assertEqual(rebrand("az ERPNextet", loose=True), "az In Techet")
		self.assertEqual(rebrand("Frappega xush kelibsiz!", loose=True), "In Techga xush kelibsiz!")
		# strict mode, the default, leaves an attached suffix alone
		self.assertEqual(rebrand("az ERPNextet"), "az ERPNextet")


class TestDetection(unittest.TestCase):
	def test_has_vendor_name(self):
		self.assertTrue(text.has_vendor_name("Powered by ERPNext"))
		self.assertTrue(text.has_vendor_name("Frappe Technologies"))
		self.assertFalse(text.has_vendor_name("frappe.call()"))
		self.assertFalse(text.has_vendor_name("Sales Order"))
		self.assertFalse(text.has_vendor_name(None))

	def test_is_vendor_url(self):
		self.assertTrue(text.is_vendor_url("https://frappe.io/support"))
		self.assertTrue(text.is_vendor_url("https://docs.erpnext.com/docs/user/manual"))
		self.assertTrue(text.is_vendor_url("https://github.com/frappe/erpnext/issues"))
		self.assertFalse(text.is_vendor_url("/desk/system-health-report"))
		self.assertFalse(text.is_vendor_url("https://almandoos.example/help"))
		self.assertFalse(text.is_vendor_url(None))

	def test_replace_vendor_urls(self):
		self.assertEqual(
			text.replace_vendor_urls("See https://docs.erpnext.com/docs/x for details", "our help"),
			"See our help for details",
		)
		self.assertEqual(text.replace_vendor_urls("No links here"), "No links here")


if __name__ == "__main__":
	unittest.main()
