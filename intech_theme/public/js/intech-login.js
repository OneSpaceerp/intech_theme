// In Tech — the login page.
//
// Frappe's own login page is kept: its form, its providers, LDAP, the email link and the
// sign-up flow all keep working because nothing about them is replaced. The theme adds a brand
// panel beside the form and the wordmark above it. The copy comes from the inline payload the
// server writes into every web page (api/website.py), so a signed-out visitor makes no request.

function payload() {
	const element = document.getElementById("intech-web");
	if (!element) return null;
	try {
		return JSON.parse(element.textContent || "{}");
	} catch (error) {
		return null;
	}
}

function is_login_page() {
	return Boolean(document.querySelector("section.for-login, .for-login"));
}

function element(tag, class_name, props = {}) {
	const node = document.createElement(tag);
	node.className = class_name;
	Object.keys(props).forEach((key) => {
		if (key === "text") node.textContent = props[key] || "";
		else node.setAttribute(key, props[key] || "");
	});
	return node;
}

// Built from nodes, not markup: every value is set as text or as an attribute, never parsed.
function brand_panel(data) {
	const panel = element("aside", "intech-login-panel", { "aria-hidden": "true" });
	const inner = element("div", "intech-login-panel-inner");
	inner.append(
		element("img", "intech-login-panel-mark", { src: data.tile, alt: "" }),
		element("img", "intech-login-panel-wordmark", { src: data.wordmark_light, alt: "" }),
		element("h2", "", { text: data.login_headline }),
		element("p", "", { text: data.login_subline }),
		element("span", "intech-login-panel-foot", { text: data.copyright })
	);
	panel.appendChild(inner);
	return panel;
}

export function start() {
	if (!is_login_page()) return;
	const data = payload();
	if (!data) return;

	document.body.classList.add("intech-login");
	if (data.has_login_image) document.body.classList.add("intech-login-has-image");

	if (!document.querySelector(".intech-login-panel")) {
		document.body.appendChild(brand_panel(data));
	}

	document.querySelectorAll(".page-card-head .app-logo").forEach((logo) => {
		logo.setAttribute("alt", data.brand_name || "");
	});
}
