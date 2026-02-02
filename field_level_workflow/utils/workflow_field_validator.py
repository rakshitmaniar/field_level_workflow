# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from frappe import _


def validate_workflow_fields(doc, method=None):
    """
    Pre-save validator aligned with Frappe v15 workflow execution.
    """
    if doc.is_new():
        doc.flags.tracked_fields_changed = True
        return

    if doc.flags.get("in_cancel") or doc.flags.get("in_amend"):
        doc.flags.tracked_fields_changed = True
        return

    workflow = get_active_workflow(doc.doctype)
    if not workflow or not workflow.enable_field_level_workflow:
        doc.flags.tracked_fields_changed = True
        return

    doc.flags.tracked_fields_changed = tracked_fields_changed(doc, workflow)


def check_field_changes(doc, workflow_action=None):
    """
    before_workflow_action hook.
    Skips workflow when no tracked field changes are detected
    and logs changes when workflow executes.
    """
    workflow = get_active_workflow(doc.doctype)
    if not workflow or not workflow.enable_field_level_workflow:
        return

    if doc.flags.get("tracked_fields_changed") is False:
        doc.flags.skip_workflow = True
        frappe.msgprint(
            _("Workflow action skipped: no tracked field changes detected"),
            indicator="orange",
            alert=True,
        )
        return

    # Workflow will execute → log changes
    log_field_changes(doc, workflow, workflow_action)

    # Attach changed-field summary for downstream notifications
    doc.flags.workflow_change_summary = build_change_summary(doc, workflow)


def tracked_fields_changed(doc, workflow):
    before = doc.get_doc_before_save()
    if not before:
        return True

    for row in workflow.tracked_fields:
        if not row.is_child_table_field:
            if doc.has_value_changed(row.field_name):
                return True
        else:
            if child_table_changed(doc, before, row.child_table_name, row.child_field_name):
                return True

    return False


def child_table_changed(doc, before, table_field, fieldname):
    curr = doc.get(table_field) or []
    prev = before.get(table_field) or []

    # performance guard: skip deep compare for very large tables
    max_rows = frappe.local.conf.get("flw_child_table_limit", 200)
    if len(curr) > max_rows or len(prev) > max_rows:
        return True

    if len(curr) != len(prev):
        return True

    for idx, row in enumerate(curr):
        if row.get(fieldname) != prev[idx].get(fieldname):
            return True

    return False


_WORKFLOW_CACHE_KEY = "flw_active_workflow"

def get_active_workflow(doctype):
    """
    Cached lookup of active workflow per request.
    Avoids repeated DB and get_doc calls during validate/workflow execution.
    """
    cache = frappe.local.setdefault(_WORKFLOW_CACHE_KEY, {})
    if doctype in cache:
        return cache[doctype]

    name = frappe.db.get_value("Workflow", {"document_type": doctype, "is_active": 1})
    if not name:
        cache[doctype] = None
        return None

    wf = frappe.get_doc("Workflow", name)
    cache[doctype] = wf
    return wf


# ---------------- Change Summary & Audit Logging ----------------


def build_change_summary(doc, workflow):
    """Return human-readable summary of tracked field changes."""
    before = doc.get_doc_before_save()
    if not before:
        return []

    summary = []

    # cache meta per request
    meta_cache = frappe.local.setdefault("flw_meta", {})
    meta = meta_cache.setdefault(doc.doctype, frappe.get_meta(doc.doctype))

    for row in workflow.tracked_fields:
        if not row.is_child_table_field:
            if doc.has_value_changed(row.field_name):
                field = meta.get_field(row.field_name)
                label = field.label if field else row.field_name
                summary.append({
                    "field": row.field_name,
                    "label": label,
                    "old": before.get(row.field_name),
                    "new": doc.get(row.field_name),
                })
        else:
            _append_child_changes(summary, doc, before, row)

    return summary


def _append_child_changes(summary, doc, before, row):
    curr = doc.get(row.child_table_name) or []
    prev = before.get(row.child_table_name) or []
    max_len = max(len(curr), len(prev))

    for idx in range(max_len):
        old = prev[idx].get(row.child_field_name) if idx < len(prev) else None
        new = curr[idx].get(row.child_field_name) if idx < len(curr) else None
        if old != new:
            summary.append({
                "field": f"{row.child_table_name}.{row.child_field_name}",
                "label": f"{row.child_table_name}.{row.child_field_name}",
                "old": old,
                "new": new,
            })

# ---------------- Audit Logging ----------------

def log_field_changes(doc, workflow, workflow_action):
    """Persist audit logs for each tracked field change."""
    before = doc.get_doc_before_save()
    if not before:
        return

    for row in workflow.tracked_fields:
        if not row.is_child_table_field:
            if doc.has_value_changed(row.field_name):
                _insert_log(
                    doc,
                    workflow,
                    workflow_action,
                    row.field_name,
                    before.get(row.field_name),
                    doc.get(row.field_name),
                )
        else:
            _log_child_table_changes(doc, before, workflow, workflow_action, row)


def _log_child_table_changes(doc, before, workflow, workflow_action, row):
    curr = doc.get(row.child_table_name) or []
    prev = before.get(row.child_table_name) or []
    max_len = max(len(curr), len(prev))

    for idx in range(max_len):
        old = prev[idx].get(row.child_field_name) if idx < len(prev) else None
        new = curr[idx].get(row.child_field_name) if idx < len(curr) else None
        if old != new:
            _insert_log(
                doc,
                workflow,
                workflow_action,
                f"{row.child_table_name}.{row.child_field_name}",
                old,
                new,
            )


def _insert_log(doc, workflow, workflow_action, fieldname, old, new):
    frappe.get_doc({
        "doctype": "Workflow Field Change Log",
        "reference_doctype": doc.doctype,
        "reference_name": doc.name,
        "workflow_name": workflow.name,
        "action": workflow_action or "",
        "changed_field": fieldname,
        "old_value": frappe.as_json(old) if isinstance(old, (dict, list)) else old,
        "new_value": frappe.as_json(new) if isinstance(new, (dict, list)) else new,
    }).insert(ignore_permissions=True)
