import frappe
from frappe.model.document import Document


class WorkflowFieldChangeLog(Document):
    """Immutable audit log for field-level workflow executions.

    Records old/new values for a single field change.
    Entries are write-once and cannot be updated or deleted.
    """

    def before_insert(self):
        # Enforce immutability defaults
        self.changed_by = self.changed_by or frappe.session.user
        self.changed_on = self.changed_on or frappe.utils.now()

    def on_update(self):
        # Prevent updates after insert
        if not self.flags.in_insert:
            frappe.throw(frappe._("Workflow Field Change Log entries are immutable."))

    def on_trash(self):
        frappe.throw(frappe._("Workflow Field Change Log entries cannot be deleted."))
