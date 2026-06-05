""" Shared form widgets used across project apps. """

from core.forms.widgets.action_input_widget import ActionInputWidget
from core.forms.widgets.common_classes import UNFOLD_READONLY_VALUE_CLASSES
from core.forms.widgets.json_key_value_widget import JsonKeyValueWidget
from core.forms.widgets.nested_json_key_value_widget import NestedJsonKeyValueWidget

__all__: list[str] = [
    "ActionInputWidget",
    "JsonKeyValueWidget",
    "NestedJsonKeyValueWidget",
    "UNFOLD_READONLY_VALUE_CLASSES",
]
