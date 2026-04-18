from enum import StrEnum


class ThemeMode(StrEnum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class ThemeIntent(StrEnum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    TOGGLE = "toggle"
