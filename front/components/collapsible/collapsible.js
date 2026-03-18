(function () {
  class CollapsibleController {
    constructor(root) {
      this.root = root;
      this.summary = root.querySelector("[data-collapsible-summary]");
      this.panel = root.querySelector("[data-collapsible-panel]");
      this.closeOnOutside = root.dataset.closeOnOutside === "true";
      this.closeOnEscape = root.dataset.closeOnEscape !== "false";
      this.closeOnLinkClick = root.dataset.closeOnLinkClick === "true";
      this.handleDocumentClick = (event) => this.onDocumentClick(event);
      this.handleKeydown = (event) => this.onKeydown(event);
    }

    mount() {
      if (!this.summary || this.root.dataset.collapsibleInitialized === "true") {
        return;
      }

      this.root.addEventListener("toggle", () => this.syncState());

      if (this.closeOnOutside) {
        document.addEventListener("click", this.handleDocumentClick);
      }

      if (this.closeOnEscape) {
        document.addEventListener("keydown", this.handleKeydown);
      }

      if (this.closeOnLinkClick) {
        this.root.querySelectorAll("a").forEach((link) => {
          link.addEventListener("click", () => {
            this.root.removeAttribute("open");
            this.syncState();
          });
        });
      }

      this.syncState();
      this.root.dataset.collapsibleInitialized = "true";
    }

    syncState() {
      const isOpen = this.root.hasAttribute("open");
      this.root.dataset.collapsibleOpen = isOpen ? "true" : "false";
      this.summary.setAttribute("aria-expanded", isOpen ? "true" : "false");
    }

    onDocumentClick(event) {
      if (!this.root.hasAttribute("open")) {
        return;
      }

      if (!this.root.contains(event.target)) {
        this.root.removeAttribute("open");
        this.syncState();
      }
    }

    onKeydown(event) {
      if (event.key !== "Escape" || !this.root.hasAttribute("open")) {
        return;
      }

      this.root.removeAttribute("open");
      this.syncState();
    }
  }

  const registry = new Map();

  function getRootById(id) {
    if (!id) {
      return null;
    }

    return document.querySelector(`[data-collapsible-id="${CSS.escape(id)}"]`);
  }

  function init(root) {
    if (!root) {
      return null;
    }

    const existingId = root.dataset.collapsibleId;
    if (existingId && registry.has(existingId)) {
      return registry.get(existingId);
    }

    const instance = new CollapsibleController(root);
    instance.mount();

    if (existingId) {
      registry.set(existingId, instance);
    }

    return instance;
  }

  function initById(id) {
    return init(getRootById(id));
  }

  window.GeaCollapsible = window.GeaCollapsible || {
    init,
    initById,
    registry,
  };

  const pending = window.GeaCollapsibleQueue || [];
  pending.forEach((id) => initById(id));
  window.GeaCollapsibleQueue = [];
})();
