(function () {
    "use strict";

    class ThemeButtonController {
        constructor(root) {
            this.root = root;
            this.button = root.querySelector("[data-button]");
            this.iconNode = root.querySelector("[data-theme-button-icon]");
            this.labelNode = root.querySelector("[data-theme-button-label]");
            this.intent = root.dataset.themeIntent || "toggle";
            this.unsubscribe = null;
        }

        mount() {
            if (!this.button || this.root.dataset.themeButtonInitialized === "true" || !window.ThemeController) {
                return;
            }

            if (window.GeaButton && typeof window.GeaButton.init === "function") {
                window.GeaButton.init(this.button);
            }

            this.button.addEventListener("click", () => this.handleClick());
            this.unsubscribe = window.ThemeController.subscribe((state) => this.sync(state));
            this.root.dataset.themeButtonInitialized = "true";
        }

        getNextTheme(state) {
            if (this.intent !== "toggle") {
                return this.intent;
            }

            if (state.selectedTheme === "system") {
                return "light";
            }

            return state.resolvedTheme === "dark" ? "light" : "dark";
        }

        sync(state) {
            const visualTheme = this.intent === "toggle" ? state.resolvedTheme : this.intent;
            const icon = this.root.dataset[`theme${capitalize(visualTheme)}Icon`] || "";
            const label = this.root.dataset[`theme${capitalize(visualTheme)}Label`] || visualTheme;

            if (this.iconNode) {
                setIconName(this.iconNode, icon);
            }

            if (this.labelNode) {
                this.labelNode.textContent = label;
            }

            const isActive = this.intent !== "toggle" && state.selectedTheme === this.intent;
            this.button.setAttribute("aria-pressed", isActive ? "true" : "false");
        }

        handleClick() {
            const state = window.ThemeController.getState();
            window.ThemeController.applyTheme(this.getNextTheme(state));
        }
    }

    function capitalize(value) {
        return value.charAt(0).toUpperCase() + value.slice(1);
    }

    function setIconName(wrapper, nextIconName) {
        if (!wrapper || !nextIconName) {
            return;
        }

        const iconNode = wrapper.querySelector(".gc-icon");
        const previousIconName = wrapper.dataset.themeButtonIconName;

        if (!iconNode) {
            return;
        }

        if (previousIconName) {
            iconNode.classList.remove(`fa-${previousIconName}`);
        }

        iconNode.classList.add(`fa-${nextIconName}`);
        wrapper.dataset.themeButtonIconName = nextIconName;
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-theme-button-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const existingId = root.dataset.themeButtonId;
        if (existingId && registry.has(existingId)) {
            return registry.get(existingId);
        }

        const instance = new ThemeButtonController(root);
        instance.mount();

        if (existingId) {
            registry.set(existingId, instance);
        }

        return instance;
    }

    function initById(id) {
        return init(getRootById(id));
    }

    window.GeaThemeButton = window.GeaThemeButton || {
        init,
        initById,
        registry,
    };

    const pending = window.GeaThemeButtonQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaThemeButtonQueue = [];
})();
