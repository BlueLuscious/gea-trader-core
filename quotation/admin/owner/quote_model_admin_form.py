""" Form used by the owner quote admin. """

from typing import Any
from django import forms
from django.utils.translation import gettext_lazy as _
from quotation.models import QuoteModel


class QuoteModelAdminForm(forms.ModelForm):
    """ Owner-facing form for a quote record. """

    class Meta:
        model = QuoteModel
        fields = (
            "status",
            "customer_name",
            "customer_email",
            "customer_phone",
            "company_name",
            "tax_id",
            "notes",
            "cart",
            "user",
            "requested_at",
            "sent_at",
            "answered_at",
        )
        labels = {
            "status": _("Quote status"),
            "customer_name": _("Customer name"),
            "customer_email": _("Customer email"),
            "customer_phone": _("Customer phone"),
            "company_name": _("Company"),
            "tax_id": _("Tax ID"),
            "notes": _("Internal notes"),
            "cart": _("Source cart"),
            "user": _("Customer account"),
            "requested_at": _("Requested at"),
            "sent_at": _("Sent at"),
            "answered_at": _("Answered at"),
        }
        help_texts = {
            "status": _("Track where this quote currently is in your sales follow-up."),
            "company_name": _("Optional. Use this when the quote belongs to a business customer."),
            "tax_id": _("Optional tax or company identification reference."),
            "notes": _("Private context for your team. Customers do not need to see this text."),
        }

    def clean(self) -> dict[str, Any]:
        """ Enforce the minimum customer data required for a manual owner quote.

        Returns:
            dict[str, Any]: Cleaned quote form data.
        """
        cleaned_data = super().clean()
        customer_name = str(cleaned_data.get("customer_name") or "").strip()
        customer_email = str(cleaned_data.get("customer_email") or "").strip()
        customer_phone = str(cleaned_data.get("customer_phone") or "").strip()

        if not customer_name:
            self.add_error("customer_name", _("Enter the customer name before saving the quote."))

        if not customer_email and not customer_phone:
            error_message = _("Add at least an email address or phone number so your team can follow up.")
            self.add_error("customer_email", error_message)
            self.add_error("customer_phone", error_message)

        return cleaned_data
