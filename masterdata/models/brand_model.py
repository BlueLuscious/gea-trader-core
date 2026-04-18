""" Brand persistence model for tenant-scoped catalog reference data. """

from typing import TYPE_CHECKING
from uuid import UUID
from django.db import models
from django.utils.translation import gettext_lazy as _
from masterdata.models.managers.brand_model_manager import BrandModelManager

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class BrandModel(models.Model):
    """ Master brand entity shared across domains.

    Example:
        BrandModel.objects.create(tenant=tenant, name="GEA", slug="gea")
    """

    tenant: "TenantModel" = models.ForeignKey(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="brands",
        verbose_name=_("Business"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Brand name"),
        help_text=_("Use the brand name your team and customers already recognize."),
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name=_("URL slug"),
        help_text=_("Usually created from the brand name. Adjust it only when you need a custom URL."),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
        help_text=_("Optional. Add short internal guidance about when this brand should be used."),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Available for products"),
        help_text=_("Disable this brand when you want to stop using it without deleting its history."),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    objects: BrandModelManager = BrandModelManager()

    id: int
    tenant_id: UUID

    class Meta:
        """ Declarative admin-facing metadata for brand persistence. """

        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "slug"),
                name="masterdata_brand_slug_unique_per_tenant",
            ),
        ]
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")

    def __str__(self) -> str:
        """ Return the admin-friendly label for the brand.

        Returns:
            str: Brand name.
        """
        return self.name
