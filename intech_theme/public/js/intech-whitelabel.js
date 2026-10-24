// In Tech — white label, browser side.
//
// The server renames every string that passes through translation and re-tiles every app it
// can reach in the boot payload (api/boot.py). Three things are left for the browser:
//
//   1. the part of the boot payload assembled after the server hook has run (`apps_data`);
//   2. names and logos written straight into markup by the desk's own scripts;
//   3. links and menu rows that lead to the vendor's sites.

import {
	is_vendor_asset,
	is_vendor_url,
	may_have_vendor_name,
	rebrand,
	vendor_asset_app,
} from "./intech-brand-text";

const LOGO_KEYS = ["logo", "logo_url", "app_logo_url", "brand_logo"];

// Where the text pass must not reach. Editors and inputs hold what the user is typing; the
// rest hold the site's own records. A customer who really is called "Frappe Trading" has to
// stay that way on screen -- this pass is for the interface, never for data.
const PROTECTED = [
	"script",
	"style",
	"textarea",
	"input",
	"select",
	"code",
	"pre",
	"[contenteditable]",
	".ace_editor",
	".cm-editor",
	".CodeMirror",
	".ql-editor",
	".like-disabled-input",
	".control-value",
	".list-row-container",
	".result",
	".datatable",
	".grid-body",
	".timeline-content",
	".comment-content",
	".kanban-card",
	".tree-node",
	".report-wrapper",
	".print-preview",
	".awesomplete",
	".link-preview-popover",
].join(",");

const TEXT_ATTRIBUTES = ["title", "placeholder", "aria-label", "alt", "data-original-title"];

let settings = {};
let brand = "In Tech";
let callbacks = [];
let scheduled = false;

// ---------------------------------------------------------------------------
// Boot payload
// ---------------------------------------------------------------------------
// A vendor's mark becomes the tile of the app that shipped it, or the brand's own mark.
function brand_logo_for(url) {
	const app = vendor_asset_app(url);
	const identity = app && (settings.apps || {})[app];
	return (identity && identity.icon) || settings.logo;
}

function replace_vendor_logos(node, depth = 0) {
	if (!node || depth > 8 || typeof node !== "object") return;

	if (Array.isArray(node)) {
		node.forEach((item) => replace_vendor_logos(item, depth + 1));
		return;
	}

	Object.keys(node).forEach((key) => {
		let value = node[key];
		if (LOGO_KEYS.indexOf(key) !== -1) {
			// an unresolved hook value arrives as a list of paths
			if (Array.isArray(value)) value = value[0];
			if (is_vendor_asset(value)) node[key] = brand_logo_for(value);
		} else if (value && typeof value === "object") {
			replace_vendor_logos(value, depth + 1);
		}
	});
}

// `apps_data.apps` is built after the server's boot hook, from `frappe.apps.get_apps`
// called directly rather than through the whitelisted override, so it arrives untouched.
function brand_apps_list(apps) {
	const identities = settings.apps || {};
	(apps || []).forEach((app) => {
		const identity = app && identities[app.name];
		if (!identity) return;
		app.title = identity.title;
		app.logo = identity.icon;
		if (app.setup_wizard_text) app.setup_wizard_text = rebrand(app.setup_wizard_text, brand);
	});
}

export function patch_boot(boot) {
	if (!boot) return;
	if (boot.apps_data) brand_apps_list(boot.apps_data.apps);
	["apps_data", "app_data", "desktop_icons", "dock", "module_sidebars"].forEach((key) =>
		replace_vendor_logos(boot[key])
	);
	if (is_vendor_asset(boot.app_logo_url)) boot.app_logo_url = settings.logo;
}

// ---------------------------------------------------------------------------
// Help links
// ---------------------------------------------------------------------------
function own_help_links(links) {
	if (!Array.isArray(links)) return links;
	return links.filter((link) => !is_vendor_url(link && link.url));
}

// Pages register their documentation links as they load, so emptying the table once is not
// enough: it is wrapped, and every later registration is filtered on the way in.
export function guard_help_links() {
	frappe.provide("frappe.help");
	const table = frappe.help.help_links || {};
	Object.keys(table).forEach((key) => {
		table[key] = own_help_links(table[key]);
	});

	frappe.help.help_links = new Proxy(table, {
		set(target, key, value) {
			target[key] = own_help_links(value);
			return true;
		},
	});
}

// ---------------------------------------------------------------------------
// Menus
// ---------------------------------------------------------------------------
// Some menu rows carry the vendor's address inside a click handler -- the support row of the
// /desk avatar menu is one ("Frappe Support" -> support.frappe.io). There is no link in the
// page to rewrite and no setting to switch off, so the row is taken out as the menu is built.
// A row is judged by where it leads, never by its label: by now the label has been
// translated and no longer names anyone.
function leads_to_vendor(row) {
	if (!row || typeof row !== "object") return false;
	if (is_vendor_url(row.href) || is_vendor_url(row.url) || is_vendor_url(row.route)) return true;

	const handler = row.onclick || row.onClick;
	if (typeof handler !== "function") return false;
	try {
		return is_vendor_url(Function.prototype.toString.call(handler));
	} catch (error) {
		return false;
	}
}

function support_row(row) {
	return {
		label: __("Support"),
		icon: row.icon,
		onclick: () => window.open(settings.support_url, "_blank", "noopener"),
	};
}

function own_menu_rows(options) {
	if (!Array.isArray(options)) return options;

	const rows = [];
	options.forEach((row) => {
		if (row && Array.isArray(row.options)) {
			// a group, or a row with a submenu
			rows.push(Object.assign({}, row, { options: own_menu_rows(row.options) }));
		} else if (leads_to_vendor(row)) {
			// With a support address of your own, the row stays and leads there.
			if (settings.support_url) rows.push(support_row(row));
		} else {
			rows.push(row);
		}
	});
	return rows;
}

