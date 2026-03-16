from enum import StrEnum
from typing import Iterable, TypeVar


EnumValue = TypeVar("EnumValue", bound=StrEnum)


def normalize_enum(value: str | None, enum_cls: type[EnumValue], default: EnumValue) -> EnumValue:
    if not value:
        return default

    if value in enum_cls._value2member_map_:
        return enum_cls(value)

    return default


def normalize_bool(value: bool | str | None, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    return str(value).strip().lower() in {"1", "true", "yes", "on"}

