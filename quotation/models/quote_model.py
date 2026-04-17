from typing import TYPE_CHECKING
from uuid import UUID
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from quotation.choices import QuoteWorkflowStatus
from quotation.models.managers.quote_model_manager import QuoteModelManager

if TYPE_CHECKING:
    from accounts.models.user_model import UserModel
    from cart.models import CartModel
    from tenancy.models import TenantModel


class QuoteModel(models.Model):
    """ Formal quotation request generated from a cart or direct input. """

    tenant: "TenantModel" = models.ForeignKey(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="quotes",
        verbose_name=_("Business"),
        help_text=_("Business that owns this quote and the follow-up around it."),
    )
    cart: "CartModel | None" = models.ForeignKey(
        "cart.CartModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
        verbose_name=_("Source cart"),
        help_text=_("Optional cart that originated this quote."),
    )
    user: "UserModel | None" = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
        verbose_name=_("Customer account"),
        help_text=_("Optional customer account related to this quote."),
    )
    workflow_status = models.CharField(
        max_length=16,
        choices=QuoteWorkflowStatus.choices,
        default=QuoteWorkflowStatus.DRAFT,
        verbose_name=_("Workflow status"),
        help_text=_("Current internal workflow stage of this quote."),
    )
    customer_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Customer name"),
        help_text=_("Name of the person requesting the quote."),
    )
    customer_email = models.EmailField(
        blank=True,
        default="",
        verbose_name=_("Customer email"),
        help_text=_("Email address used to follow up on this quote."),
    )
    customer_phone = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Customer phone"),
        help_text=_("Phone number used to follow up on this quote."),
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Company"),
        help_text=_("Optional company name when the quote belongs to a business customer."),
    )
    tax_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Tax ID"),
        help_text=_("Optional tax or company identification reference."),
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Internal notes"),
        help_text=_("Private notes not intended for customers."),
    )
    requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Requested at"),
        help_text=_("When the quote was formally requested."),
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Resolved at"),
        help_text=_("When the internal workflow for this quote reached a terminal resolution."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When this quote was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When this quote was last updated."),
    )

    objects: QuoteModelManager = QuoteModelManager()

    id: int
    tenant_id: UUID
    cart_id: int | None
    user_id: int | None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Quote")
        verbose_name_plural = _("Quotes")

    def __str__(self) -> str:
        """ Return the admin-friendly label for the quote.

        Returns:
            str: Quote label.
        """
        return f"Quote {self.pk}"

    def clean(self) -> None:
        """ Validate optional source cart ownership before persistence.

        Raises:
            ValidationError: When the selected source cart belongs to another tenant.
        """
        super().clean()
        self._validate_source_cart_scope()
        self._validate_workflow_transition()

    def save(self, *args: object, **kwargs: object) -> None:
        """ Persist the quote after validating source cart ownership.

        Args:
            *args: Positional save arguments.
            **kwargs: Keyword save arguments.

        Raises:
            ValidationError: When the selected source cart belongs to another tenant.
        """
        self._validate_source_cart_scope()
        self._validate_workflow_transition()
        self._apply_workflow_timestamps()
        super().save(*args, **kwargs)

    def _validate_source_cart_scope(self) -> None:
        """ Keep cart-originated quotes inside one tenant boundary.

        Raises:
            ValidationError: When the selected source cart belongs to another tenant.
        """
        if self.cart_id is None:
            return

        if self.cart.tenant_id != self.tenant_id:
            raise ValidationError({"cart": _("Source cart must belong to the same business as the quote.")})

    def _get_previous_workflow_status(self) -> str | None:
        """ Return the previously persisted workflow status when the quote exists.

        Returns:
            str | None: Persisted workflow status or ``None`` for new quotes.
        """
        if self.pk is None:
            return None

        return type(self).objects.filter(pk=self.pk).values_list("workflow_status", flat=True).first()

    def _validate_workflow_transition(self) -> None:
        """ Keep workflow transitions monotonic through the internal quote flow.

        Raises:
            ValidationError: When one workflow transition moves backward.
        """
        previous_status = self._get_previous_workflow_status()
        if previous_status is None:
            return

        workflow_order = self._get_workflow_order()
        previous_order = workflow_order[previous_status]
        current_order = workflow_order[self.workflow_status]

        terminal_statuses = {QuoteWorkflowStatus.COMPLETED, QuoteWorkflowStatus.CANCELLED}
        if previous_status in terminal_statuses and self.workflow_status != previous_status:
            raise ValidationError(
                {"workflow_status": _("Workflow status cannot change after the quote reaches a terminal resolution.")}
            )

        if current_order < previous_order:
            raise ValidationError(
                {"workflow_status": _("Workflow status cannot move backward once the quote progresses.")}
            )

    def _apply_workflow_timestamps(self) -> None:
        """ Derive internal workflow timestamps from the current workflow status. """
        workflow_order = self._get_workflow_order()
        now = timezone.now()
        current_order = workflow_order[self.workflow_status]

        if current_order >= workflow_order[QuoteWorkflowStatus.REQUESTED] and self.requested_at is None:
            self.requested_at = now

        if self.workflow_status in {QuoteWorkflowStatus.COMPLETED, QuoteWorkflowStatus.CANCELLED} and self.resolved_at is None:
            self.resolved_at = now

    def _get_workflow_order(self) -> dict[str, int]:
        """ Return the current internal workflow progression order.

        Returns:
            dict[str, int]: Rank per workflow status.
        """
        return {
            QuoteWorkflowStatus.DRAFT: 0,
            QuoteWorkflowStatus.REQUESTED: 1,
            QuoteWorkflowStatus.IN_PROGRESS: 2,
            QuoteWorkflowStatus.COMPLETED: 3,
            QuoteWorkflowStatus.CANCELLED: 3,
        }
