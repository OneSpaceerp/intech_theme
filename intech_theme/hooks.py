app_name = "intech_theme"
app_title = "In Tech"
app_publisher = "In Tech"
app_description = "In Tech brand theme and white-label layer for Frappe / ERPNext v16"
app_email = "kelshiekh@gmail.com"
app_license = "mit"

# Nothing is required beyond Frappe: the theme brands whatever apps are installed. Install it
# AFTER them, though - install order is what lets this app's translations, templates and
# stylesheets win over theirs.

# Brand
# -----
# Asked for whenever the framework wants an app's mark. Navbar Settings and Website Settings
# are also written on install (see install.py), because several screens read those and never
# consult this hook - /desk's own navbar logo is one.
app_logo_url = "/assets/intech_theme/images/intech-mark-256.png"

website_context = {
	"favicon": "/assets/intech_theme/images/favicon-64.png",
	"splash_image": "/assets/intech_theme/images/intech-logo-stacked.png",
}
update_website_context = ["intech_theme.api.website.update_website_context"]

# Desk
# ----
# Bundles, not raw /assets paths: only a ".bundle." name goes through assets.json and gets a
# content hash, so a shipped fix actually reaches browsers and nginx caches.
app_include_css = ["intech_theme.bundle.css"]
app_include_js = ["intech_theme.bundle.js"]

# Website, portal and login
# -------------------------
web_include_css = ["intech_theme_web.bundle.css"]
web_include_js = ["intech_theme_web.bundle.js"]

# Emails
# ------
# The framework prints every app's `default_mail_footer`, so the vendor's "Sent via" line
# cannot be removed from here; templates/emails/email_footer.html replaces the template that
# prints them, and shows this line (or the Email Footer from settings) instead.
default_mail_footer = """<span>In Tech</span>"""

# Jinja
# -----
jinja = {
	"methods": [
		"intech_theme.jinja.intech_settings",
		"intech_theme.jinja.intech_brand_name",
	],
}

# Boot and requests
# -----------------
extend_bootinfo = ["intech_theme.api.boot.extend_bootinfo"]
after_request = ["intech_theme.api.website.after_request"]

# Each override calls the original and edits what comes back, so a framework release that
# changes the original's behaviour is picked up without a change here.
override_whitelisted_methods = {
	"frappe.apps.get_apps": "intech_theme.api.apps.get_apps",
	"frappe.utils.change_log.get_versions": "intech_theme.api.apps.get_versions",
}

# Install
# -------
after_install = "intech_theme.install.after_install"
after_migrate = ["intech_theme.install.after_migrate"]
before_uninstall = "intech_theme.install.before_uninstall"

# API methods must declare their argument and return types.
require_type_annotated_api_methods = True
