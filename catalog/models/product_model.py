from typing import TYPE_CHECKING
from uuid import UUID
from django.db import models
from django.utils.translation import gettext_lazy as _
from catalog.models.managers.product_model_manager import ProductModelManager

if TYPE_CHECKING:
    from masterdata.models import BrandModel, CategoryModel
    from tenancy.models import TenantModel


class ProductModel(models.Model):
    """ Catalog product entity used across public site and quotation flow.

    Example:
        ProductModel.objects.with_related().active()
    """

    tenant: "TenantModel" = models.ForeignKey(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Tenant"),
        help_text=_("Tenant that owns this product and its related catalog data."),
    )
    brand: "BrandModel | None" = models.ForeignKey(
        "masterdata.BrandModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Brand"),
        help_text=_("Optional brand shown with this product."),
    )
    category: "CategoryModel | None" = models.ForeignKey(
        "masterdata.CategoryModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Category"),
        help_text=_("Optional category used to organize this product."),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product name"),
        help_text=_("Customer-facing name shown across the catalog."),
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name=_("URL slug"),
        help_text=_("Short URL-friendly identifier used in product links."),
    )
    short_description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Short description"),
        help_text=_("Short summary for compact cards and product lists."),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Full description"),
        help_text=_("Full product description with the details customers should read."),
    )
    sku_base = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Base SKU"),
        help_text=_("Internal base reference used to identify this product family and its variants."),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Visible to customers"),
        help_text=_("Turn this off to hide the product without deleting it."),
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured product"),
        help_text=_("Highlight this product in featured catalog sections."),
    )
    requires_quote = models.BooleanField(
        default=True,
        verbose_name=_("Request through quote"),
        help_text=_("Enable this when customers should request a quote instead of buying directly."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When this product was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When this product was last updated."),
    )

    objects: ProductModelManager = ProductModelManager()

    id: int
    tenant_id: UUID
    brand_id: int | None
    category_id: int | None

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["tenant", "is_active", "is_featured"])]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "slug"],
                name="catalog_product_slug_unique_per_tenant",
            ),
        ]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self) -> str:
        """ Return the product label.

        Returns:
            str: Product name.
        """
        return self.name
