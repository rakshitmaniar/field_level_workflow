frappe.ui.form.on('Workflow', {
  refresh(frm) {
    toggle_tracked_fields(frm);

    if (frm.doc.enable_field_level_workflow && frm.doc.document_type && !frm.is_new()) {
      frm.add_custom_button(__('Preview Tracked Fields'), () => {
        preview_tracked_fields(frm);
      });
    }
  },

  enable_field_level_workflow(frm) {
    toggle_tracked_fields(frm);
  },

  document_type(frm) {
    if (frm.doc.tracked_fields && frm.doc.tracked_fields.length) {
      frappe.msgprint(__('Changing Document Type will reset tracked fields'));
      frm.clear_table('tracked_fields');
      frm.refresh_field('tracked_fields');
    }
  }
});

function toggle_tracked_fields(frm) {
  frm.set_df_property('tracked_fields', 'hidden', !frm.doc.enable_field_level_workflow);
}

function preview_tracked_fields(frm) {
  let html = '<ul>';
  (frm.doc.tracked_fields || []).forEach(row => {
    html += `<li>${row.field_label || row.field_name}</li>`;
  });
  html += '</ul>';

  frappe.msgprint({
    title: __('Tracked Fields'),
    message: html,
    wide: true
  });
}
