// In Tech — the English / Arabic switcher.
//
// One button, drawn in three places: the /desk header, the foot of the sidebar, and the login
// page. It always names the language it switches *to*, in that language ("العربية" while the
// interface is English, "English" while it is Arabic), which is what someone who cannot read
// the current one is looking for.
//
// The switch itself is api/language.py: the signed-in user's own language, or the
// preferred_language cookie for a visitor. The page then reloads, because Frappe translates at
// boot and switches the page direction (rtl / ltr) with the language.

const TARGET = {
	en: { code: "ar", label: "العربية", short: "ع" },
	ar: { code: "en", label: "English", short: "EN" },
};

const METHOD = "/api/method/intech_theme.api.language.switch_language";

const GLOBE =
	'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" ' +
	'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
	'<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>' +
	'<path d="M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9s1.3-6.4 3.9-9Z"/></svg>';

function target_for(language) {
	return TARGET[(language || "en").split("-")[0]] || TARGET.en;
}

function csrf_token() {
	return (window.frappe && frappe.csrf_token) || window.csrf_token || "";
}

/** Switch to `code` and reload. Uses the desk's own request helper when there is one. */
export function switch_to(code) {
	const done = () => window.location.reload();

	if (window.frappe && frappe.xcall && frappe.boot && frappe.boot.intech) {
		return frappe
			.xcall("intech_theme.api.language.switch_language", { language: code })
			.then(done);
	}

	const body = new URLSearchParams({ language: code });
	return fetch(METHOD, {
		method: "POST",
		credentials: "same-origin",
		headers: {
			Accept: "application/json",
			"Content-Type": "application/x-www-form-urlencoded",
			"X-Frappe-CSRF-Token": csrf_token(),
		},
		body,
	}).then((response) => {
		if (!response.ok) throw new Error(`language switch failed: ${response.status}`);
		done();
	});
}

/**
 * The button, as an element. `variant` is "header" (a pill), "sidebar" (a full-width row that
 * folds to its globe when the sidebar is collapsed) or "floating" (the login page's corner).
 */
export function make_button(language, variant = "header") {
	const target = target_for(language);
	const button = document.createElement("button");
	button.type = "button";
	button.className = `intech-lang-switch intech-lang-switch--${variant}`;
	button.setAttribute("lang", target.code);
	button.setAttribute("dir", target.code === "ar" ? "rtl" : "ltr");
	button.setAttribute("title", target.label);
	button.setAttribute("aria-label", target.label);

	const icon = document.createElement("span");
	icon.className = "intech-lang-switch__icon";
	icon.innerHTML = GLOBE; // a constant, never data

	const label = document.createElement("span");
	label.className = "intech-lang-switch__label";
	label.textContent = target.label;

	const short = document.createElement("span");
	short.className = "intech-lang-switch__short";
	short.textContent = target.short;

	button.append(icon, label, short);
	button.addEventListener("click", () => {
		button.disabled = true;
		button.classList.add("is-busy");
		switch_to(target.code).catch((error) => {
			button.disabled = false;
			button.classList.remove("is-busy");
			console.error("In Tech:", error);
		});
	});
	return button;
}
