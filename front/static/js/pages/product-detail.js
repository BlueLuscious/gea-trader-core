(function () {
    "use strict";

    function collectVariantPayload(itemNode) {
        const variantId = itemNode.dataset.variantId || "";
        const productId = itemNode.dataset.productId || "";
        const productName = itemNode.dataset.productName || "";
        const variantName = itemNode.dataset.variantName || "";
        const variantSku = itemNode.dataset.variantSku || "";
        const variantPrice = itemNode.dataset.variantPrice || "";
        const variantImageUrl = itemNode.dataset.variantImageUrl || "";
        const variantHref = itemNode.dataset.variantHref || "";
        const displayName = variantName ? `${productName} - ${variantName}` : productName;

        return {
            id: variantId || `${productId}:${variantSku || variantName || productName}`,
            product_id: productId,
            variant_id: variantId,
            sku: variantSku,
            name: displayName,
            image_url: variantImageUrl,
            price: variantPrice,
            href: variantHref,
            quantity: 1,
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

        window.CartController.addItem(collectVariantPayload(variantItem));

        if (typeof window.CartController.openCart === "function") {
            window.CartController.openCart();
        }
    }

    document.addEventListener("click", handleAddVariant);
})();
