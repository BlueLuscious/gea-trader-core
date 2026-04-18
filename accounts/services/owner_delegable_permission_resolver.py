""" Policy object for owner-delegable Django permissions. """

import logging
from django.contrib.auth.models import Permission
from django.contrib.auth.models import PermissionsMixin
from django.db.models import Q, QuerySet
from tenancy.models import TenantModel
from tenancy.access.tenant_access_policy import TenantAccessPolicy

logger = logging.getLogger(__name__)


class OwnerDelegablePermissionResolver:
    """ Resolve the permissions that one owner may delegate through tenant-scoped groups. """

    @classmethod
    def get_queryset(cls, user: PermissionsMixin, tenant: TenantModel | None = None) -> QuerySet[Permission]:
        """ Return the permissions that the current owner may delegate.

        Args:
            user: Authenticated owner user whose effective permissions should cap delegation.
            tenant: Active tenant currently in scope.

        Returns:
            QuerySet[Permission]: Permissions already held by the owner inside the active tenant context.
        """
        if not TenantAccessPolicy.can_manage_tenant(user, tenant):
            logger.info(
                "Returned no delegable permissions because the actor cannot manage the active tenant user_id=%s tenant_id=%s",
                getattr(user, "pk", None),
                getattr(tenant, "pk", None),
            )
            return Permission.objects.none()

        user_permission_keys = user.get_all_permissions()
        permission_filter = Q()

        for permission_key in user_permission_keys:
            try:
                app_label, codename = permission_key.split(".", 1)
            except ValueError:
                continue

            permission_filter |= Q(
                content_type__app_label=app_label,
                codename=codename,
            )

        if not permission_filter:
            logger.info(
                "Returned no delegable permissions because the actor has no effective permission keys user_id=%s tenant_id=%s",
                getattr(user, "pk", None),
                getattr(tenant, "pk", None),
            )
            return Permission.objects.none()

        permission_queryset = Permission.objects.filter(permission_filter).select_related("content_type").order_by(
            "content_type__app_label",
            "content_type__model",
            "codename",
        )
        logger.info(
            "Resolved delegable permissions user_id=%s tenant_id=%s permission_count=%s",
            getattr(user, "pk", None),
            getattr(tenant, "pk", None),
            permission_queryset.count(),
        )
        return permission_queryset
