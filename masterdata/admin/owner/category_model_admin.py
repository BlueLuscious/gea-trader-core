""" Category admin registration for the owner admin site. """

from typing import TYPE_CHECKING
from django.contrib import admin
from django.db.models import ForeignKey
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import owner_admin_site
from masterdata.access import CategoryAccessPolicy
from masterdata.admin.owner.category_child_model_inline import CategoryChildModelInline
from masterdata.admin.owner.category_model_admin_form import CategoryModelAdminForm
from masterdata.models import CategoryModel

if TYPE_CHECKING:
    from django.forms import ModelChoiceField
    from masterdata.models.querysets.category_model_queryset import CategoryModelQuerySet
    from tenancy.models import TenantModel


@admin.register(CategoryModel, site=owner_admin_site)
class CategoryModelAdmin(ModelAdmin):
    """ Guided owner admin for tenant-scoped category reference data. """

    form = CategoryModelAdminForm
    inlines = (CategoryChildModelInline,)
    list_display = ("name", "parent", "sort_order", "is_active", "updated_at")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("sort_order", "name")
    prepopulated_fields = {"slug": ("name",)}
    save_on_top = True
    fieldsets = (
        (
            _("Category details"),
            {
                "classes": ("tab",),
                "description": _("Create reusable category references for the active business catalog."),
                "fields": (
                    ("name", "slug"),
                    "description",
                    ("parent", "sort_order"),
                    "is_active",
                ),
            },
        ),
        (
            _("Advanced details"),
            {
                "classes": ("tab",),
                "description": _("Read-only audit details for this category."),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> "CategoryModelQuerySet":
        """ Return only categories that belong to the active tenant.

        Args:
            request: Current admin request.

        Returns:
            QuerySet[CategoryModel]: Tenant-scoped category queryset.
        """
        tenant: "TenantModel | None" = getattr(request, "tenant", None)
        if tenant is None:
            return CategoryModel.objects.none()

        return super().get_queryset(request).for_tenant(tenant)

    def save_model(self, request: HttpRequest, obj: CategoryModel, form, change: bool) -> None:
        """ Persist categories under the active tenant in owner admin.

        Args:
            request: Current admin request.
            obj: Category being saved.
            form: Bound admin form.
            change: Whether the object already exists.
        """
        if not change:
            obj.tenant = getattr(request, "tenant", None)

        super().save_model(request, obj, form, change)

    def get_form(self, request: HttpRequest, obj: CategoryModel | None = None, change: bool = False, **kwargs):
        """ Inject the current request into the owner category form.

        Args:
            request: Current admin request.
            obj: Category being edited when present.
            change: Whether the screen edits an existing category.
            **kwargs: Extra admin form keyword arguments.

        Returns:
            type[CategoryModelAdminForm]: Request-aware owner category form class.
        """
        base_form_class = super().get_form(request, obj, change, **kwargs)

        class RequestAwareCategoryModelAdminForm(base_form_class):
            """ Owner category admin form bound to the current request context. """

            def __init__(self, *args: object, **form_kwargs: object) -> None:
                """ Forward the current request to the base owner category form.

                Args:
                    *args: Positional form arguments.
                    **form_kwargs: Keyword form arguments.
                """
                form_kwargs["request"] = request
                super().__init__(*args, **form_kwargs)

        return RequestAwareCategoryModelAdminForm

    def formfield_for_foreignkey(self, db_field: ForeignKey, request: HttpRequest, **kwargs) -> "ModelChoiceField | None":
        """ Scope category parent choices to the active tenant.

        Args:
            db_field: Foreign key field being built.
            request: Current admin request.
            **kwargs: Extra form field keyword arguments.

        Returns:
            ModelChoiceField | None: Built admin form field.
        """
        if db_field.name == "parent":
            tenant = getattr(request, "tenant", None)
            if tenant is None:
                kwargs["queryset"] = CategoryModel.objects.none()
            else:
                kwargs["queryset"] = CategoryModel.objects.for_tenant(tenant).order_by("sort_order", "name")

        form_field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "parent":
            object_id = request.resolver_match.kwargs.get("object_id") if getattr(request, "resolver_match", None) else None
            if object_id is not None:
                form_field.queryset = form_field.queryset.exclude(
                    pk__in=self._get_blocked_parent_ids(int(object_id))
                )

        return form_field

    def _get_blocked_parent_ids(self, category_id: int) -> set[int]:
        """ Return the category ids that cannot be chosen as parent in owner admin.

        Args:
            category_id: Current category primary key.

        Returns:
            set[int]: Category ids that would create an invalid parent relationship.
        """
        blocked_ids: set[int] = {category_id}
        pending_parent_ids: list[int] = [category_id]

        while pending_parent_ids:
            child_ids = list(
                CategoryModel.objects.filter(parent_id__in=pending_parent_ids).values_list("pk", flat=True)
            )
            next_pending_ids = [child_id for child_id in child_ids if child_id not in blocked_ids]
            blocked_ids.update(next_pending_ids)
            pending_parent_ids = next_pending_ids

        return blocked_ids

    def has_module_permission(self, request: HttpRequest) -> bool:
        """ Return whether the category module should appear in owner admin.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the actor may access category flows.
        """
        return CategoryAccessPolicy.can_access_categories(request)

    def has_view_permission(self, request: HttpRequest, obj: CategoryModel | None = None) -> bool:
        """ Return whether the current request may view categories in owner admin.

        Args:
            request: Current admin request.
            obj: Category instance when available.

        Returns:
            bool: ``True`` when the actor may view the category module or one in-scope category.
        """
        if obj is None:
            return CategoryAccessPolicy.can_access_categories(request)

        return CategoryAccessPolicy.can_view_category(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """ Return whether the current request may create categories.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the actor may add categories in the active tenant.
        """
        return CategoryAccessPolicy.can_add_category(request)

    def has_change_permission(self, request: HttpRequest, obj: CategoryModel | None = None) -> bool:
        """ Return whether the current request may edit categories in owner admin.

        Args:
            request: Current admin request.
            obj: Category instance when available.

        Returns:
            bool: ``True`` when the actor may change the category module or one in-scope category.
        """
        if obj is None:
            return CategoryAccessPolicy.can_access_categories(request)

        return CategoryAccessPolicy.can_change_category(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj: CategoryModel | None = None) -> bool:
        """ Disable hard delete for categories in owner admin.

        Args:
            request: Current admin request.
            obj: Category instance when available.

        Returns:
            bool: Always ``False`` to prefer deactivation via ``is_active``.
        """
        return False
