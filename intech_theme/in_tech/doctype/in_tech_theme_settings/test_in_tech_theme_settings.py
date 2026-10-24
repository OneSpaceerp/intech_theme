# Copyright (c) 2026, In Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

from intech_theme.api.apps import app_identity, brand_app_data
from intech_theme.api.boot import client_settings
from intech_theme.branding import get_settings


class TestInTechThemeSettings(IntegrationTestCase):
	def setUp(self):
		self.doc = frappe.get_single("In Tech Theme Settings")

	def tearDown(self):
		frappe.db.rollback()

	def test_rejects_a_colour_that_is_not_hex(self):
		self.doc.primary_color = "red; background:url(x)"
		self.assertRaises(frappe.ValidationError, self.doc.save)

	def test_image_backdrop_needs_an_image(self):
		self.doc.desk_backdrop = "Image"
		self.doc.desk_background_image = None
		self.assertRaises(frappe.ValidationError, self.doc.save)

	def test_dimming_is_clamped(self):
		self.doc.backdrop_dim = 400
		self.doc.save()
		self.assertEqual(self.doc.backdrop_dim, 80)

	def test_duplicate_app_rows_are_refused(self):
		self.doc.set("app_identities", [{"app": "frappe", "title": "A"}, {"app": "frappe", "title": "B"}])
		self.assertRaises(frappe.ValidationError, self.doc.save)

	def test_site_row_outranks_the_shipped_identity(self):
		self.doc.set("app_identities", [{"app": "frappe", "title": "Core"}])
		self.doc.save()
		self.assertEqual(app_identity("frappe")["title"], "Core")

	def test_every_app_on_the_apps_screen_loses_its_vendor_logo(self):
		apps = [
			{
				"app_name": "frappe",
				"app_title": "Framework",
				"app_logo_url": "/assets/frappe/images/frappe-framework-logo.svg",
			},
			{
				"app_name": "erpnext",
				"app_title": "ERPNext",
				"app_logo_url": "/assets/erpnext/images/erpnext-logo.svg",
			},
			{
				"app_name": "some_new_app",
				"app_title": "Frappe Thing",
				"app_logo_url": "/assets/some_new_app/logo.svg",
			},
		]
		brand_app_data(apps)
		for app in apps:
			self.assertNotIn("/assets/frappe/", app["app_logo_url"])
			self.assertNotIn("/assets/erpnext/", app["app_logo_url"])
			self.assertNotIn("Frappe", app["app_title"])
			self.assertNotIn("ERPNext", app["app_title"])
		self.assertTrue(apps[2]["app_logo_url"].startswith("data:image/svg+xml"))

	def test_client_settings_carry_the_palette(self):
		settings = client_settings(get_settings())
		self.assertEqual(len(settings["menu_colors"]), 8)
		self.assertTrue(settings["colors"]["primary"].startswith("#"))
		self.assertIn(settings["desk_backdrop"], ("circuit", "aurora", "mesh", "waves", "image", "none"))
