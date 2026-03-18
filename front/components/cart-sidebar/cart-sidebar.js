(function () {
    "use strict";

    function getItemKey(item, index) {
        if (item && item.id !== undefined && item.id !== null && item.id !== "") {
            return String(item.id);
        }

        if (item && item.product_id !== undefined && item.product_id !== null && item.product_id !== "") {
            return String(item.product_id);
        }

        if (item && item.sku) {
            return String(item.sku);
        }

        return String(index);
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function formatCurrency(value) {
        const amount = Number(value);
        if (!Number.isFinite(amount)) {
            return "";
        }

        return new Intl.NumberFormat("es-AR", {
            style: "currency",
            currency: "ARS",
            maximumFractionDigits: 0,
        }).format(amount);
    }

    class CartSidebarController {
        constructor(root) {
            this.root = root;
            this.id = root.dataset.cartSidebarId || "";
            this.title = root.dataset.cartSidebarTitle || "Carrito";
            this.emptyTitle = root.dataset.cartSidebarEmptyTitle || "Tu carrito esta vacio";
            this.emptyCopy = root.dataset.cartSidebarEmptyCopy || "Agrega productos para continuar.";
            this.sidebar = root.querySelector("[data-sidebar]");
            this.sidebarId = this.sidebar ? this.sidebar.dataset.sidebarId : "";
            this.itemsNode = root.querySelector("[data-cart-sidebar-items]");
            this.emptyNode = root.querySelector("[data-cart-sidebar-empty]");
            this.countNodes = root.querySelectorAll("[data-cart-sidebar-count]");
            this.unsubscribe = null;
        }

        mount() {
            if (this.root.dataset.cartSidebarInitialized === "true" || !window.CartController) {
                return;
            }

            if (window.GeaSidebar && this.sidebarId) {
                window.GeaSidebar.initById(this.sidebarId);
            }

            this.root.addEventListener("click", (event) => this.handleAction(event));
            document.addEventListener("cartopen", () => this.open());
            document.addEventListener("cartchange", (event) => this.render(event.detail || { items: [], count: 0 }));
            this.unsubscribe = window.CartController.subscribe((state) => this.render(state));
            this.root.dataset.cartSidebarInitialized = "true";
        }

        open() {
            if (window.GeaSidebar && this.sidebarId) {
                window.GeaSidebar.openById(this.sidebarId);
            }
        }

        handleAction(event) {
            const clearButton = event.target.closest("[data-cart-clear]");
            if (clearButton) {
                event.preventDefault();
                window.CartController.clear();
                return;
            }

            const quoteButton = event.target.closest("[data-cart-quote]");
            if (quoteButton) {
                event.preventDefault();
                document.dispatchEvent(new CustomEvent("cartquote", {
                    detail: window.CartController.getState(),
                }));
                return;
            }

            const actionButton = event.target.closest("[data-cart-action]");
            if (!actionButton) {
                return;
            }

            event.preventDefault();
            const itemId = actionButton.dataset.itemId;
            const action = actionButton.dataset.cartAction;
            if (!itemId || !action) {
                return;
            }

            if (action === "remove") {
                window.CartController.removeItem(itemId);
                return;
            }

            if (action === "increment") {
                window.CartController.incrementItem(itemId);
                return;
            }

            if (action === "decrement") {
                window.CartController.decrementItem(itemId);
            }
        }

        render(state) {
            const count = Number(state.count || 0);
            const items = Array.isArray(state.items) ? state.items : [];
            this.countNodes.forEach((node) => {
                node.textContent = String(count);
            });

            if (!this.itemsNode || !this.emptyNode) {
                return;
            }

            if (!items.length) {
                this.emptyNode.classList.remove("is-hidden");
                this.itemsNode.classList.add("is-hidden");
                this.itemsNode.innerHTML = "";
                return;
            }

            this.emptyNode.classList.add("is-hidden");
            this.itemsNode.classList.remove("is-hidden");

            const subtotal = items.reduce((total, item) => {
                const quantity = Number(item && item.quantity ? item.quantity : 1);
                const price = Number(item && item.price ? item.price : 0);
                return total + (Number.isFinite(quantity) ? quantity : 1) * (Number.isFinite(price) ? price : 0);
            }, 0);

            const itemsMarkup = items.map((item, index) => {
                const itemId = getItemKey(item, index);
                const quantity = Math.max(1, Number(item && item.quantity ? item.quantity : 1) || 1);
                const title = item && (item.title || item.name || item.label) ? (item.title || item.name || item.label) : `Producto ${index + 1}`;
                const meta = item && (item.sku || item.subtitle || item.description) ? (item.sku || item.subtitle || item.description) : "";
                const price = formatCurrency(item && item.price ? item.price : 0);

                return `
                    <article class="gc-cart-sidebar__item">
                        <div class="gc-cart-sidebar__item-head">
                            <p class="gc-cart-sidebar__item-title">${escapeHtml(title)}</p>
                            ${meta ? `<p class="gc-cart-sidebar__item-meta">${escapeHtml(meta)}</p>` : ""}
                            ${price ? `<p class="gc-cart-sidebar__item-price">${escapeHtml(price)}</p>` : ""}
                        </div>
                        <div class="gc-cart-sidebar__item-actions">
                            <div class="gc-cart-sidebar__qty-controls" aria-label="Cantidad">
                                <button
                                    type="button"
                                    class="gc-cart-sidebar__qty-button"
                                    data-cart-action="decrement"
                                    data-item-id="${escapeHtml(itemId)}"
                                >-</button>
                                <span class="gc-cart-sidebar__qty">${escapeHtml(quantity)}</span>
                                <button
                                    type="button"
                                    class="gc-cart-sidebar__qty-button"
                                    data-cart-action="increment"
                                    data-item-id="${escapeHtml(itemId)}"
                                >+</button>
                            </div>
                            <button
                                type="button"
                                class="gc-cart-sidebar__remove"
                                data-cart-action="remove"
                                data-item-id="${escapeHtml(itemId)}"
                            >Quitar</button>
                        </div>
                    </article>
                `;
            }).join("");

            const summaryMarkup = `
                <section class="gc-cart-sidebar__summary">
                    <div class="gc-cart-sidebar__summary-row">
                        <p class="gc-cart-sidebar__summary-label">Items</p>
                        <p class="gc-cart-sidebar__summary-value">${escapeHtml(count)}</p>
                    </div>
                    <div class="gc-cart-sidebar__summary-row">
                        <p class="gc-cart-sidebar__summary-label">Subtotal estimado</p>
                        <p class="gc-cart-sidebar__summary-value">${escapeHtml(formatCurrency(subtotal) || "-")}</p>
                    </div>
                </section>
            `;

            this.itemsNode.innerHTML = itemsMarkup + summaryMarkup;
        }
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-cart-sidebar-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const existingId = root.dataset.cartSidebarId;
        if (existingId && registry.has(existingId)) {
            return registry.get(existingId);
        }

        const instance = new CartSidebarController(root);
        instance.mount();

        if (existingId) {
            registry.set(existingId, instance);
        }

        return instance;
    }

    function initById(id) {
        return init(getRootById(id));
    }

    window.GeaCartSidebar = window.GeaCartSidebar || {
        init,
        initById,
        registry,
    };

    const pending = window.GeaCartSidebarQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaCartSidebarQueue = [];
})();
