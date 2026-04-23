(function () {
    "use strict";

    function getSiteShell() {
        return document.querySelector(".site-shell");
    }

    function getCookie(name) {
        const cookie = document.cookie
            .split(";")
            .map((item) => item.trim())
            .find((item) => item.startsWith(`${name}=`));
        if (!cookie) {
            return "";
        }

        return decodeURIComponent(cookie.slice(name.length + 1));
    }

    class CartController {
        constructor() {
            this.listeners = new Set();
            this.state = {
                cart_id: null,
                status: "",
                items: [],
                count: 0,
                items_html: "",
                summary_html: "",
            };
        }

        init() {
            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", () => {
                    this.refresh();
                }, { once: true });
                return;
            }

            this.refresh();
        }

        getUrls() {
            const shell = getSiteShell();
            return {
                state: shell ? shell.dataset.cartStateUrl || "" : "",
                add: shell ? shell.dataset.cartAddUrl || "" : "",
                updateQuantity: shell ? shell.dataset.cartUpdateQuantityUrl || "" : "",
                remove: shell ? shell.dataset.cartRemoveUrl || "" : "",
                clear: shell ? shell.dataset.cartClearUrl || "" : "",
            };
        }

        getItems() {
            return Array.isArray(this.state.items) ? this.state.items : [];
        }

        getCount() {
            return Number(this.state.count || 0);
        }

        getState() {
            return {
                ...this.state,
                items: this.getItems(),
                count: this.getCount(),
                items_html: this.state.items_html || "",
                summary_html: this.state.summary_html || "",
            };
        }

        subscribe(listener) {
            this.listeners.add(listener);
            listener(this.getState());

            return () => {
                this.listeners.delete(listener);
            };
        }

        notify() {
            const detail = this.getState();
            this.listeners.forEach((listener) => listener(detail));
            document.dispatchEvent(new CustomEvent("cartchange", { detail }));
        }

        setState(nextState) {
            this.state = {
                cart_id: nextState && nextState.cart_id ? nextState.cart_id : null,
                status: nextState && nextState.status ? nextState.status : "",
                items: Array.isArray(nextState && nextState.items) ? nextState.items : [],
                count: Number(nextState && nextState.count ? nextState.count : 0),
                items_html: nextState && nextState.items_html ? nextState.items_html : "",
                summary_html: nextState && nextState.summary_html ? nextState.summary_html : "",
            };
            this.notify();
        }

        async request(url, payload) {
            if (!url) {
                console.error("CartController: missing runtime URL.");
                return this.getState();
            }

            const response = await fetch(url, {
                method: payload ? "POST" : "GET",
                headers: payload ? {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                } : {},
                credentials: "same-origin",
                body: payload ? JSON.stringify(payload) : undefined,
            });

            if (!response.ok) {
                let errorMessage = `Cart request failed with status ${response.status}`;
                try {
                    const errorPayload = await response.json();
                    if (errorPayload && errorPayload.error) {
                        errorMessage = String(errorPayload.error);
                    }
                } catch (error) {
                    // Keep the generic message when the response is not JSON.
                }
                console.error("CartController: request failed.", {
                    url,
                    status: response.status,
                    statusText: response.statusText,
                });
                throw new Error(errorMessage);
            }

            const nextState = await response.json();
            this.setState(nextState);
            return this.getState();
        }

        async refresh() {
            try {
                return await this.request(this.getUrls().state);
            } catch (error) {
                console.error("CartController: unable to refresh cart state.", error);
                return this.getState();
            }
        }

        async addItem(item) {
            const nextItem = item && typeof item === "object" ? item : {};
            if (!nextItem.product_id) {
                return this.getState();
            }

            try {
                const nextState = await this.request(this.getUrls().add, {
                    product_id: nextItem.product_id,
                    variant_id: nextItem.variant_id || "",
                    quantity: nextItem.quantity || 1,
                });
                document.dispatchEvent(new CustomEvent("cartitemadded", {
                    detail: {
                        productTitle: nextItem.product_title || "",
                        count: this.getCount(),
                    },
                }));
                if (window.ToastController && typeof window.ToastController.success === "function") {
                    window.ToastController.success({
                        title: "Producto agregado",
                        message: nextItem.product_title
                            ? `${nextItem.product_title} ya está en tu carrito de cotización.`
                            : "El producto ya está en tu carrito de cotización.",
                    });
                }
                return nextState;
            } catch (error) {
                console.error("CartController: unable to add item.", error);
                if (window.ToastController && typeof window.ToastController.danger === "function") {
                    window.ToastController.danger({
                        title: "No pudimos agregar el producto",
                        message: error && error.message ? error.message : "Volvé a intentarlo en unos segundos.",
                    });
                }
                return this.getState();
            }
        }

        async updateQuantity(itemId, quantity) {
            if (!itemId) {
                return this.getState();
            }

            try {
                return await this.request(this.getUrls().updateQuantity, {
                    item_id: itemId,
                    quantity,
                });
            } catch (error) {
                console.error("CartController: unable to update quantity.", error);
                return this.getState();
            }
        }

        async incrementItem(itemId) {
            const currentItem = this.getItems().find((item) => String(item.id) === String(itemId));
            const currentQuantity = Number(currentItem && currentItem.quantity ? currentItem.quantity : 1) || 1;
            return this.updateQuantity(itemId, currentQuantity + 1);
        }

        async decrementItem(itemId) {
            const currentItem = this.getItems().find((item) => String(item.id) === String(itemId));
            const currentQuantity = Number(currentItem && currentItem.quantity ? currentItem.quantity : 1) || 1;
            return this.updateQuantity(itemId, currentQuantity - 1);
        }

        async removeItem(itemId) {
            if (!itemId) {
                return this.getState();
            }

            try {
                const nextState = await this.request(this.getUrls().remove, {
                    item_id: itemId,
                });
                if (window.ToastController && typeof window.ToastController.info === "function") {
                    window.ToastController.info({
                        title: "Producto quitado",
                        message: "El producto se eliminó del carrito de cotización.",
                    });
                }
                return nextState;
            } catch (error) {
                console.error("CartController: unable to remove item.", error);
                if (window.ToastController && typeof window.ToastController.danger === "function") {
                    window.ToastController.danger({
                        title: "No pudimos quitar el producto",
                        message: error && error.message ? error.message : "Volvé a intentarlo en unos segundos.",
                    });
                }
                return this.getState();
            }
        }

        async clear() {
            try {
                const hadItems = this.getCount() > 0;
                const nextState = await this.request(this.getUrls().clear, {});
                if (hadItems && window.ToastController && typeof window.ToastController.info === "function") {
                    window.ToastController.info({
                        title: "Carrito vaciado",
                        message: "Quitamos todos los productos del carrito de cotización.",
                    });
                }
                return nextState;
            } catch (error) {
                console.error("CartController: unable to clear cart.", error);
                if (window.ToastController && typeof window.ToastController.danger === "function") {
                    window.ToastController.danger({
                        title: "No pudimos vaciar el carrito",
                        message: error && error.message ? error.message : "Volvé a intentarlo en unos segundos.",
                    });
                }
                return this.getState();
            }
        }

        openCart() {
            document.dispatchEvent(new CustomEvent("cartopen", { detail: this.getState() }));
        }
    }

    if (!window.CartController) {
        window.CartController = new CartController();
        window.CartController.init();
    }
})();
