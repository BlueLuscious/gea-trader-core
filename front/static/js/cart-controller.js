(function () {
    "use strict";

    class CartController {
        constructor() {
            this.storageKey = "quote-cart-items";
            this.listeners = new Set();
        }

        init() {
            this.notify();
        }

        getStoredItems() {
            try {
                const raw = localStorage.getItem(this.storageKey);
                const parsed = raw ? JSON.parse(raw) : [];
                return Array.isArray(parsed) ? parsed : [];
            } catch (error) {
                return [];
            }
        }

        saveItems(items) {
            try {
                localStorage.setItem(this.storageKey, JSON.stringify(items));
            } catch (error) {
                // localStorage may be blocked by browser privacy settings.
            }
        }

        getItems() {
            return this.getStoredItems();
        }

        getItemId(item, index) {
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

        findItemIndex(items, itemId) {
            const targetId = String(itemId);
            return items.findIndex((item, index) => this.getItemId(item, index) === targetId);
        }

        getCount() {
            return this.getItems().reduce((total, item) => {
                const quantity = Number(item && item.quantity ? item.quantity : 1);
                return total + (Number.isFinite(quantity) ? quantity : 1);
            }, 0);
        }

        getState() {
            const items = this.getItems();
            return {
                items,
                count: this.getCount(),
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

        setItems(items) {
            const nextItems = Array.isArray(items) ? items : [];
            this.saveItems(nextItems);
            this.notify();
        }

        addItem(item) {
            const nextItem = item && typeof item === "object" ? item : {};
            const items = this.getItems();
            const incomingId = this.getItemId(nextItem, items.length);
            const existingIndex = this.findItemIndex(items, incomingId);

            if (existingIndex >= 0) {
                const currentItem = items[existingIndex];
                const currentQuantity = Number(currentItem && currentItem.quantity ? currentItem.quantity : 1) || 1;
                const nextQuantity = Number(nextItem && nextItem.quantity ? nextItem.quantity : 1) || 1;
                items[existingIndex] = {
                    ...currentItem,
                    ...nextItem,
                    quantity: currentQuantity + nextQuantity,
                };
            } else {
                items.push({
                    quantity: Number(nextItem.quantity || 1) || 1,
                    ...nextItem,
                });
            }

            this.setItems(items);
        }

        updateQuantity(itemId, quantity) {
            const nextQuantity = Math.max(0, Number(quantity) || 0);
            const items = this.getItems();
            const itemIndex = this.findItemIndex(items, itemId);
            if (itemIndex < 0) {
                return;
            }

            if (nextQuantity <= 0) {
                items.splice(itemIndex, 1);
            } else {
                items[itemIndex] = {
                    ...items[itemIndex],
                    quantity: nextQuantity,
                };
            }

            this.setItems(items);
        }

        incrementItem(itemId) {
            const items = this.getItems();
            const itemIndex = this.findItemIndex(items, itemId);
            if (itemIndex < 0) {
                return;
            }

            const currentQuantity = Number(items[itemIndex] && items[itemIndex].quantity ? items[itemIndex].quantity : 1) || 1;
            this.updateQuantity(itemId, currentQuantity + 1);
        }

        decrementItem(itemId) {
            const items = this.getItems();
            const itemIndex = this.findItemIndex(items, itemId);
            if (itemIndex < 0) {
                return;
            }

            const currentQuantity = Number(items[itemIndex] && items[itemIndex].quantity ? items[itemIndex].quantity : 1) || 1;
            this.updateQuantity(itemId, currentQuantity - 1);
        }

        removeItem(itemId) {
            const items = this.getItems();
            const itemIndex = this.findItemIndex(items, itemId);
            if (itemIndex < 0) {
                return;
            }

            items.splice(itemIndex, 1);
            this.setItems(items);
        }

        clear() {
            this.setItems([]);
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
