from enum import StrEnum
from typing import Iterable, Mapping, TypeVar


EnumValue = TypeVar("EnumValue", bound=StrEnum)


def normalize_enum(value: str | None, enum_cls: type[EnumValue], default: EnumValue) -> EnumValue:
    if not value:
        return default

    if value in enum_cls._value2member_map_:
        return enum_cls(value)

    return default


def normalize_int(value: int | str | None, default: int, minimum: int = 0) -> int:
    try:
        return max(minimum, int(value))
    except (TypeError, ValueError):
        return default


def normalize_bool(value: bool | str | None, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def normalize_list(value: Iterable | None) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return list(value)


def normalize_data_attributes(value: Mapping | None) -> list[tuple[str, str]]:
    if not value:
        return []

    normalized: list[tuple[str, str]] = []
    for key, raw_attr_value in value.items():
        attr_name = str(key).strip().lower()
        if not attr_name:
            continue

        if not attr_name.startswith("data-"):
            attr_name = f"data-{attr_name}"

        if raw_attr_value is None:
            continue

        normalized.append((attr_name, str(raw_attr_value)))

    return normalized
