""" Owner inline formset for direct category children. """

from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet
from masterdata.models import CategoryModel


class CategoryChildModelInlineFormSet(BaseInlineFormSet):
    """ Persist direct child categories under the same tenant as their parent. """

    def _construct_form(self, i: int, **kwargs: object) -> ModelForm:
        """ Build one inline child form with inherited tenant and parent context.

        Args:
            i: Zero-based form index.
            **kwargs: Extra form construction keyword arguments.

        Returns:
            ModelForm: Bound child-category form with parent and tenant preloaded.
        """
        form: ModelForm = super()._construct_form(i, **kwargs)
        form.instance.parent = self.instance
        form.instance.tenant = self.instance.tenant
        return form

    def save_new(self, form: ModelForm, commit: bool = True) -> CategoryModel:
        """ Persist one newly added child category with inherited tenant ownership.

        Args:
            form: Bound inline form for the child category.
            commit: Whether the new child category should be saved immediately.

        Returns:
            CategoryModel: Newly created child category instance.
        """
        child_category: CategoryModel = super().save_new(form, commit=False)
        child_category.tenant = self.instance.tenant

        if commit:
            child_category.save()
            form.save_m2m()

        return child_category
