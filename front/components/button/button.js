(function () {
    "use strict";

    class ButtonController {
        constructor(root) {
            this.root = root;
            this.toggle = root.dataset.buttonToggle === "true";
        }

        mount() {
            if (this.root.dataset.buttonInitialized === "true") {
                return;
            }

            if (this.toggle && this.root.tagName === "BUTTON") {
                this.root.addEventListener("click", () => this.togglePressed());
            }

            this.root.dataset.buttonInitialized = "true";
        }

        togglePressed() {
            const nextPressed = this.root.getAttribute("aria-pressed") !== "true";
            this.root.setAttribute("aria-pressed", nextPressed ? "true" : "false");
        }
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-button-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const existingId = root.dataset.buttonId;
        if (existingId && registry.has(existingId)) {
            return registry.get(existingId);
        }

        const instance = new ButtonController(root);
        instance.mount();

        if (existingId) {
            registry.set(existingId, instance);
        }

        return instance;
    }

    function initById(id) {
        return init(getRootById(id));
    }

    window.GeaButton = window.GeaButton || {
        init,
        initById,
        registry,
    };

    const pending = window.GeaButtonQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaButtonQueue = [];
})();
