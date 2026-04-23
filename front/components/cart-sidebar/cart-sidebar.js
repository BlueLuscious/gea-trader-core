(function () {
    "use strict";

    function getSiteShell() {
        return document.querySelector(".site-shell");
    }

    function getCartQuoteUrl() {
        const shell = getSiteShell();
        return shell ? shell.dataset.cartQuoteUrl || "" : "";
    }

    function getQuoteModalContentNode() {
        return document.querySelector("[data-quote-request-modal-content]");
    }

    function getCsrfToken() {
        const cookie = document.cookie
            .split(";")
            .map((item) => item.trim())
            .find((item) => item.startsWith("csrftoken="));
        if (!cookie) {
            return "";
        }

        return decodeURIComponent(cookie.slice("csrftoken=".length));
    }

    class CartSidebarController {
        constructor(root) {
            this.root = root;
            this.id = root.dataset.cartSidebarId || "";
            this.title = root.dataset.cartSidebarTitle || "Carrito";
            this.emptyTitle = root.dataset.cartSidebarEmptyTitle || "Tu carrito está vacío";
            this.emptyCopy = root.dataset.cartSidebarEmptyCopy || "Agregá productos para continuar.";
            this.sidebar = root.querySelector("[data-sidebar]");
            this.sidebarId = this.sidebar ? this.sidebar.dataset.sidebarId : "";
            this.itemsNode = root.querySelector("[data-cart-sidebar-items]");
            this.emptyNode = root.querySelector("[data-cart-sidebar-empty]");
            this.quoteModalId = root.dataset.quoteModalId || "";
            this.countNodes = root.querySelectorAll("[data-cart-sidebar-count]");
            this.unsubscribe = null;
            this.pendingQuantityAnimation = null;
            this.quoteModalContentNode = getQuoteModalContentNode();
            this.initialQuoteRequestMarkup = this.quoteModalContentNode ? this.quoteModalContentNode.innerHTML : "";
        }

        mount() {
            if (this.root.dataset.cartSidebarInitialized === "true" || !window.CartController) {
                return;
            }

            if (window.GeaSidebar && this.sidebarId) {
                window.GeaSidebar.initById(this.sidebarId);
            }

            this.root.addEventListener("click", (event) => this.handleAction(event));
            document.addEventListener("submit", (event) => this.handleSubmit(event));
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

        async handleAction(event) {
            const clearButton = event.target.closest("[data-cart-clear]");
            if (clearButton) {
                event.preventDefault();
                await window.CartController.clear();
                return;
            }

            const quoteButton = event.target.closest("[data-cart-quote]");
            if (quoteButton) {
                event.preventDefault();
                this.openQuoteRequest();
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
                await window.CartController.removeItem(itemId);
                return;
            }

            if (action === "increment") {
                this.pendingQuantityAnimation = { itemId, direction: "up" };
                await window.CartController.incrementItem(itemId);
                return;
            }

            if (action === "decrement") {
                this.pendingQuantityAnimation = { itemId, direction: "down" };
                await window.CartController.decrementItem(itemId);
            }
        }

        async openQuoteRequest() {
            if (!window.CartController || !window.CartController.getCount()) {
                return;
            }

            if (!this.quoteModalContentNode) {
                this.quoteModalContentNode = getQuoteModalContentNode();
            }

            if (this.quoteModalContentNode && !this.quoteModalContentNode.innerHTML.trim()) {
                this.restoreInitialQuoteRequestMarkup();
            }

            if (window.ModalController && this.quoteModalId) {
                window.ModalController.openById(this.quoteModalId);
            }
        }

        async submitQuoteRequest(form) {
            if (!form) {
                return;
            }

            const quoteUrl = getCartQuoteUrl();
            if (!this.quoteModalContentNode) {
                this.quoteModalContentNode = getQuoteModalContentNode();
            }

            if (!quoteUrl || !this.quoteModalContentNode) {
                return;
            }

            try {
                const response = await fetch(quoteUrl, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: new FormData(form),
                });
                const payload = await response.json();

                if (payload.success) {
                    this.restoreInitialQuoteRequestMarkup();
                    if (window.ModalController && this.quoteModalId) {
                        window.ModalController.closeById(this.quoteModalId);
                    }
                    if (payload.cart_state && window.CartController) {
                        window.CartController.setState(payload.cart_state);
                    } else if (window.CartController) {
                        await window.CartController.refresh();
                    }
                    if (window.ToastController && typeof window.ToastController.success === "function") {
                        window.ToastController.success({
                            title: "Solicitud enviada",
                            message: payload.message || "Recibimos tu pedido y lo vamos a revisar a la brevedad.",
                        });
                    }
                    return;
                }

                this.quoteModalContentNode.innerHTML = payload.form_html || "";
                if (window.ModalController && this.quoteModalId) {
                    window.ModalController.openById(this.quoteModalId);
                }
            } catch (error) {
                console.error("CartSidebarController: unable to submit quote request.", error);
                if (window.ToastController && typeof window.ToastController.danger === "function") {
                    window.ToastController.danger({
                        title: "No pudimos enviar la solicitud",
                        message: "Revisá tus datos y volvé a intentarlo en unos segundos.",
                    });
                }
            }
        }

        handleSubmit(event) {
            const quoteForm = event.target.closest("[data-cart-quote-form]");
            if (!quoteForm) {
                return;
            }

            event.preventDefault();
            this.submitQuoteRequest(quoteForm);
        }

        render(state) {
            const count = Number(state.count || 0);
            this.countNodes.forEach((node) => {
                node.textContent = String(count);
            });

            if (!this.itemsNode || !this.emptyNode) {
                return;
            }

            if (!count) {
                this.emptyNode.classList.remove("is-hidden");
                this.itemsNode.classList.add("is-hidden");
                this.itemsNode.innerHTML = "";
                this.restoreInitialQuoteRequestMarkup();
                if (window.ModalController && this.quoteModalId) {
                    window.ModalController.closeById(this.quoteModalId);
                }
                return;
            }

            this.emptyNode.classList.add("is-hidden");
            this.itemsNode.classList.remove("is-hidden");
            this.itemsNode.innerHTML = `${state && state.items_html ? state.items_html : ""}${state && state.summary_html ? state.summary_html : ""}`;
            this.applyPendingQuantityAnimation();
        }

        applyPendingQuantityAnimation() {
            if (!this.pendingQuantityAnimation || !this.itemsNode) {
                return;
            }

            const { itemId, direction } = this.pendingQuantityAnimation;
            this.pendingQuantityAnimation = null;
            window.requestAnimationFrame(() => {
                const itemNode = this.itemsNode.querySelector(`[data-cart-item-id="${CSS.escape(String(itemId))}"]`);
                if (!itemNode) {
                    return;
                }

                const buttonAction = direction === "up" ? "increment" : "decrement";
                const buttonNode = itemNode.querySelector(`[data-cart-action="${buttonAction}"]`);
                const qtyNode = itemNode.querySelector("[data-cart-qty-value]");

                if (buttonNode) {
                    buttonNode.classList.remove("is-bumping");
                    void buttonNode.offsetWidth;
                    buttonNode.classList.add("is-bumping");
                    window.setTimeout(() => {
                        buttonNode.classList.remove("is-bumping");
                    }, 360);
                }

                if (qtyNode) {
                    const className = direction === "up" ? "is-ticking-up" : "is-ticking-down";
                    qtyNode.classList.remove("is-ticking-up", "is-ticking-down");
                    void qtyNode.offsetWidth;
                    qtyNode.classList.add(className);
                    window.setTimeout(() => {
                        qtyNode.classList.remove(className);
                    }, 440);
                }

                itemNode.classList.remove("is-updating");
                void itemNode.offsetWidth;
                itemNode.classList.add("is-updating");
                window.setTimeout(() => {
                    itemNode.classList.remove("is-updating");
                }, 460);

                const mediaNode = itemNode.querySelector(".gc-cart-sidebar__item-media");
                if (mediaNode) {
                    mediaNode.animate(
                        [
                            { transform: "scale(1)", offset: 0 },
                            { transform: direction === "up" ? "scale(1.04)" : "scale(0.98)", offset: 0.45 },
                            { transform: "scale(1)", offset: 1 },
                        ],
                        {
                            duration: 420,
                            easing: "cubic-bezier(0.22, 1, 0.36, 1)",
                        }
                    );
                }
            });
        }

        restoreInitialQuoteRequestMarkup() {
            if (!this.quoteModalContentNode) {
                this.quoteModalContentNode = getQuoteModalContentNode();
            }

            if (this.quoteModalContentNode) {
                this.quoteModalContentNode.innerHTML = this.initialQuoteRequestMarkup;
            }
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
