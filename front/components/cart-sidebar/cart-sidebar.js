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

    class CartSidebarQuantityAnimator {
        constructor(itemsNode) {
            this.itemsNode = itemsNode;
            this.pendingAnimation = null;
        }

        queue(itemId, direction) {
            this.pendingAnimation = { itemId, direction };
        }

        apply() {
            if (!this.pendingAnimation || !this.itemsNode) {
                return;
            }

            const { itemId, direction } = this.pendingAnimation;
            this.pendingAnimation = null;
            window.requestAnimationFrame(() => {
                const itemNode = this.itemsNode.querySelector(`[data-cart-item-id="${CSS.escape(String(itemId))}"]`);
                if (!itemNode) {
                    return;
                }

                this.animateButton(itemNode, direction);
                this.animateQuantity(itemNode, direction);
                this.animateItem(itemNode);
                this.animateMedia(itemNode, direction);
            });
        }

        animateButton(itemNode, direction) {
            const buttonAction = direction === "up" ? "increment" : "decrement";
            const buttonNode = itemNode.querySelector(`[data-cart-action="${buttonAction}"]`);
            if (!buttonNode) {
                return;
            }

            buttonNode.classList.remove("is-bumping");
            void buttonNode.offsetWidth;
            buttonNode.classList.add("is-bumping");
            window.setTimeout(() => {
                buttonNode.classList.remove("is-bumping");
            }, 360);
        }

        animateQuantity(itemNode, direction) {
            const qtyNode = itemNode.querySelector("[data-cart-qty-value]");
            if (!qtyNode) {
                return;
            }

            const className = direction === "up" ? "is-ticking-up" : "is-ticking-down";
            qtyNode.classList.remove("is-ticking-up", "is-ticking-down");
            void qtyNode.offsetWidth;
            qtyNode.classList.add(className);
            window.setTimeout(() => {
                qtyNode.classList.remove(className);
            }, 440);
        }

        animateItem(itemNode) {
            itemNode.classList.remove("is-updating");
            void itemNode.offsetWidth;
            itemNode.classList.add("is-updating");
            window.setTimeout(() => {
                itemNode.classList.remove("is-updating");
            }, 460);
        }

        animateMedia(itemNode, direction) {
            const mediaNode = itemNode.querySelector(".gc-cart-sidebar__item-media");
            if (!mediaNode) {
                return;
            }

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
    }

    class CartQuoteRequestController {
        constructor(options) {
            this.modalId = options.modalId || "";
            this.getCartCount = options.getCartCount;
            this.contentNode = getQuoteModalContentNode();
            this.initialMarkup = this.contentNode ? this.contentNode.innerHTML : "";
        }

        mount() {
            document.addEventListener("submit", (event) => this.handleSubmit(event));
        }

        open() {
            if (typeof this.getCartCount === "function" && !this.getCartCount()) {
                return;
            }

            this.ensureContentNode();
            if (this.contentNode && !this.contentNode.innerHTML.trim()) {
                this.restoreInitialMarkup();
            }

            if (window.ModalController && this.modalId) {
                window.ModalController.openById(this.modalId);
            }
        }

        close() {
            if (window.ModalController && this.modalId) {
                window.ModalController.closeById(this.modalId);
            }
        }

        resetAndClose() {
            this.restoreInitialMarkup();
            this.close();
        }

        async submit(form) {
            if (!form) {
                return;
            }

            const quoteUrl = getCartQuoteUrl();
            this.ensureContentNode();
            if (!quoteUrl || !this.contentNode) {
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
                    await this.handleSuccess(payload);
                    return;
                }

                this.renderFormErrors(payload.form_html || "");
            } catch (error) {
                console.error("CartQuoteRequestController: unable to submit quote request.", error);
                if (window.ToastController && typeof window.ToastController.danger === "function") {
                    window.ToastController.danger({
                        title: "No pudimos enviar la solicitud",
                        message: "Revisá tus datos y volvé a intentarlo en unos segundos.",
                    });
                }
            }
        }

        async handleSuccess(payload) {
            this.restoreInitialMarkup();
            this.close();

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
        }

        renderFormErrors(formHtml) {
            if (this.contentNode) {
                this.contentNode.innerHTML = formHtml;
            }

            if (window.ModalController && this.modalId) {
                window.ModalController.openById(this.modalId);
            }
        }

        handleSubmit(event) {
            const quoteForm = event.target.closest("[data-cart-quote-form]");
            if (!quoteForm) {
                return;
            }

            event.preventDefault();
            this.submit(quoteForm);
        }

        restoreInitialMarkup() {
            this.ensureContentNode();
            if (this.contentNode) {
                this.contentNode.innerHTML = this.initialMarkup;
            }
        }

        ensureContentNode() {
            if (!this.contentNode) {
                this.contentNode = getQuoteModalContentNode();
            }
        }
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
            this.quantityAnimator = new CartSidebarQuantityAnimator(this.itemsNode);
            this.quoteRequestController = new CartQuoteRequestController({
                modalId: this.quoteModalId,
                getCartCount: () => window.CartController ? window.CartController.getCount() : 0,
            });
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
            this.quoteRequestController.mount();
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
                this.quoteRequestController.open();
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
                this.quantityAnimator.queue(itemId, "up");
                await window.CartController.incrementItem(itemId);
                return;
            }

            if (action === "decrement") {
                this.quantityAnimator.queue(itemId, "down");
                await window.CartController.decrementItem(itemId);
            }
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
                this.quoteRequestController.resetAndClose();
                return;
            }

            this.emptyNode.classList.add("is-hidden");
            this.itemsNode.classList.remove("is-hidden");
            this.itemsNode.innerHTML = `${state && state.items_html ? state.items_html : ""}${state && state.summary_html ? state.summary_html : ""}`;
            this.quantityAnimator.apply();
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
