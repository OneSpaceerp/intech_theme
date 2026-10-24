/* In Tech — desk scripts, bundled.
   =========================================================================
   Parsed after the framework's bundles and before the desk starts (the desk
   starts on DOM ready, and scripts at the end of <body> run before that), so
   everything in `prepare` is in place by the time the first screen is drawn
   and nothing is seen to change.

   Bundled for cache busting: a raw /assets path carries no content hash, so
   browsers and nginx kept serving the previous release's scripts.
   ========================================================================= */

import * as about from "./intech-about";
import * as desktop from "./intech-desktop";
import * as whitelabel from "./intech-whitelabel";
import { apply_browser_chrome, apply_mode, apply_theme } from "./intech-boot";

function read_settings() {
	return (window.frappe && frappe.boot && frappe.boot.intech) || null;
}

function prepare(settings) {
	apply_theme(settings);
	apply_mode(settings);
	apply_browser_chrome(settings);
	whitelabel.start(settings);
	if (settings.white_label) about.install(settings);
}

// Saving In Tech Theme Settings repaints every open desk without a reload.
function listen_for_changes() {
	if (!frappe.realtime || !frappe.realtime.on) return;
	frappe.realtime.on("intech_theme_updated", () => {
		frappe
			.xcall("intech_theme.api.boot.get_client_settings")
			.then((fresh) => {
				if (!fresh) return;
				frappe.boot.intech = fresh;
				frappe.intech.settings = fresh;
				apply_theme(fresh);
				apply_browser_chrome(fresh);
				desktop.refresh(fresh);
			})
			.catch(() => {
				// the next page load picks the change up anyway
			});
	});
}

const settings = read_settings();

if (settings) {
	frappe.provide("frappe.intech");
	frappe.intech.settings = settings;
	frappe.intech.show_about = () => about.show_about(frappe.intech.settings);

	try {
		prepare(settings);
	} catch (error) {
		// A theme must never stop the desk from loading.
		console.error("In Tech: theme setup failed", error);
	}

	$(document).on("app_ready", () => {
		try {
			desktop.start(settings, whitelabel.on_dom_change);
			listen_for_changes();
		} catch (error) {
			console.error("In Tech: desk additions failed to start", error);
		}
	});
}
