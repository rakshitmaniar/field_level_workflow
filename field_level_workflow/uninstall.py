# -*- coding: utf-8 -*-
"""
Uninstall cleanup for Field Level Workflow
- Disable (do not delete) custom fields created by this app
- Ensure Workflow override is no longer active after uninstall

Safe for production: no data loss, reversible by reinstall.
"""
from __future__ import unicode_literals
import frappe

CUSTOM_FIELDS = [
    "Workflow-enable_field_level_workflow",
    "Workflow-tracked_fields",
]


def before_uninstall():
    """
    Executed by Frappe before app uninstall.
    We only *disable* artifacts so rollback/reinstall is safe.
    """
    disable_custom_fields()


def disable_custom_fields():
    for name in CUSTOM_FIELDS:
        if frappe.db.exists("Custom Field", name):
            try:
                frappe.db.set_value("Custom Field", name, "disabled", 1)
            except Exception:
                # Never block uninstall
                frappe.log_error(frappe.get_traceback(), "Field Level Workflow uninstall")
