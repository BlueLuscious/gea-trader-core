(function () {
    "use strict";

    class ThemeSwitchController {
        constructor(root) {
            this.root = root;
            this.input = root.querySelector("[data-switch-input]");
            this.unsubscribe = null;
        }

        mount() {
            if (!this.input || this.root.dataset.themeSwitchInitialized === "true" || !window.ThemeController) {
                return;
            }

            if (window.GeaSwitch && typeof window.GeaSwitch.init === "function") {
                window.GeaSwitch.init(this.root.querySelector("[data-switch]") || this.root.querySelector(".gc-switch"));
            }

            this.input.addEventListener("change", () => this.handleChange());
            this.unsubscribe = window.ThemeController.subscribe((state) => this.sync(state));
            this.root.dataset.themeSwitchInitialized = "true";
        }

        sync(state) {
            this.input.checked = state.resolvedTheme === "dark";
            this.input.setAttribute("aria-checked", this.input.checked ? "true" : "false");
            this.root.dataset.themeResolved = state.resolvedTheme;
        }

        handleChange() {
            window.ThemeController.applyTheme(this.input.checked ? "dark" : "light");
        }
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-theme-switch-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const existingId = root.dataset.themeSwitchId;
        if (existingId && registry.has(existingId)) {
            return registry.get(existingId);
        }

        const instance = new ThemeSwitchController(root);
        instance.mount();

        if (existingId) {
            registry.set(existingId, instance);
        }

        return instance;
    }

    function initById(id) {
        return init(getRootById(id));
    }

    window.GeaThemeSwitch = window.GeaThemeSwitch || {
        init,
        initById,
        registry,
    };

    const pending = window.GeaThemeSwitchQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaThemeSwitchQueue = [];
})();
