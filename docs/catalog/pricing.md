# Catalog Pricing

This document explains the current catalog pricing contract.

## Goal

The catalog pricing model keeps one clear commercial source of truth while remaining compatible with both the current quotation-first runtime and a future ecommerce evolution.

## Source Of Truth

Price lives on `ProductVariantModel`.

`ProductModel` does not define a product-level base price.

This keeps the aggregate explicit:

- `ProductModel` is the catalog root users browse
- `ProductVariantModel` is the concrete commercial option behind that product

## Product Shape

Every product must have:

- at least one variant
- exactly one default variant

This applies to:

- simple products with one variant
- multi-variant products with several concrete options

## Quote-Only Products

If `ProductModel.requires_quote = True`:

- public price must not be exposed
- variant price remains internal-only
- variant price stays optional

Supported quote-only cases:

- a default variant without price
- a default variant with an internal price reference

## Directly Purchasable Products

If `ProductModel.requires_quote = False`:

- the product is directly purchasable
- the default variant must have a price
- public price resolves from the default variant

This applies to both:

- simple products with one variant
- multi-variant products with one default entrypoint variant

The default variant must remain available for selection.

## Current Enforcement

The current contract is enforced through a mix of model helpers, owner-admin validation, and DTO mapping.

### Product Helpers

`ProductModel` currently exposes:

- `has_variants()`
- `get_default_variant()`
- `get_public_price()`

Current behavior:

- `get_public_price()` returns `None` for quote-only products
- `get_public_price()` returns the default variant price for directly purchasable products

### Owner Admin

The owner product flow enforces the catalog write contract through the variant inline formset.

Current owner-admin rules:

- a product cannot be saved without variants
- a product cannot be saved without exactly one default variant
- a default variant cannot be kept unavailable for selection
- a directly purchasable product cannot be saved without a price on the default variant
- a quote-only product may keep the default variant price empty

Current owner-admin guidance:

- the product screen explains the difference between quote-only and directly purchasable flows
- the variant inline price field changes its help text based on `requires_quote`

### DTO Contract

`ProductModelDTO` currently exposes:

- `public_price`

This keeps one stable read path for future public catalog consumers without duplicating pricing logic in templates or views.

Current DTO behavior:

- quote-only products expose `public_price = None`
- directly purchasable products expose the default variant price as `public_price`

## What We Are Not Doing

Current exclusions:

- no product-level `base_price`
- no price ranges
- no uniform-price optimization
- no stock or checkout rules
- no ecommerce-specific merchandising logic beyond the current future-ready contract

## Related Files

- `catalog/models/product_model.py`
- `catalog/models/product_variant_model.py`
- `catalog/admin/owner/product_variant_model_inline_form.py`
- `catalog/admin/owner/product_variant_model_inline_formset.py`
- `catalog/dtos/product_model_dto.py`
- `catalog/dtos/factories/product_model_dto_factory.py`
