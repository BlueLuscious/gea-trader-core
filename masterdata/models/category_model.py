from django.db import models
from masterdata.models.managers.category_model_manager import CategoryModelManager


class CategoryModel(models.Model):
    """ Master category entity shared across domains.

    Example:
        CategoryModel.objects.create(name="Lubricacion", slug="lubricacion")
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
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
    parent_id: int | None
    children: CategoryModelManager

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        """ Return the admin-friendly label for the category.

        Returns:
            str: Category name.
        """
        return self.name
