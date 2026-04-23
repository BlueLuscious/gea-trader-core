(function () {
    "use strict";

    function collectVariantPayload(itemNode) {
        const variantId = itemNode.dataset.variantId || "";
        const productId = itemNode.dataset.productId || "";
        const productName = itemNode.dataset.productName || "";
        const variantName = itemNode.dataset.variantName || "";

        return {
            product_id: productId,
            variant_id: variantId,
            quantity: 1,
            product_title: variantName ? `${productName} · ${variantName}` : productName,
        };
    }

    function handleAddVariant(event) {
        const addButton = event.target.closest("[data-product-variant-add]");
        if (!addButton) {
            return;
        }

        event.preventDefault();
        const variantItem = addButton.closest("[data-variant-item]");
        if (!variantItem) {
            return;
        }

        if (!window.CartController || typeof window.CartController.addItem !== "function") {
            return;
        }

        window.CartController.addItem(collectVariantPayload(variantItem)).then(() => {
        });
    }

    document.addEventListener("click", handleAddVariant);
})();
