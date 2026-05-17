# Core Forms

This document describes reusable form infrastructure in `core/forms/`.

## Goal

`core/forms/` contains project-wide form fields and widgets that are not owned by a single domain app.

Use this package for form infrastructure when:

- the behavior is reusable across apps
- the behavior is not tied to one model or one domain workflow
- the form contract can stay stable independently from the first consumer

Do not place app-specific admin forms here. Those should stay inside the app that owns the domain flow.

## Current Exports

Current public exports:

- `JsonKeyValueField`
- `JsonKeyValueWidget`

These are re-exported from:

- `core/forms/__init__.py`

## `JsonKeyValueField`

`JsonKeyValueField` normalizes repeated key-value rows into a flat JSON-compatible dictionary.

Current contract:

- accepts empty input as `{}`
- accepts existing dictionaries
- accepts submitted row pairs
- trims keys and values
- ignores fully empty rows
- rejects rows that provide a value without a key
- rejects duplicate keys after trimming
- returns `dict[str, str]`

This field is meant for editable flat JSON objects, not arbitrary JSON.

Good fit:

- `{"size": "Large", "color": "Blue"}`
- `{"capacity": "20L", "packaging": "Drum"}`

Not a good fit:

- nested objects
- lists of objects
- typed JSON schemas
- read-only snapshot rendering

## `JsonKeyValueWidget`

`JsonKeyValueWidget` renders one flat dictionary as editable key-value rows.

Current behavior:

- renders one row per existing key-value pair
- renders one empty row for empty values
- submits repeated inputs through `<field_name>__key` and `<field_name>__value`
- submits a `<field_name>__present` marker so an intentionally empty editor clears the JSON value
- supports Django admin inline prefixes
- skips hidden `.empty-form` templates during JavaScript initialization
- initializes newly added inline rows through Django admin `formset:added`
- loads its own CSS and JavaScript through the widget `Media` contract

The widget uses Unfold-compatible classes for its visible controls because the first supported surface is owner admin.
Keep additional CSS focused on structure, spacing, and widget-specific layout only.

## Usage

Example:

```python
from django import forms
from django.utils.translation import gettext_lazy as _
from core.forms import JsonKeyValueField


class ExampleForm(forms.ModelForm):
    """ Example form that edits one flat JSONField through key-value rows. """

    metadata = JsonKeyValueField(
        label=_("Metadata"),
        help_text=_("Add metadata as key-value pairs."),
        required=False,
        key_label=_("Metadata key"),
        value_label=_("Metadata value"),
        add_label=_("Add metadata"),
        remove_label=_("Remove metadata"),
    )
```

## Read-Only JSON Display

Do not use `JsonKeyValueField` or `JsonKeyValueWidget` for read-only snapshots.

For read-only admin display, prefer a separate display helper or readonly admin method that formats the dictionary without inputs or JavaScript.

This keeps editable form behavior separate from snapshot presentation.

## Tests

Current tests live in:

- `core/tests/forms/test_json_key_value_field.py`

The tests cover:

- empty row normalization
- key and value trimming
- value-only validation
- duplicate key validation
- submitted repeated inputs
- submitted empty widgets clearing previous JSON values
- Unfold-compatible widget class context
