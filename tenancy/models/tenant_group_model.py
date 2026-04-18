""" Tenant-group persistence model for tenant-scoped auth-group bindings. """

from typing import TYPE_CHECKING
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from tenancy.models.managers.tenant_group_model_manager import TenantGroupModelManager

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class TenantGroupModel(models.Model):
    """ Binding that scopes one Django auth group to one tenant. """

    tenant: "TenantModel" = models.ForeignKey(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="tenant_groups",
        verbose_name=_("Business"),
        help_text=_("Business that owns this permission group."),
    )
    group: Group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="tenant_binding",
        verbose_name=_("Permission group"),
        help_text=_("Django auth group scoped to the selected business."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: TenantGroupModelManager = TenantGroupModelManager()

    id: int
    group_id: int

    class Meta:
        """ Declarative admin-facing metadata for tenant-group persistence. """

        ordering = ("tenant__name", "group__name", "id")
        verbose_name = _("Business group")
        verbose_name_plural = _("Business groups")

    def __str__(self) -> str:
        """ Return the admin-friendly tenant-group label.

        Returns:
            str: Tenant-group label.
        """
        return f"{self.tenant} -> {self.group}"
