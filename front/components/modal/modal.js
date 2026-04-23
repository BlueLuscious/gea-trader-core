(function () {
    "use strict";

    function updateBodyState() {
        const hasOpenModal = Boolean(document.querySelector('[data-modal][data-modal-open="true"]'));
        document.body.classList.toggle("has-modal-open", hasOpenModal);
    }

    class ModalRuntime {
        constructor(root) {
            this.root = root;
            this.id = root.dataset.modalId || "";
            this.panel = root.querySelector("[data-modal-panel]");
            this.backdrop = root.querySelector("[data-modal-backdrop]");
            this.handleKeydown = this.handleKeydown.bind(this);
            this.handleDocumentEvent = this.handleDocumentEvent.bind(this);
        }

        mount() {
            if (this.root.dataset.modalInitialized === "true") {
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
                const closeTrigger = event.target.closest("[data-modal-close]");
                if (closeTrigger) {
                    event.preventDefault();
                    this.close();
                }
            });

            document.addEventListener("keydown", this.handleKeydown);
            document.addEventListener("modal:open", this.handleDocumentEvent);
            document.addEventListener("modal:close", this.handleDocumentEvent);
            document.addEventListener("modal:toggle", this.handleDocumentEvent);
            this.root.dataset.modalInitialized = "true";
            this.sync();
        }

        handleKeydown(event) {
            if (event.key !== "Escape" || this.root.dataset.closeOnEscape !== "true") {
                return;
            }

            if (this.root.dataset.modalOpen === "true") {
                this.close();
            }
        }

        handleDocumentEvent(event) {
            const detail = event.detail || {};
            if (!detail.id || detail.id !== this.id) {
                return;
            }

            if (event.type === "modal:open") {
                this.open();
                return;
            }

            if (event.type === "modal:close") {
                this.close();
                return;
            }

            this.toggle();
        }

        sync() {
            const isOpen = this.root.dataset.modalOpen === "true";
            if (this.panel) {
                this.panel.setAttribute("aria-hidden", isOpen ? "false" : "true");
            }
            updateBodyState();
        }

        setOpen(nextOpen) {
            this.root.dataset.modalOpen = nextOpen ? "true" : "false";
            this.sync();
            document.dispatchEvent(new CustomEvent("modalchange", {
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
            this.setOpen(this.root.dataset.modalOpen !== "true");
        }
    }

    const registry = new Map();

    function getRootById(id) {
        if (!id) {
            return null;
        }

        return document.querySelector(`[data-modal-id="${CSS.escape(id)}"]`);
    }

    function init(root) {
        if (!root) {
            return null;
        }

        const existingId = root.dataset.modalId;
        if (existingId && registry.has(existingId)) {
            return registry.get(existingId);
        }

        const instance = new ModalRuntime(root);
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

    window.ModalController = window.ModalController || {
        init,
        initById,
        openById,
        closeById,
        toggleById,
        registry,
    };

    if (!window.GeaModalTriggerBound) {
        document.addEventListener("click", (event) => {
            const openTrigger = event.target.closest("[data-modal-open-target]");
            if (openTrigger) {
                event.preventDefault();
                openById(openTrigger.dataset.modalOpenTarget);
                return;
            }

            const closeTrigger = event.target.closest("[data-modal-close-target]");
            if (closeTrigger) {
                event.preventDefault();
                closeById(closeTrigger.dataset.modalCloseTarget);
                return;
            }

            const toggleTrigger = event.target.closest("[data-modal-toggle-target]");
            if (toggleTrigger) {
                event.preventDefault();
                toggleById(toggleTrigger.dataset.modalToggleTarget);
            }
        });
        window.GeaModalTriggerBound = true;
    }

    const pending = window.GeaModalQueue || [];
    pending.forEach((id) => initById(id));
    window.GeaModalQueue = [];
})();