export function guard_menus() {
	const Original = frappe.ui && frappe.ui.Dropdown;
	if (typeof Original !== "function" || Original.intech_guarded) return;

	const filter_options = (options) =>
		typeof options === "function"
			? (...args) => own_menu_rows(options(...args))
			: own_menu_rows(options);

	class Dropdown extends Original {
		constructor(opts = {}) {
			if (opts && opts.options) opts.options = filter_options(opts.options);
			super(opts);
		}
	}

	if (typeof Original.prototype.set_options === "function") {
		Dropdown.prototype.set_options = function (options, ...rest) {
			return Original.prototype.set_options.call(this, filter_options(options), ...rest);
		};
	}

	Dropdown.intech_guarded = true;
	frappe.ui.Dropdown = Dropdown;
}

// ---------------------------------------------------------------------------
// Document
// ---------------------------------------------------------------------------
function is_protected(element) {
	return !element || (element.closest && element.closest(PROTECTED) !== null);
}

function scrub_text_node(node) {
	const value = node.nodeValue;
	if (!may_have_vendor_name(value)) return;
	if (is_protected(node.parentElement)) return;
	const renamed = rebrand(value, brand);
	if (renamed !== value) node.nodeValue = renamed;
}

function scrub_element(element) {
	if (element.tagName === "IMG") {
		const source = element.getAttribute("src");
		if (is_vendor_asset(source)) element.setAttribute("src", brand_logo_for(source));
	}

	if (element.tagName === "A" && settings.hide_help_links) {
		const href = element.getAttribute("href");
		if (is_vendor_url(href)) {
			if (settings.support_url) {
				element.setAttribute("href", settings.support_url);
			} else {
				// No replacement to offer: the row stays, in case it is the only thing in its
				// menu, but it no longer leaves the site.
				element.removeAttribute("href");
				element.removeAttribute("target");
				element.setAttribute("aria-disabled", "true");
				element.style.pointerEvents = "none";
				element.style.opacity = "0.55";
			}
		}
	}

	if (is_protected(element)) return;

	TEXT_ATTRIBUTES.forEach((name) => {
		const value = element.getAttribute(name);
		if (may_have_vendor_name(value)) {
			const renamed = rebrand(value, brand);
			if (renamed !== value) element.setAttribute(name, renamed);
		}
	});
}

function scrub_tree(root) {
	if (!root) return;

	if (root.nodeType === Node.TEXT_NODE) {
		scrub_text_node(root);
		return;
	}
	if (root.nodeType !== Node.ELEMENT_NODE) return;

	scrub_element(root);

	// Elements first (logos, links, tooltips), then the text between them.
	const candidates = root.querySelectorAll(
		"img, a[href], [title], [placeholder], [aria-label], [data-original-title]"
	);
	for (let index = 0; index < candidates.length; index++) scrub_element(candidates[index]);

	const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
		acceptNode(node) {
			return may_have_vendor_name(node.nodeValue)
				? NodeFilter.FILTER_ACCEPT
				: NodeFilter.FILTER_REJECT;
		},
	});
	const found = [];
	while (walker.nextNode()) found.push(walker.currentNode);
	found.forEach(scrub_text_node);
}

function scrub_title() {
	const renamed = rebrand(document.title, brand);
	if (renamed !== document.title) document.title = renamed;
}

function run_callbacks() {
	scheduled = false;
	callbacks.forEach((callback) => {
		try {
			callback();
		} catch (error) {
			// One failing hook must not stop the others, or the pass itself.
			console.error("In Tech:", error);
		}
	});
}

function schedule_callbacks() {
	if (scheduled || !callbacks.length) return;
	scheduled = true;
	window.requestAnimationFrame(run_callbacks);
}

/** Call `callback` (at most once a frame) whenever the desk's markup changes. */
export function on_dom_change(callback) {
	callbacks.push(callback);
}

function observe() {
	const scrub = Boolean(settings.scrub_text);

	const observer = new MutationObserver((mutations) => {
		if (scrub) {
			for (let index = 0; index < mutations.length; index++) {
				const mutation = mutations[index];
				if (mutation.type === "characterData") {
					scrub_text_node(mutation.target);
				} else if (mutation.type === "attributes") {
					scrub_element(mutation.target);
				} else {
					mutation.addedNodes.forEach(scrub_tree);
				}
			}
		}
		schedule_callbacks();
	});

	observer.observe(document.body, {
		childList: true,
		subtree: true,
		characterData: scrub,
		attributes: scrub,
		attributeFilter: scrub ? ["src", "href", ...TEXT_ATTRIBUTES] : undefined,
	});

	if (!scrub) return;

	scrub_tree(document.body);

	const title = document.querySelector("title");
	if (title) {
		new MutationObserver(scrub_title).observe(title, {
			childList: true,
			characterData: true,
			subtree: true,
		});
		scrub_title();
	}
}

/** Start the white-label pass. Call once, as early as the settings are known. */
export function start(theme_settings) {
	settings = theme_settings || {};
	brand = settings.brand_name || brand;

	if (settings.white_label) {
		patch_boot(window.frappe && frappe.boot);
		if (settings.hide_help_links) {
			guard_help_links();
			guard_menus();
		}
	}

	// The observer also drives `on_dom_change`, which the /desk greeting relies on, so it runs
	// whether or not the text pass is switched on.
	if (document.body) {
		observe();
	} else {
		document.addEventListener("DOMContentLoaded", observe, { once: true });
	}
}
