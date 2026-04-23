(function () {
    "use strict";

    class ProductCardController {
        constructor(root) {
            this.root = root;
            this.addButton = root.querySelector("[data-product-card-add]");
            this.handleAdd = this.handleAdd.bind(this);
        }

        init() {
            if (this.addButton) {
                this.addButton.addEventListener("click", this.handleAdd);
            }
        }

        handleAdd(event) {
            event.preventDefault();

            if (!window.CartController || typeof window.CartController.addItem !== "function") {
                return;
            }

            const productId = this.root.dataset.productId || "";
            const productTitle = this.root.dataset.productTitle || "";
            window.CartController.addItem({
                product_id: productId,
                quantity: 1,
                product_title: productTitle,
            });
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
