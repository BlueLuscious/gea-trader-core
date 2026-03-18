(function () {
    "use strict";

    class CartButtonController {
        constructor(root) {
            this.root = root;
            this.button = root.querySelector("[data-button]");
            this.countNode = root.querySelector("[data-cart-button-count]");
            this.unsubscribe = null;
        }

        mount() {
            if (!this.button || this.root.dataset.cartButtonInitialized === "true" || !window.CartController) {
                return;
            }

            if (window.GeaButton && typeof window.GeaButton.init === "function") {
                window.GeaButton.init(this.button);
            }

            this.button.addEventListener("click", (event) => this.handleClick(event));
            this.unsubscribe = window.CartController.subscribe((state) => this.sync(state));
            this.root.dataset.cartButtonInitialized = "true";
        }

        handleClick(event) {
            event.preventDefault();
            window.CartController.openCart();
        }

        sync(state) {
            const count = Number(state.count || 0);

            this.root.dataset.cartCount = String(count);
            this.button.setAttribute("aria-label", count > 0 ? `Abrir carrito (${count})` : "Abrir carrito");

            if (!this.countNode) {
                return;
            }

            this.countNode.textContent = String(count);
            this.countNode.classList.toggle("is-hidden", count <= 0);
            this.countNode.setAttribute("aria-hidden", count > 0 ? "false" : "true");
        }
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-cart-button-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const existingId = root.dataset.cartButtonId;
        if (existingId && registry.has(existingId)) {
            return registry.get(existingId);
        }

        const instance = new CartButtonController(root);
        instance.mount();

        if (existingId) {
            registry.set(existingId, instance);
        }

        return instance;
    }

    function initById(id) {
        return init(getRootById(id));
    }

    window.GeaCartButton = window.GeaCartButton || {
        init,
        initById,
        registry,
    };

    const pending = window.GeaCartButtonQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaCartButtonQueue = [];
})();
