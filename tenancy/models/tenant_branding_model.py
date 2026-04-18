""" Tenant-branding persistence model for business visual identity assets. """

from typing import TYPE_CHECKING
from django.db import models
from django.utils.translation import gettext_lazy as _
from tenancy.models.managers.tenant_branding_model_manager import TenantBrandingModelManager

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class TenantBrandingModel(models.Model):
    """ Visual branding assets and display metadata attached to one tenant. """

    tenant: "TenantModel" = models.OneToOneField(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="branding",
        verbose_name=_("Business"),
        help_text=_("Business that owns this branding configuration."),
    )
    display_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Display name"),
        help_text=_("Optional public name used instead of the business name when branding is shown."),
    )
    logo_light = models.ImageField(
        upload_to="branding/logos/",
        blank=True,
        verbose_name=_("Light logo"),
        help_text=_("Logo variant intended for light backgrounds."),
    )
    logo_dark = models.ImageField(
        upload_to="branding/logos/",
        blank=True,
        verbose_name=_("Dark logo"),
        help_text=_("Logo variant intended for dark backgrounds."),
    )
    icon_light = models.ImageField(
        upload_to="branding/icons/",
        blank=True,
        verbose_name=_("Light icon"),
        help_text=_("Compact icon variant intended for light backgrounds."),
    )
    icon_dark = models.ImageField(
        upload_to="branding/icons/",
        blank=True,
        verbose_name=_("Dark icon"),
        help_text=_("Compact icon variant intended for dark backgrounds."),
    )
    favicon_light = models.ImageField(
        upload_to="branding/favicons/",
        blank=True,
        verbose_name=_("Light favicon"),
        help_text=_("Favicon variant intended for light browser themes or light backgrounds."),
    )
    favicon_dark = models.ImageField(
        upload_to="branding/favicons/",
        blank=True,
        verbose_name=_("Dark favicon"),
        help_text=_("Favicon variant intended for dark browser themes or dark backgrounds."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: TenantBrandingModelManager = TenantBrandingModelManager()

    class Meta:
        """ Declarative admin-facing metadata for tenant branding. """

        ordering = ("tenant__name", "id")
        verbose_name = _("Business branding")
        verbose_name_plural = _("Business branding")

    def __str__(self) -> str:
        """ Return the admin-friendly branding label.

        Returns:
            str: Branding label.
        """
        return self.display_name or str(self.tenant)
