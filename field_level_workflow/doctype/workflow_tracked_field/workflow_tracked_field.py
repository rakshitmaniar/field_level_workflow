# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from frappe.model.document import Document


class WorkflowTrackedField(Document):
    """Child table DocType for tracking workflow-relevant fields."""

    def validate(self):
        # Auto-populate label and type when possible
        if self.field_name and self.parent_doctype:
            self.populate_field_metadata()

    def populate_field_metadata(self):
        try:
            meta = frappe.get_meta(self.parent_doctype)

            if not self.is_child_table_field:
                field = meta.get_field(self.field_name)
                if field:
                    self.field_label = field.label or field.fieldname
                    self.field_type = field.fieldtype
            else:
                parent_field = meta.get_field(self.child_table_name)
                if parent_field:
                    child_meta = frappe.get_meta(parent_field.options)
                    child_field = child_meta.get_field(self.child_field_name)
                    if child_field:
                        self.field_label = f"{parent_field.label} → {child_field.label}"
                        self.field_type = child_field.fieldtype
        except Exception:
            frappe.log_error(frappe.get_traceback(), "WorkflowTrackedField.populate_field_metadata")
