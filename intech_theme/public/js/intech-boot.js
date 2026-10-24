// In Tech — theme attributes, colours and fonts.
//
// Runs first in both bundles, synchronously. On the desk it reads `frappe.boot.intech`; on the
// website and login page the server has already written the attributes onto <html> and the
// administrator's colours into an inline style (api/website.py), so there is nothing to wait
// for. Either way the stylesheets key off what is set here.

const GOOGLE_FONTS = {
	Poppins: "Poppins:wght@400;500;600;700",
	Manrope: "Manrope:wght@400;500;600;700",
	"IBM Plex Sans": "IBM+Plex+Sans:wght@400;500;600;700",
	Cairo: "Cairo:wght@400;500;600;700",
};

const HEX = /^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i;

function set_var(root, name, value) {
	if (typeof value === "string" && HEX.test(value)) root.style.setProperty(name, value);
}

function load_font(family) {
	const spec = GOOGLE_FONTS[family];
	if (!spec || document.getElementById("intech-font")) return;
	const link = document.createElement("link");
	link.id = "intech-font";
	link.rel = "stylesheet";
	link.href = `https://fonts.googleapis.com/css2?family=${spec}&display=swap`;
	document.head.appendChild(link);
}

/** Write the theme onto <html>. Safe to call again with new settings. */
export function apply_theme(settings, root = document.documentElement) {
	if (!settings) return;

	root.setAttribute("data-intech", "1");
	root.setAttribute("data-intech-sidebar", settings.sidebar_style || "navy");
	root.setAttribute("data-intech-backdrop", settings.desk_backdrop || "circuit");
	root.setAttribute("data-intech-menus", settings.colorful_menus ? "colorful" : "plain");
	root.setAttribute("data-intech-glass", settings.glass_tiles ? "1" : "0");
	root.setAttribute("data-intech-font", settings.font_family || "Inter");
	root.setAttribute("data-intech-hide-promotions", settings.hide_promotions ? "1" : "0");
	root.setAttribute("data-intech-workspace-backdrop", settings.backdrop_on_workspaces ? "1" : "0");

	const colors = settings.colors || {};
	set_var(root, "--it-primary", colors.primary);
	set_var(root, "--it-accent", colors.accent);
	set_var(root, "--it-ink", colors.ink);

	(settings.menu_colors || []).forEach((color, index) => set_var(root, `--it-m${index + 1}`, color));

	root.style.setProperty("--it-dim", String(Number(settings.backdrop_dim) || 0));
	if (settings.desk_background_image) {
		const url = String(settings.desk_background_image).replace(/["'()\\\s<>]/g, "");
		root.style.setProperty("--it-desk-image", `url("${url}")`);
	} else {
		root.style.removeProperty("--it-desk-image");
	}

	load_font(settings.font_family);
}

/** The browser chrome: tab icon, and the mobile address bar's colour. */
export function apply_browser_chrome(settings) {
	const head = document.head;
	if (!head || !settings) return;

	if (settings.favicon) {
		head.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]').forEach((link) =>
			link.setAttribute("href", settings.favicon)
		);
	}

	let meta = head.querySelector('meta[name="theme-color"]');
	if (!meta) {
		meta = document.createElement("meta");
		meta.setAttribute("name", "theme-color");
		head.appendChild(meta);
	}
	meta.setAttribute("content", (settings.colors && settings.colors.ink) || "#1E2448");
}

/** Force dark, when the site asks for it. The desk reads the mode from here when it starts. */
export function apply_mode(settings, root = document.documentElement) {
	if (!settings || !settings.force_dark) return;
	root.setAttribute("data-theme-mode", "dark");
	root.setAttribute("data-theme", "dark");
}
