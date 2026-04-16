from typing import TYPE_CHECKING
from uuid import UUID
from django.core.exceptions import ValidationError
from django.db import models
from masterdata.models.managers.category_model_manager import CategoryModelManager

if TYPE_CHECKING:
    from tenancy.models import TenantModel


class CategoryModel(models.Model):
    """ Master category entity shared across domains.

    Example:
        CategoryModel.objects.create(tenant=tenant, name="Lubricacion", slug="lubricacion")
    """

    tenant: "TenantModel" = models.ForeignKey(
        "tenancy.TenantModel",
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")
    parent: "CategoryModel | None" = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: CategoryModelManager = CategoryModelManager()

    id: int
    tenant_id: UUID
    parent_id: int | None
    children: CategoryModelManager

    class Meta:
        ordering = ("sort_order", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "slug"),
                name="masterdata_category_slug_unique_per_tenant",
            ),
        ]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        """ Return the admin-friendly label for the category.

        Returns:
            str: Category name.
        """
        return self.name

    def clean(self) -> None:
        """ Validate category relationships before persistence.

        Raises:
            ValidationError: When the parent category belongs to another tenant or
            creates an invalid hierarchy.
        """
        super().clean()
        self._validate_parent_relationship()

    def save(self, *args: object, **kwargs: object) -> None:
        """ Persist the category after validating tenant-safe hierarchy rules.

        Args:
            *args: Positional save arguments.
            **kwargs: Keyword save arguments.

        Raises:
            ValidationError: When the parent category belongs to another tenant or
            creates an invalid hierarchy.
        """
        self._validate_parent_relationship()
        super().save(*args, **kwargs)

    def _validate_parent_relationship(self) -> None:
        """ Keep category trees tenant-scoped and cycle-free.

        Raises:
            ValidationError: When the parent category belongs to a different tenant,
            when a category tries to parent itself, or when the relationship creates
            a cycle in the hierarchy.
        """
        if self.parent_id is None:
            return

        if self.pk is not None and self.parent_id == self.pk:
            raise ValidationError({"parent": "A category cannot be its own parent."})

        if self.tenant_id != self.parent.tenant_id:
            raise ValidationError({"parent": "Parent category must belong to the same tenant."})

        current_parent: "CategoryModel | None" = self.parent
        visited_parent_ids: set[int] = set()
        while current_parent is not None:
            if current_parent.pk in visited_parent_ids:
                raise ValidationError({"parent": "Category hierarchy cannot contain cycles."})

            visited_parent_ids.add(current_parent.pk)
            if self.pk is not None and current_parent.pk == self.pk:
                raise ValidationError({"parent": "Category hierarchy cannot contain cycles."})

            current_parent = current_parent.parent
