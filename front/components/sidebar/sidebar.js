(function () {
    "use strict";

    function updateBodyState() {
        const hasOpenSidebar = Boolean(document.querySelector('[data-sidebar][data-sidebar-open="true"]'));
        document.body.classList.toggle("has-sidebar-open", hasOpenSidebar);
    }

    class SidebarController {
        constructor(root) {
            this.root = root;
            this.id = root.dataset.sidebarId || "";
            this.panel = root.querySelector("[data-sidebar-panel]");
            this.backdrop = root.querySelector("[data-sidebar-backdrop]");
            this.handleKeydown = this.handleKeydown.bind(this);
            this.handleDocumentEvent = this.handleDocumentEvent.bind(this);
        }

        mount() {
            if (this.root.dataset.sidebarInitialized === "true") {
                return;
            }

            if (this.backdrop) {
                this.backdrop.addEventListener("click", () => {
                    if (this.root.dataset.closeOnBackdrop === "true") {
                        this.close();
                    }
                });
            }

            this.root.addEventListener("click", (event) => {
                const closeTrigger = event.target.closest("[data-sidebar-close]");
                if (closeTrigger) {
                    event.preventDefault();
                    this.close();
                }
            });

            document.addEventListener("keydown", this.handleKeydown);
            document.addEventListener("sidebar:open", this.handleDocumentEvent);
            document.addEventListener("sidebar:close", this.handleDocumentEvent);
            document.addEventListener("sidebar:toggle", this.handleDocumentEvent);
            this.root.dataset.sidebarInitialized = "true";
            this.sync();
        }

        handleKeydown(event) {
            if (event.key !== "Escape" || this.root.dataset.closeOnEscape !== "true") {
                return;
            }

            if (this.root.dataset.sidebarOpen === "true") {
                this.close();
            }
        }

        handleDocumentEvent(event) {
            const detail = event.detail || {};
            if (!detail.id || detail.id !== this.id) {
                return;
            }

            if (event.type === "sidebar:open") {
                this.open();
                return;
            }

            if (event.type === "sidebar:close") {
                this.close();
                return;
            }

            this.toggle();
        }

        sync() {
            const isOpen = this.root.dataset.sidebarOpen === "true";
            if (this.panel) {
                this.panel.setAttribute("aria-hidden", isOpen ? "false" : "true");
            }
            updateBodyState();
        }

        setOpen(nextOpen) {
            this.root.dataset.sidebarOpen = nextOpen ? "true" : "false";
            this.sync();
            document.dispatchEvent(new CustomEvent("sidebarchange", {
                detail: { id: this.id, open: nextOpen },
            }));
        }

        open() {
            this.setOpen(true);
        }

        close() {
            this.setOpen(false);
        }

        toggle() {
            this.setOpen(this.root.dataset.sidebarOpen !== "true");
        }
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-sidebar-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const existingId = root.dataset.sidebarId;
        if (existingId && registry.has(existingId)) {
            return registry.get(existingId);
        }

        const instance = new SidebarController(root);
        instance.mount();

        if (existingId) {
            registry.set(existingId, instance);
        }

        return instance;
    }

    function initById(id) {
        return init(getRootById(id));
    }

    function openById(id) {
        const instance = initById(id);
        if (instance) {
            instance.open();
        }
        return instance;
    }

    function closeById(id) {
        const instance = initById(id);
        if (instance) {
            instance.close();
        }
        return instance;
    }

    function toggleById(id) {
        const instance = initById(id);
        if (instance) {
            instance.toggle();
        }
        return instance;
    }

    window.GeaSidebar = window.GeaSidebar || {
        init,
        initById,
        openById,
        closeById,
        toggleById,
        registry,
    };

    if (!window.GeaSidebarTriggerBound) {
        document.addEventListener("click", (event) => {
            const openTrigger = event.target.closest("[data-sidebar-open-target]");
            if (openTrigger) {
                event.preventDefault();
                openById(openTrigger.dataset.sidebarOpenTarget);
                return;
            }

            const closeTrigger = event.target.closest("[data-sidebar-close-target]");
            if (closeTrigger) {
                event.preventDefault();
                closeById(closeTrigger.dataset.sidebarCloseTarget);
                return;
            }

            const toggleTrigger = event.target.closest("[data-sidebar-toggle-target]");
            if (toggleTrigger) {
                event.preventDefault();
                toggleById(toggleTrigger.dataset.sidebarToggleTarget);
            }
        });
        window.GeaSidebarTriggerBound = true;
    }

    const pending = window.GeaSidebarQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaSidebarQueue = [];
})();
