""" Quote admin registration for the owner admin site. """

import logging
from typing import TYPE_CHECKING
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import action as unfold_action
from unfold.enums import ActionVariant
from core.adminsites.site_instances import owner_admin_site
from quotation.access import QuotationAccessPolicy
from quotation.admin.owner.quote_item_model_inline import QuoteItemModelInline
from quotation.admin.owner.quote_model_admin_form import QuoteModelAdminForm
from quotation.choices import QuoteWorkflowStatus
from quotation.models import QuoteModel
from quotation.services import QuoteWorkflowTransitionBatchResult, QuoteWorkflowTransitionService

if TYPE_CHECKING:
    from unfold.dataclasses import UnfoldAction
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
    list_display = ("id", "customer_name", "customer_email", "workflow_status", "requested_at", "updated_at")
    list_filter = ("workflow_status", "requested_at", "created_at", "updated_at")
    search_fields = ("=id", "customer_name", "customer_email", "company_name", "tax_id")
    ordering = ("-created_at",)
    list_select_related = ("cart", "user")
    save_on_top = True
    inlines = (QuoteItemModelInline,)
    actions = ("complete_selected_quotes", "cancel_selected_quotes")
    actions_submit_line = ("complete_quote", "cancel_quote")

    add_fieldsets = (
        (
            _("Customer"),
            {
                "classes": ("tab",),
                "description": _("Fill in who requested the quote and how to contact them."),
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
                "description": _("Start the quote with one workflow stage and any notes needed for follow-up."),
                "fields": (
                    "workflow_status",
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
                    ("requested_at", "resolved_at"),
                    ("created_at", "updated_at"),
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
            return QuotationAccessPolicy.can_change_quotation(request)

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

        return ("cart", "user", "requested_at", "resolved_at", "created_at", "updated_at")

    def get_fieldsets(self, request: HttpRequest, obj: QuoteModel | None = None) -> tuple[tuple[str, dict[str, object]], ...]:
        """ Return a simpler add layout and a richer read-only layout after creation.

        Args:
            request: Current admin request.
            obj: Quote instance when available.

        Returns:
            tuple[tuple[str, dict[str, object]], ...]: Fieldsets for the current quote workflow stage.
        """
        return self.add_fieldsets if obj is None else self.change_fieldsets

    def get_actions_submit_line(self, request: HttpRequest, object_id: int | str) -> list["UnfoldAction"]:
        """ Return object-level workflow actions while the quote is still open.

        Args:
            request: Current admin request.
            object_id: Quote primary key from the change form.

        Returns:
            list[UnfoldAction]: Available submit-line actions for the quote.
        """
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return []

        quote_is_active = (
            QuoteModel.objects.for_tenant(tenant)
            .active()
            .filter(pk=object_id)
            .exists()
        )
        if not quote_is_active:
            return []

        return super().get_actions_submit_line(request, object_id)

    @unfold_action(
        description=_("Complete quote"),
        icon="check_circle",
        variant=ActionVariant.SUCCESS,
    )
    def complete_quote(self, request: HttpRequest, obj: QuoteModel) -> None:
        """ Complete one quote from the owner change form.

        Args:
            request: Current admin request.
            obj: Quote being edited.
        """
        self._transition_quote_from_submit_line(
            request=request,
            quote=obj,
            workflow_status=QuoteWorkflowStatus.COMPLETED,
            success_message=_("Quote marked as completed."),
        )

    @unfold_action(
        description=_("Cancel quote"),
        icon="cancel",
        variant=ActionVariant.DANGER,
    )
    def cancel_quote(self, request: HttpRequest, obj: QuoteModel) -> None:
        """ Cancel one quote from the owner change form.

        Args:
            request: Current admin request.
            obj: Quote being edited.
        """
        self._transition_quote_from_submit_line(
            request=request,
            quote=obj,
            workflow_status=QuoteWorkflowStatus.CANCELLED,
            success_message=_("Quote marked as cancelled."),
        )

    @admin.action(
        description=_("Mark selected quotes as completed"),
        permissions=("change",),
    )
    def complete_selected_quotes(self, request: HttpRequest, queryset: "QuoteModelQuerySet") -> None:
        """ Complete selected quotes from the owner changelist.

        Args:
            request: Current admin request.
            queryset: Selected quote queryset.
        """
        result = QuoteWorkflowTransitionService.complete_many(queryset.iterator())
        self._message_batch_transition_result(
            request=request,
            result=result,
            success_message=_("%(count)s quote(s) marked as completed."),
        )

    @admin.action(
        description=_("Mark selected quotes as cancelled"),
        permissions=("change",),
    )
    def cancel_selected_quotes(self, request: HttpRequest, queryset: "QuoteModelQuerySet") -> None:
        """ Cancel selected quotes from the owner changelist.

        Args:
            request: Current admin request.
            queryset: Selected quote queryset.
        """
        result = QuoteWorkflowTransitionService.cancel_many(queryset.iterator())
        self._message_batch_transition_result(
            request=request,
            result=result,
            success_message=_("%(count)s quote(s) marked as cancelled."),
        )

    def _transition_quote_from_submit_line(
        self,
        *,
        request: HttpRequest,
        quote: QuoteModel,
        workflow_status: QuoteWorkflowStatus,
        success_message: str,
    ) -> None:
        """ Transition one quote and show an admin feedback message.

        Args:
            request: Current admin request.
            quote: Quote to transition.
            workflow_status: Target workflow status.
            success_message: Message shown when the transition succeeds.
        """
        try:
            QuoteWorkflowTransitionService.transition(quote, workflow_status)
        except ValidationError:
            self.message_user(
                request,
                _("Quote workflow status could not be updated because this transition is not allowed."),
                messages.ERROR,
            )
            return

        self.message_user(request, success_message, messages.SUCCESS)

    def _message_batch_transition_result(
        self,
        *,
        request: HttpRequest,
        result: QuoteWorkflowTransitionBatchResult,
        success_message: str,
    ) -> None:
        """ Show a summary message for one bulk workflow transition.

        Args:
            request: Current admin request.
            result: Batch transition result.
            success_message: Message template for changed quotes.
        """
        if result.changed_count:
            self.message_user(
                request,
                success_message % {"count": result.changed_count},
                messages.SUCCESS,
            )

        if result.skipped_count:
            self.message_user(
                request,
                _("%(count)s quote(s) already had the selected workflow status.") % {"count": result.skipped_count},
                messages.INFO,
            )

        if result.failed_count:
            self.message_user(
                request,
                _("%(count)s quote(s) could not be updated because their workflow transition is not allowed.")
                % {"count": result.failed_count},
                messages.WARNING,
            )
