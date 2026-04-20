(function () {
    "use strict";

    class ProductCardController {
        constructor(root) {
            this.root = root;
            this.addButton = root.querySelector("[data-product-card-add]");
            this.handleAdd = this.handleAdd.bind(this);
        }

        init() {
            if (!this.addButton) {
                return;
            }

            this.addButton.addEventListener("click", this.handleAdd);
        }

        handleAdd(event) {
            event.preventDefault();

            if (!window.CartController || typeof window.CartController.addItem !== "function") {
                return;
            }

            const productId = this.root.dataset.productId || "";
            const title = this.root.dataset.productTitle || "";
            const brandName = this.root.dataset.productBrand || "";
            const imageUrl = this.root.dataset.productImageUrl || "";
            const priceValue = this.root.dataset.productPrice || "";
            const href = this.root.dataset.productHref || "";

            window.CartController.addItem({
                id: productId || title,
                product_id: productId,
                name: title,
                brand_name: brandName,
                image_url: imageUrl,
                price: priceValue,
                href,
                quantity: 1,
            });

            if (typeof window.CartController.openCart === "function") {
                window.CartController.openCart();
            }
        }
    }

    const registry = new Map();

    function init(root) {
        if (!root) {
            return null;
        }

        const id = root.dataset.productCardId;
        if (id && registry.has(id)) {
            return registry.get(id);
        }

        const controller = new ProductCardController(root);
        controller.init();

        if (id) {
            registry.set(id, controller);
        }

        return controller;
    }

    function initById(id) {
        if (!id) {
            return null;
        }

        const root = document.querySelector(`[data-product-card-id="${id}"]`);
        return init(root);
    }

    window.GeaProductCard = {
        init,
        initById,
    };

    const pending = window.GeaProductCardQueue || [];
    pending.splice(0).forEach((id) => initById(id));
})();
