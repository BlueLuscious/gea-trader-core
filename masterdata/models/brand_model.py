from typing import TYPE_CHECKING
from uuid import UUID
from django.db import models
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
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: BrandModelManager = BrandModelManager()

    id: int
    tenant_id: UUID

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "slug"),
                name="masterdata_brand_slug_unique_per_tenant",
            ),
        ]
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self) -> str:
        """ Return the admin-friendly label for the brand.

        Returns:
            str: Brand name.
        """
        return self.name
