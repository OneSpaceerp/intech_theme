# Copyright (c) 2026, In Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from intech_theme.palette import is_hex_color


class InTechThemeSettings(Document):
	def validate(self):
		for fieldname in ("primary_color", "accent_color", "ink_color"):
			value = self.get(fieldname)
			if value and not is_hex_color(value):
				frappe.throw(
					_("{0} must be a hex colour such as #2472AE.").format(
						frappe.bold(_(self.meta.get_label(fieldname)))
					)
				)

		self.backdrop_dim = min(max(cint(self.backdrop_dim), 0), 80)

		if self.desk_backdrop == "Image" and not self.desk_background_image:
			frappe.throw(_("Attach a Background Image, or pick another background for /desk."))

		self._validate_app_identities()

	def _validate_app_identities(self):
		"""One row per app: a second row for the same app would silently lose."""
		seen = set()
		installed = set(frappe.get_installed_apps())
		for row in self.app_identities or []:
			row.app = (row.app or "").strip()
			if row.app in seen:
				frappe.throw(_("Row {0}: {1} already has a row.").format(row.idx, frappe.bold(row.app)))
			if row.app not in installed:
				frappe.msgprint(
					_("Row {0}: {1} is not installed on this site; the row will apply once it is.").format(
						row.idx, frappe.bold(row.app)
					),
					indicator="orange",
					alert=True,
				)
			seen.add(row.app)

	def on_update(self):
		if not self.flags.intech_seeding:
			from intech_theme.install import apply_branding

			apply_branding()

		# The theme rides on every user's cached boot, and the App tiles on every user's
		# cached desktop icons. Clear just those, not the whole site cache.
		frappe.cache.delete_key("bootinfo")
		frappe.cache.delete_key("desktop_icons")
		frappe.publish_realtime("intech_theme_updated", {}, room="all", after_commit=True)
