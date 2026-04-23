(function () {
    "use strict";

    const DEFAULT_VARIANT = "info";
    const DEFAULT_AUTO_CLOSE_MS = 4200;
    const DEFAULT_TITLE_BY_VARIANT = {
        info: "Aviso",
        success: "Listo",
        warning: "Atención",
        danger: "No pudimos completar la acción",
        accent: "Actualización",
    };
    const DEFAULT_ICON_BY_VARIANT = {
        info: "fa-solid fa-circle-info",
        success: "fa-solid fa-circle-check",
        warning: "fa-solid fa-triangle-exclamation",
        danger: "fa-solid fa-circle-xmark",
        accent: "fa-solid fa-sparkles",
    };
    const LEAVE_DURATION_MS = 220;

    class ToastRuntime {
        constructor(root) {
            this.root = root;
            this.id = root.dataset.toastId || "";
            this.maxVisible = Math.max(Number(root.dataset.toastMaxVisible || 4), 1);
            this.autoCloseMs = Math.max(Number(root.dataset.toastAutoCloseMs || DEFAULT_AUTO_CLOSE_MS), 1);
            this.template = root.nextElementSibling && root.nextElementSibling.matches("[data-toast-template]")
                ? root.nextElementSibling
                : document.querySelector("[data-toast-template]");
        }

        show(options) {
            if (!this.template) {
                return null;
            }

            const payload = options && typeof options === "object" ? options : {};
            const variant = payload.variant || DEFAULT_VARIANT;
            const item = this.template.content.firstElementChild.cloneNode(true);
            const iconNode = item.querySelector("[data-toast-icon]");
            const titleNode = item.querySelector("[data-toast-title]");
            const messageNode = item.querySelector("[data-toast-message]");
            const dismissButton = item.querySelector("[data-toast-dismiss]");
            const iconClassName = payload.iconClassName || DEFAULT_ICON_BY_VARIANT[variant] || DEFAULT_ICON_BY_VARIANT.info;

            item.classList.remove("gc-toast__item--info");
            item.classList.add(`gc-toast__item--${variant}`);

            if (iconNode) {
                iconNode.innerHTML = `<i class="${iconClassName}" aria-hidden="true"></i>`;
            }

            if (titleNode) {
                titleNode.textContent = payload.title || DEFAULT_TITLE_BY_VARIANT[variant] || DEFAULT_TITLE_BY_VARIANT.info;
            }

            if (messageNode) {
                messageNode.textContent = payload.message || "";
                messageNode.hidden = !payload.message;
            }

            if (dismissButton) {
                dismissButton.addEventListener("click", () => this.dismiss(item));
            }

            this.root.prepend(item);
            requestAnimationFrame(() => {
                item.classList.add("is-visible");
            });

            while (this.root.children.length > this.maxVisible) {
                this.dismiss(this.root.lastElementChild, true);
            }

            const autoCloseMs = Number(payload.autoCloseMs || this.autoCloseMs);
            if (autoCloseMs > 0) {
                window.setTimeout(() => this.dismiss(item), autoCloseMs);
            }

            return item;
        }

        dismiss(item, immediate) {
            if (!item || !item.parentElement) {
                return;
            }

            if (immediate) {
                item.remove();
                return;
            }

            if (item.dataset.toastLeaving === "true") {
                return;
            }

            item.dataset.toastLeaving = "true";
            item.classList.remove("is-visible");
            item.classList.add("is-leaving");
            window.setTimeout(() => {
                item.remove();
            }, LEAVE_DURATION_MS);
        }
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-toast-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const id = root.dataset.toastId;
        if (id && registry.has(id)) {
            return registry.get(id);
        }

        const runtime = new ToastRuntime(root);
        if (id) {
            registry.set(id, runtime);
        }

        return runtime;
    }

    function initById(id) {
        return init(getRootById(id));
    }

    function getDefaultRuntime() {
        const existingRuntime = registry.values().next().value;
        if (existingRuntime) {
            return existingRuntime;
        }

        const root = document.querySelector("[data-toast]");
        return root ? init(root) : null;
    }

    function show(options) {
        const runtime = getDefaultRuntime();
        return runtime ? runtime.show(options) : null;
    }

    function showVariant(variant, options) {
        return show({ ...(options || {}), variant });
    }

    window.ToastController = window.ToastController || {
        init,
        initById,
        show,
        info(options) {
            return showVariant("info", options);
        },
        success(options) {
            return showVariant("success", options);
        },
        warning(options) {
            return showVariant("warning", options);
        },
        danger(options) {
            return showVariant("danger", options);
        },
        accent(options) {
            return showVariant("accent", options);
        },
    };

    function initExistingToasts() {
        document.querySelectorAll("[data-toast]").forEach((root) => {
            init(root);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initExistingToasts, { once: true });
    } else {
        initExistingToasts();
    }

    const pending = window.GeaToastQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaToastQueue = [];
})();
