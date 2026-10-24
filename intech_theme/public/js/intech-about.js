// In Tech — the About dialog.
//
// The framework's own shows the vendor's wordmark, links to its website, repository and forum,
// and a copyright line. None of that can be renamed into something true, so the dialog is
// replaced rather than edited.

function escape(value) {
	return frappe.utils.escape_html(value === null || value === undefined ? "" : String(value));
}

function component_rows(versions) {
	return Object.keys(versions)
		.map((app) => {
			const details = versions[app] || {};
			return `<tr>
				<td class="text-ink-gray-7">${escape(__(details.title || app))}</td>
				<td class="text-right text-ink-gray-5">${escape(details.version)}</td>
			</tr>`;
		})
		.join("");
}

export function show_about(settings) {
	const versions = frappe.boot.versions || {};
	const version = (versions.erpnext || versions.frappe || {}).version || settings.version;

	const dialog = new frappe.ui.Dialog({ title: __("About") });
	dialog.$wrapper.addClass("intech-about-dialog");

	const support = settings.support_url
		? `<a class="es-button intech-about-support" data-variant="outline" target="_blank" rel="noopener"
				href="${escape(settings.support_url)}">${__("Get Support")}</a>`
		: "";

	dialog.$body.html(`
		<div class="intech-about">
			<img class="intech-about-logo" src="${escape(settings.tile || settings.logo)}" alt="">
			<h3 class="intech-about-name">${escape(settings.brand_name)}</h3>
			${settings.tagline ? `<p class="intech-about-tagline">${escape(settings.tagline)}</p>` : ""}
			<span class="intech-about-version">${__("Version {0}", [escape(version)])}</span>
			${support}
			<div class="intech-about-components w-100 mt-4 hidden">
				<table class="table table-sm mb-0"><tbody></tbody></table>
			</div>
			<div class="intech-about-copyright">${escape(settings.copyright)}</div>
		</div>
	`);

	// Component versions are for the people who maintain the site. The call goes through the
	// whitelisted override, so the titles arrive already renamed.
	if (frappe.user.has_role("System Manager")) {
		frappe
			.xcall("frappe.utils.change_log.get_versions")
			.then((details) => {
				if (!details) return;
				dialog.$body.find(".intech-about-components tbody").html(component_rows(details));
				dialog.$body.find(".intech-about-components").removeClass("hidden");
			})
			.catch(() => {
				// the dialog is complete without the table
			});
	}

	dialog.show();
	return dialog;
}

/** Point every path that opens the framework's About dialog at this one. */
export function install(settings) {
	frappe.provide("frappe.ui.misc");
	frappe.provide("frappe.ui.toolbar");

	const open = () => {
		show_about(settings);
		return false;
	};

	frappe.ui.misc.about = open;
	frappe.ui.toolbar.show_about = open;
}
