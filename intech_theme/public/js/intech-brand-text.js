// Vendor-name replacement for text built in the browser.
//
// This mirrors intech_theme/utils/text.py rule for rule. The server renames everything that
// passes through translation; this is for the strings that never do.

// A vendor name counts only as a standalone word of prose. The guards keep identifiers,
// paths, emails and domains intact, and test ASCII neighbours only, so a name running
// straight into Chinese or Japanese text is still found.
const BEFORE = "(?<![A-Za-z0-9_/.@#])";
const AFTER = "(?![A-Za-z0-9_@]|[./][A-Za-z0-9_])";

const PUBLISHER = new RegExp(
	BEFORE +
		"Frappe Technologies(?:,? Pvt\\.? Ltd\\.?)?(?:,? and [Cc]ontributors)?" +
		"(?![A-Za-z0-9_@])",
	"g"
);

// Longest names first: "Frappe Framework" has to go before the bare "Frappe" does.
const PRODUCTS = new RegExp(
	BEFORE +
		"(?:Frappe Framework|Frappe Cloud|Frappe Mail|Frappe School|Frappe Support|ERPNext|Frappe)" +
		AFTER,
	"g"
);

const SUFFIXED = {
	"Frappe Cloud": " Cloud",
	"Frappe Mail": " Mail",
	"Frappe School": " Academy",
	"Frappe Support": " Support",
};

const VENDOR_HOSTS = [
	"frappe.io",
	"frappeframework.com",
	"frappecloud.com",
	"frappe.cloud",
	"frappe.school",
	"erpnext.com",
	"erpnext.org",
	"github.com/frappe",
];

// Mirrors `VENDOR_APPS` in branding.py.
const VENDOR_ASSET = /^\/assets\/(frappe|erpnext|hrms|crm|helpdesk|lms|insights|payments)\/.*(?:logo|favicon|wordmark|splash)[^/]*$/i;

function escape_regex(value) {
	return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Cheap test: true if `text` might hold a vendor name. */
export function may_have_vendor_name(text) {
	return (
		typeof text === "string" &&
		text.length > 5 &&
		(text.indexOf("Frappe") !== -1 || text.indexOf("ERPNext") !== -1)
	);
}

/** Return `text` with every vendor product name replaced by `brand`. Idempotent. */
export function rebrand(text, brand) {
	if (!may_have_vendor_name(text) || !brand) return text;

	let out = text
		.replace(PUBLISHER, brand)
		.replace(PRODUCTS, (match) => brand + (SUFFIXED[match] || ""));

	if (out === text) return text;

	const doubled = escape_regex(brand);
	// "Frappe ERPNext" would otherwise read "In Tech In Tech".
	out = out.replace(new RegExp(`${doubled}(?:\\s+${doubled})+`, "g"), brand);

	// "A Frappe instance" must not become "A In Tech instance".
	if ("aeiou".indexOf(brand[0].toLowerCase()) !== -1) {
		out = out.replace(new RegExp(`\\b([Aa])(?= ${doubled})`, "g"), "$1n");
	}
	return out;
}

/** True if `url` points at one of the vendor's own sites. */
export function is_vendor_url(url) {
	if (typeof url !== "string" || !url) return false;
	const lowered = url.toLowerCase();
	return VENDOR_HOSTS.some((host) => lowered.indexOf(host) !== -1);
}

/** The vendor app that ships `url` as its logo, wordmark or favicon, or `null`. */
export function vendor_asset_app(url) {
	if (typeof url !== "string" || !url) return null;
	// tolerate an absolute URL to this same site, and a cache-busting query string
	const path = url.replace(/^https?:\/\/[^/]+/i, "").split("?")[0];
	const match = VENDOR_ASSET.exec(path);
	return match ? match[1].toLowerCase() : null;
}

/** True for the logo, wordmark and favicon files the vendor apps ship. */
export function is_vendor_asset(url) {
	return vendor_asset_app(url) !== null;
}
