""" Quote admin registration for the owner admin site. """

import logging
from typing import TYPE_CHECKING
from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from core.adminsites.site_instances import owner_admin_site
from quotation.access import QuotationAccessPolicy
from quotation.admin.owner.quote_item_model_inline import QuoteItemModelInline
from quotation.admin.owner.quote_model_admin_form import QuoteModelAdminForm
from quotation.models import QuoteModel

if TYPE_CHECKING:
    from quotation.models.querysets.quote_model_queryset import QuoteModelQuerySet
    from tenancy.models import TenantModel

logger = logging.getLogger(__name__)


@admin.register(QuoteModel, site=owner_admin_site)
class QuoteModelAdmin(ModelAdmin):
    """ Guided owner admin for quotes with snapshot items shown inline. """

    class Media:
        """ Load owner-specific assets for the quote admin layout. """

        css = {
            "all": ("quotation/admin/owner/quote_model_admin.css",),
        }

    form = QuoteModelAdminForm
    list_display = ("id", "customer_name", "customer_email", "status", "requested_at", "updated_at")
    list_filter = ("status", "requested_at", "created_at", "updated_at")
    search_fields = ("=id", "customer_name", "customer_email", "company_name", "tax_id")
    ordering = ("-created_at",)
    list_select_related = ("cart", "user")
    save_on_top = True
    inlines = (QuoteItemModelInline,)

    add_fieldsets = (
        (
            _("Customer"),
            {
                "classes": ("tab",),
                "description": _("Fill in who requested the quote and how your team can contact them."),
                "fields": (
                    ("customer_name", "customer_email"),
                    ("customer_phone", "company_name"),
                    "tax_id",
                ),
            },
        ),
        (
            _("Quote details"),
            {
                "classes": ("tab",),
                "description": _("Start the quote with a status and any internal context you need for follow-up."),
                "fields": (
                    "status",
                    "notes",
                ),
            },
        ),
    )
    change_fieldsets = add_fieldsets + (
        (
            _("Origin"),
            {
                "classes": ("tab",),
                "description": _("Reference information about where this quote came from."),
                "fields": (
                    ("user", "cart"),
                ),
            },
        ),
        (
            _("Timeline"),
            {
                "classes": ("tab",),
                "description": _("Read-only timestamps that describe the quote lifecycle."),
                "fields": (
                    ("requested_at", "sent_at"),
                    ("answered_at", "created_at"),
                    "updated_at",
                ),
            },
        ),
    )
    
    def get_queryset(self, request: HttpRequest) -> "QuoteModelQuerySet":
        """ Return only quotes that belong to the active tenant.

        Args:
            request: Current admin request.

        Returns:
            QuerySet[QuoteModel]: Tenant-scoped quote queryset.
        """
        tenant: "TenantModel | None" = getattr(request, "tenant", None)
        if tenant is None:
            logger.info("Returned no owner-visible quotes because no active tenant is bound to the request")
            return QuoteModel.objects.none()

        tenant_queryset: "QuoteModelQuerySet" = super().get_queryset(request).for_tenant(tenant)
        logger.info(
            "Scoped owner quote queryset tenant_id=%s quote_count=%s",
            tenant.pk,
            tenant_queryset.count(),
        )
        return tenant_queryset

    def save_model(self, request: HttpRequest, obj: QuoteModel, form: QuoteModelAdminForm, change: bool) -> None:
        """ Persist owner-created quotes under the active tenant.

        Args:
            request: Current admin request.
            obj: Quote being saved.
            form: Bound admin form.
            change: Whether the object already exists.
        """
        if not change:
            obj.tenant = getattr(request, "tenant", None)

        super().save_model(request, obj, form, change)
        logger.info(
            "Saved owner quote tenant_id=%s quote_id=%s change=%s",
            getattr(obj.tenant, "pk", None),
            obj.pk,
            change,
        )

    def has_module_permission(self, request: HttpRequest) -> bool:
        """ Return whether the quotation module should appear in owner admin.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the actor may access quotation flows.
        """
        return QuotationAccessPolicy.can_access_quotation(request)

    def has_view_permission(self, request: HttpRequest, obj: QuoteModel | None = None) -> bool:
        """ Return whether the current request may view quotes in owner admin.

        Args:
            request: Current admin request.
            obj: Quote instance when available.

        Returns:
            bool: ``True`` when the actor may view the quotation module or one in-scope quote.
        """
        if obj is None:
            return QuotationAccessPolicy.can_access_quotation(request)

        return QuotationAccessPolicy.can_view_quote(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """ Return whether the current request may create quotes.

        Args:
            request: Current admin request.

        Returns:
            bool: ``True`` when the actor may add quotes in the active tenant.
        """
        return QuotationAccessPolicy.can_add_quote(request)

    def has_change_permission(self, request: HttpRequest, obj: QuoteModel | None = None) -> bool:
        """ Return whether the current request may edit quotes in owner admin.

        Args:
            request: Current admin request.
            obj: Quote instance when available.

        Returns:
            bool: ``True`` when the actor may change the quotation module or one in-scope quote.
        """
        if obj is None:
            return QuotationAccessPolicy.can_access_quotation(request)

        return QuotationAccessPolicy.can_change_quote(request, obj)
    
    def has_delete_permission(self, request: HttpRequest, obj: QuoteModel | None = None) -> bool:
        """ Disable hard delete for quotes in owner admin.

        Args:
            request: Current admin request.
            obj: Quote instance when available.

        Returns:
            bool: Always ``False`` to keep quote history stable.
        """
        return False

    def get_readonly_fields(self, request: HttpRequest, obj: QuoteModel | None = None) -> tuple[str, ...]:
        """ Return read-only fields only after the quote has already been created.

        Args:
            request: Current admin request.
            obj: Quote instance when available.

        Returns:
            tuple[str, ...]: Read-only fields for the current owner quote screen.
        """
        if obj is None:
            return ()

        return ("cart", "user", "requested_at", "sent_at", "answered_at", "created_at", "updated_at")

    def get_fieldsets(self, request: HttpRequest, obj: QuoteModel | None = None) -> tuple[tuple[str, dict[str, object]], ...]:
        """ Return a simpler add layout and a richer read-only layout after creation.

        Args:
            request: Current admin request.
            obj: Quote instance when available.

        Returns:
            tuple[tuple[str, dict[str, object]], ...]: Fieldsets for the current quote workflow stage.
        """
        return self.add_fieldsets if obj is None else self.change_fieldsets
