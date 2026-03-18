from enum import StrEnum


class ContentKind(StrEnum):
    ARTICLE = "article"
    BANNER = "banner"


KIND_ALIASES = {
    "hero": ContentKind.BANNER,
}


def normalize_kind(value: str | None, default: ContentKind = ContentKind.ARTICLE) -> ContentKind:
    if not value:
        return default

    if value in ContentKind._value2member_map_:
        return ContentKind(value)

    aliased = KIND_ALIASES.get(value)
    if aliased:
        return aliased

    return default
