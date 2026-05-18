""" Shared form widgets used across project apps. """

from core.forms.widgets.json_key_value_widget import JsonKeyValueWidget
from core.forms.widgets.nested_json_key_value_widget import NestedJsonKeyValueWidget

__all__: list[str] = [
    "JsonKeyValueWidget",
    "NestedJsonKeyValueWidget",
]
