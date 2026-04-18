(function () {
    "use strict";

    class SwitchController {
        constructor(root) {
            this.root = root;
            this.input = root.querySelector("[data-switch-input]");
        }

        mount() {
            if (!this.input || this.root.dataset.switchInitialized === "true") {
                return;
            }

            this.sync();
            this.input.addEventListener("change", () => this.sync());
            this.root.dataset.switchInitialized = "true";
        }

        sync() {
            this.root.dataset.switchChecked = this.input.checked ? "true" : "false";
        }
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-switch-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const existingId = root.dataset.switchId;
        if (existingId && registry.has(existingId)) {
            return registry.get(existingId);
        }

        const instance = new SwitchController(root);
        instance.mount();

        if (existingId) {
            registry.set(existingId, instance);
        }

        return instance;
    }

    function initById(id) {
        return init(getRootById(id));
    }

    window.GeaSwitch = window.GeaSwitch || {
        init,
        initById,
        registry,
    };

    const pending = window.GeaSwitchQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaSwitchQueue = [];
})();
