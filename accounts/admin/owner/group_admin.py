""" Group admin registration for the owner admin site. """

import logging
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group, Permission
from django.apps import apps
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from accounts.access import AccountsAccessPolicy
from unfold.admin import ModelAdmin
from accounts.admin.owner.group_admin_form import OwnerGroupAdminForm
from accounts.services.owner_delegable_permission_resolver import OwnerDelegablePermissionResolver
from core.adminsites.site_instances import owner_admin_site
from tenancy.models import TenantGroupModel

logger = logging.getLogger(__name__)


@admin.register(Group, site=owner_admin_site)
class OwnerGroupAdmin(BaseGroupAdmin, ModelAdmin):
    """ Guided group admin scoped to the active tenant. """

    class Media:
        """ Owner admin assets for small layout refinements. """

        css = {
            "all": ("accounts/admin/owner/group_admin.css",),
        }

    form = OwnerGroupAdminForm
    save_on_top = True
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

    fieldsets = (
        (
            _("Team group"),
            {
                "classes": ("tab",),
                "description": _("Create permission groups for people working in this business."),
                "fields": ("name",),
            },
        ),
        (
            _("Access permissions"),
            {
                "classes": ("tab",),
                "description": _("This group can include any permissions you already have."),
                "fields": ("permissions",),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Group]:
        """ Return only groups bound to the active tenant.

        Args:
            request: Current admin request.

        Returns:
            QuerySet[Group]: Tenant-scoped owner-visible groups.
        """
        tenant = getattr(request, "tenant", None)
        queryset = super().get_queryset(request)

        if tenant is None:
            logger.info("Returned no owner-visible groups because no active tenant is bound to the request")
            return queryset.none()

        tenant_queryset = queryset.filter(tenant_binding__tenant=tenant)
        logger.info(
            "Scoped owner group queryset tenant_id=%s group_count=%s",
            tenant.pk,
            tenant_queryset.count(),
        )
        return tenant_queryset

    def formfield_for_manytomany(self, db_field, request: HttpRequest, **kwargs):
        """ Filter delegated permissions to the current owner's effective permissions.

        Args:
            db_field: Django model field being converted into a form field.
            request: Current admin request.
            **kwargs: Remaining field construction arguments.

        Returns:
            forms.Field: Built admin form field.
        """
        if db_field.name == "permissions":
            kwargs["queryset"] = OwnerDelegablePermissionResolver.get_queryset(
                request.user,
                getattr(request, "tenant", None),
            )

        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)

        if db_field.name == "permissions":
            form_field.label_from_instance = self._build_permission_label
            logger.info(
                "Built owner group permission field tenant_id=%s permission_count=%s",
                getattr(getattr(request, "tenant", None), "pk", None),
                form_field.queryset.count(),
            )

        return form_field

    @staticmethod
    def _build_permission_label(permission: Permission) -> str:
        """ Return one translated label for the permission chooser widget.

        Args:
            permission: Permission option being rendered in the admin widget.

        Returns:
            str: Human-friendly translated permission label.
        """
        model_class = permission.content_type.model_class()

        if model_class is None:
            try:
                model_class = apps.get_model(permission.content_type.app_label, permission.content_type.model)
            except LookupError:
                model_class = None

        app_label = permission.content_type.app_label.replace("_", " ")
        model_label = permission.content_type.model.replace("_", " ")

        if model_class is not None:
            app_label = str(model_class._meta.app_config.verbose_name)
            model_label = str(model_class._meta.verbose_name)

        return f"{capfirst(app_label)} | {capfirst(model_label)} | {OwnerGroupAdmin._build_permission_action_label(permission, model_label)}"

    @staticmethod
    def _build_permission_action_label(permission: Permission, model_label: str) -> str:
        """ Return one translated action label for a permission option.

        Args:
            permission: Permission option being rendered in the admin widget.
            model_label: Lowercase verbose model name used in the sentence.

        Returns:
            str: Translated action description or the stored permission name.
        """
        sentence_model_label = model_label[:1].lower() + model_label[1:] if model_label else model_label
        action_templates = {
            f"add_{permission.content_type.model}": gettext("Can add %(name)s"),
            f"change_{permission.content_type.model}": gettext("Can change %(name)s"),
            f"delete_{permission.content_type.model}": gettext("Can delete %(name)s"),
            f"view_{permission.content_type.model}": gettext("Can view %(name)s"),
        }
        template = action_templates.get(permission.codename)

        if template is None:
            return permission.name

        return template % {"name": sentence_model_label}

    def save_model(self, request: HttpRequest, obj: Group, form: OwnerGroupAdminForm, change: bool) -> None:
        """ Persist one tenant-scoped group and create its tenant binding on add.

        Args:
            request: Current admin request.
            obj: Group being saved.
            form: Bound owner group form.
            change: Whether this is an existing group edit.
        """
        super().save_model(request, obj, form, change)

        if change:
            return

        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return

        TenantGroupModel.objects.get_or_create(tenant=tenant, group=obj)
        logger.info(
            "Created owner group tenant binding tenant_id=%s group_id=%s",
            tenant.pk,
            obj.pk,
        )

    def has_module_permission(self, request: HttpRequest) -> bool:
        """ Require an active tenant before exposing the owner group module.

        Args:
            request: Current admin request.

        Returns:
            bool: True when the request has an active tenant and base permissions.
        """
        return AccountsAccessPolicy.can_access_groups(request) and super().has_module_permission(request)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """ Require an active tenant before allowing group creation.

        Args:
            request: Current admin request.

        Returns:
            bool: True when the request has an active tenant and base permissions.
        """
        return AccountsAccessPolicy.can_add_group(request) and super().has_add_permission(request)

    def has_view_permission(self, request: HttpRequest, obj: Group | None = None) -> bool:
        """ Restrict group visibility to the active tenant scope.

        Args:
            request: Current admin request.
            obj: Group being inspected, when present.

        Returns:
            bool: True when the group belongs to the active tenant and base permissions pass.
        """
        if not AccountsAccessPolicy.can_access_groups(request):
            return False

        if not super().has_view_permission(request, obj):
            return False

        if obj is None:
            return True

        return AccountsAccessPolicy.can_view_group(request, obj)

    def has_change_permission(self, request: HttpRequest, obj: Group | None = None) -> bool:
        """ Restrict group editing to the active tenant scope.

        Args:
            request: Current admin request.
            obj: Group being edited, when present.

        Returns:
            bool: True when the group belongs to the active tenant and base permissions pass.
        """
        if not AccountsAccessPolicy.can_access_groups(request):
            return False

        if not super().has_change_permission(request, obj):
            return False

        if obj is None:
            return True

        return AccountsAccessPolicy.can_view_group(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: Group | None = None) -> bool:
        """ Restrict group deletion to the active tenant scope.

        Args:
            request: Current admin request.
            obj: Group being deleted, when present.

        Returns:
            bool: True when the group belongs to the active tenant and base permissions pass.
        """
        if not AccountsAccessPolicy.can_access_groups(request):
            return False

        if not super().has_delete_permission(request, obj):
            return False

        if obj is None:
            return True

        return AccountsAccessPolicy.can_view_group(request, obj)
