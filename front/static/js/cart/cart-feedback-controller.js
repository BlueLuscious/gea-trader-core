(function () {
    "use strict";

    function canToast(type) {
        return window.ToastController && typeof window.ToastController[type] === "function";
    }

    function showToast(type, options) {
        if (canToast(type)) {
            window.ToastController[type](options);
        }
    }

    function getFailureTitle(operation) {
        const titles = {
            add: "No pudimos agregar el producto",
            updateQuantity: "No pudimos actualizar la cantidad",
            remove: "No pudimos quitar el producto",
            clear: "No pudimos vaciar el carrito",
        };
        return titles[operation] || "No pudimos completar la acción";
    }

    class CartFeedbackController {
        init() {
            document.addEventListener("cartitemadded", (event) => this.handleItemAdded(event));
            document.addEventListener("cartitemremoved", () => this.handleItemRemoved());
            document.addEventListener("cartcleared", () => this.handleCartCleared());
            document.addEventListener("cartoperationfailed", (event) => this.handleOperationFailed(event));
        }

        handleItemAdded(event) {
            const productTitle = event.detail && event.detail.productTitle ? event.detail.productTitle : "";
            showToast("success", {
                title: "Producto agregado",
                message: productTitle
                    ? `${productTitle} ya está en tu carrito de cotización.`
                    : "El producto ya está en tu carrito de cotización.",
            });
        }

        handleItemRemoved() {
            showToast("info", {
                title: "Producto quitado",
                message: "El producto se eliminó del carrito de cotización.",
            });
        }

        handleCartCleared() {
            showToast("info", {
                title: "Carrito vaciado",
                message: "Quitamos todos los productos del carrito de cotización.",
            });
        }

        handleOperationFailed(event) {
            const detail = event.detail || {};
            showToast("danger", {
                title: getFailureTitle(detail.operation || ""),
                message: detail.message || "Volvé a intentarlo en unos segundos.",
            });
        }
    }

    if (!window.CartFeedbackController) {
        window.CartFeedbackController = new CartFeedbackController();
        window.CartFeedbackController.init();
    }
})();
