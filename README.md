# Field Level Workflow

Custom Frappe app to enable **field-level conditional workflow execution**.

This app extends the core Workflow behavior to trigger approvals **only when configured fields change**, reducing unnecessary workflow transitions.

---

## Features

- Enable/disable field-level workflow per Workflow
- Configure tracked fields per Workflow
- Prevent workflow actions when irrelevant fields change
- Audit log of field changes (optional)
- Upgrade-safe: no core patches

---

## Installation

```bash
bench get-app field_level_workflow
bench --site <site_name> install-app field_level_workflow
bench migrate
bench restart
```

After installation, two custom fields are added to **Workflow**:

- `Enable Field Level Workflow`
- `Tracked Fields`

---

## Usage (User Guide)

1. Open **Workflow**
2. Enable **Enable Field Level Workflow**
3. Add rows in **Tracked Fields** table
   - Fieldname
   - Condition (optional)
4. Save Workflow

Now, workflow transitions will only execute if at least one tracked field has changed.

---

## Admin Notes

### Performance

- Validation runs on `validate` and `before_workflow_action`
- Guarded internally; no overhead for doctypes without workflows
- Safe for large datasets

### Rollback / Disable

- Disable field-level logic by unchecking **Enable Field Level Workflow**
- Or uninstall the app (see below)

---

## Uninstall / Cleanup

The app supports **safe uninstall** with no data loss.

On uninstall:

- Custom Fields are **disabled**, not deleted
- Workflow override is automatically removed
- Existing Workflow and documents remain untouched

```bash
bench --site <site_name> uninstall-app field_level_workflow
bench migrate
bench restart
```

To fully remove artifacts (optional, manual):

- Delete disabled Custom Fields from **Customize Form**
- Remove change log records if no longer needed

---

## Compatibility

- Frappe v15+
- ERPNext / HRMS compatible

---

## License

MIT
