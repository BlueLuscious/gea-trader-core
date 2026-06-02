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

- `ActionInputWidget`
- `JsonKeyValueField`
- `JsonKeyValueWidget`
- `NestedJsonKeyValueField`
- `NestedJsonKeyValueWidget`

These are re-exported from:

- `core/forms/__init__.py`

Internal field modules live in:

- `core/forms/fields/`

Internal widget modules live in:

- `core/forms/widgets/`

Widget static assets live in:

- `core/static/core/forms/widgets/`

`BaseJsonKeyValueWidget` is an internal extension point for shared widget labels, Unfold-compatible classes, submitted-data helpers, and shared CSS.
Public consumers should import the concrete fields or widgets from `core.forms`, not from internal modules.

## `ActionInputWidget`

`ActionInputWidget` renders a normal text input with one inline action button.

Current contract:

- keeps the original field value contract unchanged
- renders input and action button from a Django widget template
- receives an `action_url` used by the generic JavaScript controller
- receives an `action_label` for the button text
- reads one response key, configured by `response_value_key`, and writes that value back to the input
- supports static request params through `static_params`
- supports dynamic request params through `source_params`
- uses Unfold-compatible input and button classes, keeping custom CSS limited to inline layout
- keeps domain-specific generation logic outside `core/forms/`

`source_params` entries are dictionaries with:

- `name`: request query parameter name
- `selector`: CSS selector used to find the source element
- `scope`: `document` for global lookup or `closest` for lookup inside a nearby container
- `closest_selector`: optional ancestor selector used when `scope` is `closest`
- `attribute`: optional attribute name to read instead of the source element value

Good fit:

- admin slug suggestion buttons
- small server-backed value suggestions
- reusable input actions where the field remains a plain text-like field

Not a good fit:

- actions that mutate persisted data immediately
- rich multi-input editors
- domain-specific validation or slug generation logic

Example:

```python
from django import forms
from django.utils.translation import gettext_lazy as _
from core.forms import ActionInputWidget


class ExampleForm(forms.Form):
    """ Example form that suggests a value from a server endpoint. """

    slug = forms.SlugField(
        widget=ActionInputWidget(
            action_url="/owner-admin/example/suggest-slug/",
            action_label=_("Suggest slug"),
            response_value_key="slug",
            source_params=[
                {
                    "name": "name",
                    "selector": "#id_name",
                    "scope": "document",
                }
            ],
        )
    )
```

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

## `NestedJsonKeyValueField`

`NestedJsonKeyValueField` normalizes submitted key-value rows with explicit row and parent IDs into a bounded nested dictionary.

Current contract:

- accepts empty input as `{}`
- accepts existing nested dictionaries
- accepts submitted row dictionaries with `row_id`, `parent_id`, `key`, and `value`
- trims keys and scalar values
- ignores fully empty rows and empty groups
- rejects rows that provide a value without a key
- rejects groups that contain child rows without a key
- rejects duplicate keys within the same sibling level
- allows the same key under different parents
- rejects rows that exceed the configured `max_depth`
- rejects one node having both a scalar value and child rows
- returns `dict[str, str | dict]`

Depth is configurable through `max_depth`.

Defaults and guardrails:

- default `max_depth` is `2`
- minimum `max_depth` is `1`
- maximum supported `max_depth` is `4`

Good fit:

- `{"capacity": "20L"}`
- `{"packaging": {"type": "Drum", "volume": "20L"}}`
- `{"dimensions": {"inner": {"width": "10cm"}}}` when `max_depth=3`

Not a good fit:

- lists of values
- typed JSON schemas
- arbitrary JSON editing
- read-only snapshot rendering

## `NestedJsonKeyValueWidget`

`NestedJsonKeyValueWidget` renders a bounded nested dictionary as one flat, indented set of key-value rows.

Current behavior:

- renders one row per existing key or nested key
- renders one empty root row for empty values
- submits repeated inputs through `<field_name>__row_id`, `<field_name>__parent_id`, `<field_name>__key`, and `<field_name>__value`
- submits a `<field_name>__present` marker so an intentionally empty editor clears the JSON value
- uses row IDs and parent IDs instead of path delimiters, so keys may contain characters such as `.`
- supports Django admin inline prefixes
- skips hidden `.empty-form` templates during JavaScript initialization
- initializes newly added inline rows through Django admin `formset:added`
- can add root rows and child rows up to the configured `max_depth`
- removes descendant rows when a parent row is removed
- clears a scalar value when a child row is added to that row
- loads shared base CSS plus its own CSS and JavaScript through the widget `Media` contract

The widget uses Unfold-compatible classes for its visible controls.
Keep additional CSS focused on nested layout and indentation only.

The nested widget is available, but it should only be wired into a domain admin after a real nested JSON editing use case is confirmed.

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
- loads shared base CSS plus its own CSS and JavaScript through the widget `Media` contract

The widget uses Unfold-compatible classes for its visible controls.
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
Do not use `NestedJsonKeyValueField` for read-only snapshots either.

For read-only admin display, prefer a separate display helper or readonly admin method that formats the dictionary without inputs or JavaScript.

This keeps editable form behavior separate from snapshot presentation.

## Tests

Current tests live in:

- `core/tests/forms/test_action_input_widget.py`
- `core/tests/forms/test_json_key_value_field.py`
- `core/tests/forms/test_nested_json_key_value_field.py`

The tests cover:

- empty row normalization
- key and value trimming
- value-only validation
- duplicate key validation
- submitted repeated inputs
- submitted empty widgets clearing previous JSON values
- Unfold-compatible widget class context
- nested row normalization by `row_id` and `parent_id`
- nested max-depth validation
- nested sibling duplicate validation
- nested scalar-versus-children validation
- nested widget row flattening
- nested widget submitted row extraction
- nested widget empty-submit handling
- action input widget context
- action input widget rendered data contract
- action input widget media assets
