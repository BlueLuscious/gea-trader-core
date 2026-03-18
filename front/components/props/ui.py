from enum import StrEnum


class BadgeVariant(StrEnum):
    NEUTRAL = "neutral"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    ACCENT = "accent"
    INVERSE = "inverse"


class AutoplayMode(StrEnum):
    STOP = "stop"
    LOOP = "loop"
    BOUNCE = "bounce"


class DotsMode(StrEnum):
    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"


class IconStyle(StrEnum):
    SOLID = "solid"
    REGULAR = "regular"
    BRANDS = "brands"


class ButtonVariant(StrEnum):
    SOLID = "solid"
    SOFT = "soft"
    OUTLINE = "outline"
    GHOST = "ghost"


class Size(StrEnum):
    SM = "sm"
    MD = "md"
    LG = "lg"
    FULL = "full"


ButtonSize = Size
SwitchSize = Size


class Radius(StrEnum):
    SM = "sm"
    MD = "md"
    LG = "lg"
    FULL = "full"


ButtonRadius = Radius


class ShadowSize(StrEnum):
    NONE = "none"
    SM = "sm"
    MD = "md"
    LG = "lg"


class FontSize(StrEnum):
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "2xl"


class PanelWidth(StrEnum):
    AUTO = "auto"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    FULL = "full"
