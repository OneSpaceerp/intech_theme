// In Tech — the /desk page.
//
// Frappe's `desktop` page re-renders itself every time it is shown (DesktopPage.make empties
// the page body), and announces each render with a `desktop_screen` event. Everything here
// hangs off that event, so it is drawn again with the page rather than lost with it.
//
// What it adds:
//   * `intech-on-desktop` on <body> while /desk is showing -- Frappe's own `desktop-page`
//     class is set once at start-up and never removed, so the stylesheet cannot use it;
//   * the wordmark beside the logo in the header, with the product name under it;
//   * a greeting above the app tiles, under the product name;
//   * In Tech captions on the App tiles of the Desktop Icons grid, whose labels the server
//     must leave alone (a saved layout finds its icons by label);
//   * the English / Arabic switcher, in the header here and at the foot of the sidebar on
//     every other page.

import { make_button } from "./intech-language";

let settings = {};

function escape(value) {
	return frappe.utils.escape_html(value === null || value === undefined ? "" : String(value));
}

function on_desktop() {
	const route = (frappe.get_route && frappe.get_route()) || [];
	// the same test desktop.js uses to decide whether to hide the navbar
	return route[0] === "desktop" || route[0] === "" || route.length === 0;
}

function sync_route_class() {
	document.body.classList.toggle("intech-on-desktop", on_desktop());
}

function greeting_for(hour) {
	if (hour < 5) return __("Good evening");
	if (hour < 12) return __("Good morning");
	if (hour < 17) return __("Good afternoon");
	return __("Good evening");
}

function first_name() {
	const full = settings.full_name || frappe.session.user_fullname || "";
	return full.split(" ")[0] || full;
}

function render_hero($page) {
	const $container = $page.find(".desktop-container").first();
	if (!$container.length || $container.find(".intech-desk-hero").length) return;

	const name = first_name();
	const today = frappe.datetime.str_to_user
		? frappe.datetime.str_to_user(frappe.datetime.get_today())
		: "";

	$container.prepend(`
		<section class="intech-desk-hero" aria-label="${escape(__("Welcome"))}">
			${settings.product_name ? `<span class="intech-hero-eyebrow">${escape(settings.product_name)}</span>` : ""}
			<h1>${escape(greeting_for(new Date().getHours()))}${
		name ? `, <span class="intech-hero-name">${escape(name)}</span>` : ""
	}</h1>
			<p>${escape(settings.tagline || "")}${settings.tagline && today ? " · " : ""}${escape(today)}</p>
		</section>
	`);
}

function render_wordmark($page) {
	const $home = $page.find(".desktop-navbar .navbar-home").first();
	if (!$home.length || $home.find(".intech-brand-lockup").length) return;

	const dark = document.documentElement.getAttribute("data-theme") === "dark";
	const over_photo = settings.desk_backdrop === "image";
	const src = dark || over_photo ? settings.wordmark_light : settings.wordmark;
	if (!src) return;
	$home.append(`
		<span class="intech-brand-lockup">
			<img class="intech-wordmark" src="${escape(src)}" alt="${escape(settings.brand_name)}">
			${settings.product_name ? `<span class="intech-product-name">${escape(settings.product_name)}</span>` : ""}
		</span>
	`);
}

// label as the grid shows it -> the In Tech title
function app_captions() {
	const captions = {};
	(frappe.boot.desktop_icons || []).forEach((icon) => {
		if (icon.icon_type === "App" && icon.intech_title && icon.label) {
			captions[__(icon.label)] = icon.intech_title;
		}
	});
	return captions;
}

function rename_app_tiles($page) {
	const captions = app_captions();
	if (!Object.keys(captions).length) return;

	$page.find(".desktop-icon .icon-title, .desktop-icon .icon-caption > a").each(function () {
		const current = (this.textContent || "").trim();
		const renamed = captions[current];
		if (renamed && renamed !== current) {
			this.textContent = renamed;
			if (this.hasAttribute("data-original-title")) this.setAttribute("data-original-title", renamed);
		}
	});
}

function current_language() {
	return (frappe.boot && frappe.boot.lang) || settings.language || "en";
}

function render_header_switch($page) {
	const $navbar = $page.find(".desktop-navbar").first();
	if (!$navbar.length || $navbar.find(".intech-lang-switch").length) return;
	const button = make_button(current_language(), "header");
	const $bell = $navbar.find(".desktop-notifications").first();
	if ($bell.length) $bell.before(button);
	else $navbar.append(button);
}

// The sidebar is drawn once and then re-filled as you move around, so this is checked on
// every change and put back if it went.
function ensure_sidebar_switch() {
	const bottom = document.querySelector(".body-sidebar .body-sidebar-bottom");
	if (!bottom || bottom.querySelector(".intech-lang-switch")) return;
	bottom.insertBefore(make_button(current_language(), "sidebar"), bottom.firstChild);
}

function decorate() {
	sync_route_class();
	if (settings.show_language_switcher) ensure_sidebar_switch();
	if (!on_desktop()) return;

	const $page = $("#page-desktop, .page-container[data-page-route='desktop']").first();
	if (!$page.length) return;

	if (settings.show_desk_greeting) render_hero($page);
	if (settings.white_label) render_wordmark($page);
	if (settings.replace_app_icons) rename_app_tiles($page);
	if (settings.show_language_switcher) render_header_switch($page);
}

/** Wire the /desk additions. `on_dom_change` is the white-label pass's frame-throttled hook. */
export function start(theme_settings, on_dom_change) {
	settings = theme_settings || {};

	$(document).on("desktop_screen", () => window.requestAnimationFrame(decorate));
	$(document).on("page-change", sync_route_class);
	if (frappe.router && frappe.router.on) frappe.router.on("change", sync_route_class);

	// The Desktop Icons grid loads its bundle lazily and draws after the event has fired.
	if (typeof on_dom_change === "function") on_dom_change(decorate);

	sync_route_class();
	decorate();
}

/** Called after In Tech Theme Settings is saved, with the settings fetched again. */
export function refresh(theme_settings) {
	settings = theme_settings || settings;
	$(".intech-desk-hero, .intech-brand-lockup, .intech-lang-switch").remove();
	decorate();
}
