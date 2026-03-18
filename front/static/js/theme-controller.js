(function () {
    "use strict";

    class ThemeController {
        constructor() {
            this.storageKey = "site-theme";
            this.root = document.documentElement;
            this.mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
            this.listeners = new Set();

            this.handleControlEvent = this.handleControlEvent.bind(this);
            this.handleSystemThemeChange = this.handleSystemThemeChange.bind(this);
        }

        init() {
            this.applyTheme(this.getSelectedTheme(), { persist: false });
            document.addEventListener("change", this.handleControlEvent);
            document.addEventListener("click", this.handleControlEvent);
            this.mediaQuery.addEventListener("change", this.handleSystemThemeChange);
        }

        normalizeTheme(theme) {
            if (theme === "light" || theme === "dark" || theme === "system") {
                return theme;
            }

            return "system";
        }

        getStoredTheme() {
            try {
                return localStorage.getItem(this.storageKey);
            } catch (error) {
                return null;
            }
        }

        saveTheme(theme) {
            try {
                localStorage.setItem(this.storageKey, theme);
            } catch (error) {
                // localStorage may be blocked by browser privacy settings.
            }
        }

        resolveTheme(theme) {
            if (theme === "light" || theme === "dark") {
                return theme;
            }

            return this.mediaQuery.matches ? "dark" : "light";
        }

        getSelectedTheme() {
            return this.normalizeTheme(
                this.root.getAttribute("data-theme-selected") || this.getStoredTheme() || "system"
            );
        }

        getResolvedTheme() {
            return this.resolveTheme(this.getSelectedTheme());
        }

        applyTheme(theme, options = {}) {
            const persist = options.persist !== false;
            const selectedTheme = this.normalizeTheme(theme);
            const resolvedTheme = this.resolveTheme(selectedTheme);

            this.root.setAttribute("data-theme-selected", selectedTheme);
            this.root.setAttribute("data-theme", resolvedTheme);
            this.root.style.colorScheme = resolvedTheme;

            if (persist) {
                this.saveTheme(selectedTheme);
            }

            this.syncControls();
            this.notify();
        }

        subscribe(listener) {
            this.listeners.add(listener);
            listener(this.getState());

            return () => {
                this.listeners.delete(listener);
            };
        }

        getState() {
            return {
                selectedTheme: this.getSelectedTheme(),
                resolvedTheme: this.getResolvedTheme(),
            };
        }

        notify() {
            const detail = this.getState();

            this.listeners.forEach((listener) => listener(detail));
            document.dispatchEvent(new CustomEvent("themechange", { detail }));
        }

        syncControls() {
            const selectedTheme = this.getSelectedTheme();
            const resolvedTheme = this.getResolvedTheme();

            document.querySelectorAll("[data-theme-control]").forEach((control) => {
                this.syncControl(control, selectedTheme, resolvedTheme);
            });
        }

        syncControl(control, selectedTheme, resolvedTheme) {
            if (control.tagName === "SELECT") {
                control.value = selectedTheme;
                return;
            }

            if (control.matches('input[type="checkbox"]')) {
                const activeTheme = this.normalizeTheme(control.dataset.themeActiveValue || "dark");
                control.checked = resolvedTheme === activeTheme;
                control.setAttribute("aria-checked", control.checked ? "true" : "false");
                return;
            }

            const themeValue = this.normalizeTheme(control.dataset.themeValue);
            const isActive = themeValue === selectedTheme || (themeValue !== "system" && themeValue === resolvedTheme);
            control.setAttribute("aria-pressed", isActive ? "true" : "false");
            control.dataset.themeActive = isActive ? "true" : "false";
        }

        handleControlEvent(event) {
            const control = event.target.closest("[data-theme-control]");
            if (!control) {
                return;
            }

            if (control.tagName === "SELECT") {
                this.applyTheme(control.value);
                return;
            }

            if (control.matches('input[type="checkbox"]')) {
                const activeTheme = this.normalizeTheme(control.dataset.themeActiveValue || "dark");
                const inactiveTheme = this.normalizeTheme(control.dataset.themeInactiveValue || "light");
                this.applyTheme(control.checked ? activeTheme : inactiveTheme);
                return;
            }

            const nextTheme = this.normalizeTheme(control.dataset.themeValue);
            this.applyTheme(nextTheme);
        }

        handleSystemThemeChange() {
            if (this.getSelectedTheme() === "system") {
                this.applyTheme("system", { persist: false });
            }
        }
    }

    if (!window.ThemeController) {
        window.ThemeController = new ThemeController();
        window.ThemeController.init();
    }
})();
