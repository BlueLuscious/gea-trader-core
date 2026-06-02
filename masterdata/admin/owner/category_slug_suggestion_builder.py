""" Build owner-admin category slug suggestions. """

from django.utils.text import slugify
from masterdata.models import CategoryModel
from tenancy.models import TenantModel


class CategorySlugSuggestionBuilder:
    """ Build tenant-unique category slug suggestions for owner-admin forms. """

    fallback_slug = "category"
    max_slug_length = 255

    @classmethod
    def build(
        cls,
        *,
        tenant: TenantModel,
        name: str,
        parent_id: str = "",
        parent_slug: str = "",
        exclude_id: str = "",
    ) -> str:
        """ Build one tenant-unique category slug suggestion.

        Args:
            tenant: Active tenant that owns the category.
            name: Category display name used as the slug source.
            parent_id: Optional persisted parent category id.
            parent_slug: Optional unsaved parent slug, useful for add-page inlines.
            exclude_id: Optional category id to ignore while checking uniqueness.

        Returns:
            str: Suggested slug that is unique inside the tenant.
        """
        base_slug = slugify(name).strip("-") or cls.fallback_slug
        prefix_slug = cls._resolve_parent_slug(
            tenant=tenant,
            parent_id=parent_id,
            parent_slug=parent_slug,
        )
        candidate_base = cls._build_candidate_base(prefix_slug=prefix_slug, base_slug=base_slug)
        return cls._build_unique_slug(
            tenant=tenant,
            candidate_base=candidate_base,
            exclude_id=exclude_id,
        )

    @classmethod
    def _resolve_parent_slug(cls, *, tenant: TenantModel, parent_id: str, parent_slug: str) -> str:
        """ Resolve the slug prefix from a persisted parent or an unsaved parent slug.

        Args:
            tenant: Active tenant that owns the category.
            parent_id: Optional persisted parent category id.
            parent_slug: Optional unsaved parent slug.

        Returns:
            str: Parent slug to use as prefix, or an empty string for root categories.
        """
        normalized_parent_id = cls._normalize_id(parent_id)
        if normalized_parent_id:
            parent = CategoryModel.objects.for_tenant(tenant).filter(pk=normalized_parent_id).first()
            if parent is not None:
                return parent.slug

        return slugify(parent_slug).strip("-")

    @classmethod
    def _build_candidate_base(cls, *, prefix_slug: str, base_slug: str) -> str:
        """ Build the non-suffixed slug candidate.

        Args:
            prefix_slug: Optional parent slug prefix.
            base_slug: Slugified category name.

        Returns:
            str: Candidate slug before uniqueness suffixes are applied.
        """
        if not prefix_slug:
            return cls._truncate_slug(base_slug)

        if base_slug == prefix_slug or base_slug.startswith(f"{prefix_slug}-"):
            return cls._truncate_slug(base_slug)

        return cls._truncate_slug(f"{prefix_slug}-{base_slug}")

    @classmethod
    def _build_unique_slug(cls, *, tenant: TenantModel, candidate_base: str, exclude_id: str) -> str:
        """ Add an incremental suffix until the slug is unique inside the tenant.

        Args:
            tenant: Active tenant that owns the category.
            candidate_base: Slug candidate before uniqueness suffixes are applied.
            exclude_id: Optional category id to ignore while checking uniqueness.

        Returns:
            str: Tenant-unique slug candidate.
        """
        candidate = candidate_base
        suffix = 2
        while cls._slug_exists(tenant=tenant, slug=candidate, exclude_id=exclude_id):
            suffix_text = f"-{suffix}"
            candidate = f"{cls._truncate_slug(candidate_base, reserved_length=len(suffix_text))}{suffix_text}"
            suffix += 1

        return candidate

    @classmethod
    def _slug_exists(cls, *, tenant: TenantModel, slug: str, exclude_id: str) -> bool:
        """ Return whether a slug already exists for the tenant.

        Args:
            tenant: Active tenant that owns the category.
            slug: Slug candidate to check.
            exclude_id: Optional category id to ignore while checking uniqueness.

        Returns:
            bool: ``True`` when the slug is already used by another category.
        """
        queryset = CategoryModel.objects.for_tenant(tenant).filter(slug=slug)
        normalized_exclude_id = cls._normalize_id(exclude_id)
        if normalized_exclude_id:
            queryset = queryset.exclude(pk=normalized_exclude_id)
        return queryset.exists()

    @classmethod
    def _normalize_id(cls, value: str) -> str:
        """ Normalize a querystring id before using it in ORM filters.

        Args:
            value: Raw id value received from the owner-admin request.

        Returns:
            str: Numeric id string or an empty string when invalid.
        """
        stripped_value = value.strip()
        return stripped_value if stripped_value.isdigit() else ""

    @classmethod
    def _truncate_slug(cls, slug: str, reserved_length: int = 0) -> str:
        """ Keep slug candidates inside the model field length.

        Args:
            slug: Candidate slug value.
            reserved_length: Characters reserved for a suffix.

        Returns:
            str: Truncated slug without leading or trailing separators.
        """
        max_length = cls.max_slug_length - reserved_length
        return slug[:max_length].strip("-") or cls.fallback_slug
