# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.workflow.doctype.workflow.workflow import Workflow
from field_level_workflow.utils.workflow_field_validator import build_change_summary


class CustomWorkflow(Workflow):
    """
    Initial extension of core Workflow DocType.
    NOTE: This override is intentionally minimal and will be hardened
    after validating Frappe v15 workflow internals.
    """

    def validate(self):
        super().validate()

        if self.enable_field_level_workflow:
            self._validate_tracked_fields()

    def get_notification_message(self, doc):
        """Extend workflow notification with changed-field context."""
        message = super().get_notification_message(doc)

        summary = getattr(doc.flags, "workflow_change_summary", None)
        if not summary:
            return message

        lines = ["<br><b>Changed Fields:</b><ul>"]
        for item in summary:
            lines.append(
                f"<li><b>{item['label']}</b>: {item['old']} → {item['new']}</li>"
            )
        lines.append("</ul>")

        return message + "".join(lines)

    def _validate_tracked_fields(self):
        if not self.tracked_fields:
            frappe.throw(_("Enable Field Level Workflow requires at least one tracked field"))

        # cache meta per request
        meta_cache = frappe.local.setdefault("flw_meta", {})
        meta = meta_cache.setdefault(self.document_type, frappe.get_meta(self.document_type))

        for row in self.tracked_fields:
            if not row.is_child_table_field:
                if not meta.has_field(row.field_name):
                    frappe.throw(_("Field {0} not found in {1}").format(
                        frappe.bold(row.field_name), frappe.bold(self.document_type)
                    ))
            else:
                parent_field = meta.get_field(row.child_table_name)
                if not parent_field:
                    frappe.throw(_("Child table {0} not found").format(row.child_table_name))

                child_meta = meta_cache.setdefault(
                    parent_field.options, frappe.get_meta(parent_field.options)
                )
                if not child_meta.has_field(row.child_field_name):
                    frappe.throw(_("Field {0} not found in child table {1}").format(
                        row.child_field_name, parent_field.options
                    ))
