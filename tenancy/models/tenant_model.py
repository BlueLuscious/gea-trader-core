""" Tenant persistence model. """

from typing import TYPE_CHECKING
from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _
from tenancy.models.managers.tenant_model_manager import TenantModelManager

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from accounts.models import UserModel
    from cart.models import CartModel
    from catalog.models import ProductModel
    from masterdata.models import BrandModel, CategoryModel
    from quotation.models import QuoteModel
    from tenancy.models import TenantBrandingModel
    from tenancy.models import TenantGroupModel, TenantMembershipModel


class TenantModel(models.Model):
    """ Root tenant entity used to scope business data across the project. """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        verbose_name=_("Business name"),
        help_text=_("Public name used to identify this business across the admin."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("Business slug"),
        help_text=_("Stable URL-friendly identifier for this business."),
    )
    business_email = models.EmailField(
        blank=True,
        verbose_name=_("Business email"),
        help_text=_("Main contact email for this business."),
    )
    support_email = models.EmailField(
        blank=True,
        verbose_name=_("Support email"),
        help_text=_("Optional support email shown in emails and messages sent for this business."),
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Phone number"),
        help_text=_("Optional public phone number for this business."),
    )
    website_url = models.URLField(
        blank=True,
        verbose_name=_("Website"),
        help_text=_("Optional public website URL for this business."),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Business active"),
        help_text=_("Uncheck this to hide the business from active business selection and day-to-day use."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: TenantModelManager = TenantModelManager()

    memberships: "RelatedManager[TenantMembershipModel]"
    branding: "TenantBrandingModel"
    tenant_groups: "RelatedManager[TenantGroupModel]"
    users: "RelatedManager[UserModel]"
    brands: "RelatedManager[BrandModel]"
    categories: "RelatedManager[CategoryModel]"
    products: "RelatedManager[ProductModel]"
    carts: "RelatedManager[CartModel]"
    quotes: "RelatedManager[QuoteModel]"

    class Meta:
        ordering = ("name",)
        verbose_name = _("Business")
        verbose_name_plural = _("Businesses")

    def __str__(self) -> str:
        """ Return the admin-friendly tenant label.

        Returns:
            str: Tenant name.
        """
        return self.name
