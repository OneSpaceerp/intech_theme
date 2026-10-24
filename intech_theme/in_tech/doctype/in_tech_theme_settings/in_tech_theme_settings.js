// Copyright (c) 2026, In Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on("In Tech Theme Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Open /desk"), () => frappe.set_route("desktop"));
		frm.set_intro(
			__("Changes apply to every open session as soon as you save."),
			"blue"
		);
	},

	desk_backdrop(frm) {
		if (frm.doc.desk_backdrop !== "Image") return;
		frm.scroll_to_field("desk_background_image");
	},
});
