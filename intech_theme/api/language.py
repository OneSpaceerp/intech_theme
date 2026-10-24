"""The English / Arabic switcher.

Frappe decides the interface language in two ways (frappe.translate.get_language): a signed-in
user gets their own `User.language`, a signed-out visitor gets the `preferred_language` cookie.
The switcher writes whichever applies - both, for a signed-in user, so the login page that
follows a logout stays in the language they last chose.
"""

import frappe
from frappe import _

# What the switcher moves between. Anything else is refused, so the endpoint cannot be used
# to set an arbitrary value on the caller's User record.
SWITCHER_LANGUAGES = ("en", "ar")

# A year, the same horizon Frappe gives its own long-lived preference cookies.
COOKIE_DAYS = 365


@frappe.whitelist(allow_guest=True, methods=["POST"])
def switch_language(language: str) -> dict:
	"""Switch the caller's interface language between English and Arabic."""
	language = (language or "").strip().lower()
	if language not in SWITCHER_LANGUAGES:
		frappe.throw(_("Language must be one of: {0}").format(", ".join(SWITCHER_LANGUAGES)))
	if not frappe.db.exists("Language", language):
		frappe.throw(_("Language {0} is not available on this site.").format(language))

	user = frappe.session.user
	if user and user != "Guest":
		# The caller's own record, and only the language: no permission to grant beyond that.
		frappe.db.set_value("User", user, "language", language)
		# the language rides on the cached boot and session defaults
		frappe.clear_cache(user=user)

	frappe.local.cookie_manager.set_cookie(
		"preferred_language", language, max_age=COOKIE_DAYS * 24 * 60 * 60, deduplicate=True
	)
	return {"language": language}
