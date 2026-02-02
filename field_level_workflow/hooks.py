# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "field_level_workflow"
app_title = "Field Level Workflow"
app_publisher = "Techseria Pvt Ltd"
app_description = "Extend Workflow to trigger only on tracked field changes"
app_icon = "octicon octicon-git-branch"
app_color = "blue"
app_email = "niraj@techseria.com"
app_license = "MIT"
app_version = "1.0.0"

# IMPORTANT:
# This app has NO build-time assets. JS is loaded dynamically by Frappe form events.
# In Frappe v15, esbuild crashes on single-asset apps. Explicitly exclude from build.
build_ignore = ["field_level_workflow"]

# Uninstall hook
before_uninstall = "field_level_workflow.uninstall.before_uninstall"

# Asset declarations (required for Frappe v15 esbuild stability)
app_include_js = [
    "/assets/field_level_workflow/js/workflow.js"
]
app_include_css = []

# NOTE: Do NOT use doctype_js for core DocTypes like Workflow in Frappe v15+
# It breaks esbuild asset resolution. Use app_include_js instead.

# Fixtures for custom fields
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["name", "in", [
            "Workflow-enable_field_level_workflow",
            "Workflow-tracked_fields"
        ]]]
    }
]

# Override Workflow class (initial, will be hardened later)
override_doctype_class = {
    "Workflow": "field_level_workflow.overrides.workflow.CustomWorkflow"
}

# Document hooks
# Field-level workflow relies on deterministic pre-save validation
# and a single interception point before workflow execution.
doc_events = {
    "*": {
        # Runs on validate for all doctypes; internally guarded by active workflow
        "validate": "field_level_workflow.utils.workflow_field_validator.validate_workflow_fields",
        # Frappe v15+ hook invoked by apply_workflow()
        "before_workflow_action": "field_level_workflow.utils.workflow_field_validator.check_field_changes",
    },
    "Workflow": {
        "validate": "field_level_workflow.utils.workflow_field_validator.validate_workflow_definition",
    },
}

# Asset handling:
# For single-asset apps in Frappe v15+, rely on public/build.json only.
# Do NOT declare app_include_js/app_include_css to avoid esbuild path resolution bug.
