// Copyright (c) 2026, osaz and contributors
// For license information, please see license.txt

frappe.ui.form.on('Reservation', {
	refresh: function (frm) {
		if (frm.doc.status === 'Confirmed' && !frm.is_new()) {
			set_form_read_only(frm, true);
		}
		frm.add_custom_button(
			__(frm.read_only ? 'Edit' : 'Lock'),
			function () {
				set_form_read_only(frm, !frm.read_only);
			}
		);
	}
});

function set_form_read_only(frm, read_only) {
	frm.read_only = read_only;
	if (read_only) {
		frm.disable_save();
	} else {
		frm.enable_save();
	}
	Object.values(frm.fields_dict || {}).forEach(function (field) {
		field.df.read_only = read_only;
		field.refresh();
	});
}
