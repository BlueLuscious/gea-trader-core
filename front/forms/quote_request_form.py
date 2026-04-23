""" Public quote-request form used by the storefront quote-request modal. """

from __future__ import annotations

from django import forms


class QuoteRequestForm(forms.Form):
    """ Validate one public quote-request payload.

    The current storefront flow keeps the form intentionally small so customers
    can request follow-up without leaving the storefront flow.
    """

    customer_name = forms.CharField(
        max_length=255,
        label="Nombre y apellido",
        widget=forms.TextInput(
            attrs={
                "class": "gc-cart-quote-form__input",
                "placeholder": "Cómo te llamás",
                "autocomplete": "name",
            }
        ),
    )
    customer_email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "gc-cart-quote-form__input",
                "placeholder": "nombre@empresa.com",
                "autocomplete": "email",
            }
        ),
    )
    customer_phone = forms.CharField(
        required=False,
        max_length=64,
        label="Teléfono",
        widget=forms.TextInput(
            attrs={
                "class": "gc-cart-quote-form__input",
                "placeholder": "+54 11 1234 5678",
                "autocomplete": "tel",
            }
        ),
    )
    company_name = forms.CharField(
        required=False,
        max_length=255,
        label="Empresa",
        widget=forms.TextInput(
            attrs={
                "class": "gc-cart-quote-form__input",
                "placeholder": "Nombre de la empresa",
                "autocomplete": "organization",
            }
        ),
    )
    message = forms.CharField(
        required=False,
        label="Comentario",
        widget=forms.Textarea(
            attrs={
                "class": "gc-cart-quote-form__textarea",
                "placeholder": "Contanos si necesitás alguna presentación, volumen o dato adicional.",
                "rows": 4,
            }
        ),
    )

    def clean(self) -> dict[str, str]:
        """ Enforce one minimal public contact channel.

        Returns:
            dict[str, str]: Normalized cleaned data.
        """
        cleaned_data = super().clean()
        customer_email = str(cleaned_data.get("customer_email") or "").strip()
        customer_phone = str(cleaned_data.get("customer_phone") or "").strip()

        if not customer_email and not customer_phone:
            raise forms.ValidationError("Dejanos al menos un email o un teléfono para responderte.")

        cleaned_data["customer_email"] = customer_email
        cleaned_data["customer_phone"] = customer_phone
        cleaned_data["company_name"] = str(cleaned_data.get("company_name") or "").strip()
        cleaned_data["message"] = str(cleaned_data.get("message") or "").strip()
        cleaned_data["customer_name"] = str(cleaned_data.get("customer_name") or "").strip()
        return cleaned_data
