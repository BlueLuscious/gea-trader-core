from enum import StrEnum


class BadgeVariant(StrEnum):
    NEUTRAL = "neutral"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    ACCENT = "accent"
    INVERSE = "inverse"


class IconStyle(StrEnum):
    SOLID = "solid"
    REGULAR = "regular"
    BRANDS = "brands"


class ButtonVariant(StrEnum):
    SOLID = "solid"
    SOFT = "soft"
    OUTLINE = "outline"
    GHOST = "ghost"


class ButtonSize(StrEnum):
    SM = "sm"
    MD = "md"
    LG = "lg"
    FULL = "full"


class ButtonRadius(StrEnum):
    SM = "sm"
    MD = "md"
    LG = "lg"
    FULL = "full"
