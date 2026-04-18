(function () {
  class CarrouselController {
    constructor(root) {
      this.root = root;
      this.viewport = root.querySelector("[data-carousel-viewport]");
      this.track = root.querySelector("[data-carousel-track]");
      this.dotsContainer = root.querySelector("[data-carousel-dots]");
      this.statusNode = root.querySelector("[data-carousel-status]");
      this.prevButton = root.querySelector("[data-carousel-prev]");
      this.nextButton = root.querySelector("[data-carousel-next]");
      this.loop = root.dataset.loop === "true";
      this.showDots = root.dataset.showDots === "true";
      this.dotsMode = root.dataset.dotsMode || "auto";
      this.autoplayMs = Number(root.dataset.autoplayMs || 0);
      this.autoplayMode = root.dataset.autoplayMode || "stop";
      this.pauseOnHover = root.dataset.pauseOnHover !== "false";
      this.currentPage = 0;
      this.timerId = null;
      this.resizeHandler = () => this.handleResize();
      this.scrollFrame = null;
      this.autoplayDirection = 1;
    }

    get slides() {
      return Array.from(this.track.children);
    }

    mount() {
      if (!this.viewport || !this.track || this.root.dataset.carouselInitialized === "true") {
        return;
      }

      this.bindEvents();
      this.syncUi();
      this.ensureInitialPosition();
      this.startAutoplay();
      this.root.dataset.carouselInitialized = "true";
    }

    bindEvents() {
      if (this.prevButton) {
        this.prevButton.addEventListener("click", () => this.goToPage(this.currentPage - 1));
      }

      if (this.nextButton) {
        this.nextButton.addEventListener("click", () => this.goToPage(this.currentPage + 1));
      }

      if (this.pauseOnHover) {
        this.root.addEventListener("mouseenter", () => this.stopAutoplay());
        this.root.addEventListener("mouseleave", () => this.startAutoplay());
      }
      this.root.addEventListener("keydown", (event) => this.handleKeydown(event));
      this.viewport.addEventListener("scroll", () => this.handleScroll());
      window.addEventListener("resize", this.resizeHandler);
    }

    getSlidesPerView() {
      const rawValue = getComputedStyle(this.root).getPropertyValue("--slides-per-view").trim();
      const parsed = Number(rawValue);
      return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
    }

    getPageCount() {
      return Math.max(1, Math.ceil(this.slides.length / this.getSlidesPerView()));
    }

    getMaxStartIndex() {
      return Math.max(0, this.slides.length - this.getSlidesPerView());
    }

    getPageStartIndex(page) {
      return Math.min(page * this.getSlidesPerView(), this.getMaxStartIndex());
    }

    getPageOffsets() {
      const pageCount = this.getPageCount();
      const offsets = [];

      for (let page = 0; page < pageCount; page += 1) {
        const startIndex = this.getPageStartIndex(page);
        const slide = this.slides[startIndex];
        offsets.push(slide ? slide.offsetLeft : 0);
      }

      return offsets;
    }

    getDotsEnabled() {
      if (!this.showDots || this.getPageCount() <= 1) {
        return false;
      }

      if (this.dotsMode === "always") {
        return true;
      }

      if (this.dotsMode === "never") {
        return false;
      }

      return this.getSlidesPerView() === 1;
    }

    syncUi() {
      const maxPage = this.getPageCount() - 1;
      this.currentPage = Math.min(this.currentPage, maxPage);
      this.renderDots();
      this.updateControls();
      this.scrollToPage(this.currentPage, "auto");
      this.updateStatus();
    }

    ensureInitialPosition() {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          this.currentPage = 0;
          this.scrollToPage(0, "auto");
          this.updateControls();
          this.updateDots();
          this.updateStatus();
        });
      });
    }

    goToPage(page) {
      const maxPage = this.getPageCount() - 1;
      if (maxPage < 0) {
        return;
      }

      if (page < 0) {
        page = this.loop ? maxPage : 0;
      } else if (page > maxPage) {
        page = this.loop ? 0 : maxPage;
      }

      this.currentPage = page;
      this.scrollToPage(page, "smooth");
      this.updateControls();
      this.updateDots();
      this.updateStatus();
    }

    scrollToPage(page, behavior) {
      if (!this.slides.length) {
        return;
      }

      const index = this.getPageStartIndex(page);
      this.viewport.scrollTo({
        left: this.slides[index].offsetLeft,
        behavior,
      });
    }

    renderDots() {
      if (!this.dotsContainer) {
        return;
      }

      this.dotsContainer.hidden = !this.getDotsEnabled();
      if (this.dotsContainer.hidden) {
        this.dotsContainer.innerHTML = "";
        return;
      }

      this.dotsContainer.innerHTML = "";
      const pageCount = this.getPageCount();
      for (let index = 0; index < pageCount; index += 1) {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.className = "gc-carrousel__dot";
        dot.ariaLabel = `Go to page ${index + 1}`;
        dot.addEventListener("click", () => this.goToPage(index));
        this.dotsContainer.appendChild(dot);
      }
      this.updateDots();
    }

    updateDots() {
      if (!this.dotsContainer || this.dotsContainer.hidden) {
        return;
      }

      const dots = this.dotsContainer.querySelectorAll(".gc-carrousel__dot");
      dots.forEach((dot, index) => {
        dot.classList.toggle("is-active", index === this.currentPage);
        dot.setAttribute("aria-current", index === this.currentPage ? "true" : "false");
      });
    }

    updateControls() {
      const maxPage = this.getPageCount() - 1;
      if (this.prevButton) {
        this.prevButton.disabled = !this.loop && this.currentPage <= 0;
      }
      if (this.nextButton) {
        this.nextButton.disabled = !this.loop && this.currentPage >= maxPage;
      }
    }

    startAutoplay() {
      if (!this.autoplayMs || this.autoplayMs < 300) {
        return;
      }

      this.stopAutoplay();
      this.timerId = window.setInterval(() => this.tickAutoplay(), this.autoplayMs);
    }

    stopAutoplay() {
      if (!this.timerId) {
        return;
      }

      window.clearInterval(this.timerId);
      this.timerId = null;
    }

    tickAutoplay() {
      const maxPage = this.getPageCount() - 1;
      if (maxPage <= 0) {
        return;
      }

      if (this.autoplayMode === "loop" || this.loop) {
        this.goToPage(this.currentPage + 1);
        return;
      }

      if (this.autoplayMode === "bounce") {
        if (this.currentPage >= maxPage) {
          this.autoplayDirection = -1;
        } else if (this.currentPage <= 0) {
          this.autoplayDirection = 1;
        }

        this.goToPage(this.currentPage + this.autoplayDirection);
        return;
      }

      if (this.currentPage >= maxPage) {
        this.stopAutoplay();
        return;
      }

      this.goToPage(this.currentPage + 1);
    }

    handleScroll() {
      if (this.scrollFrame) {
        window.cancelAnimationFrame(this.scrollFrame);
      }

      this.scrollFrame = window.requestAnimationFrame(() => {
        this.scrollFrame = null;
        this.syncPageFromScroll();
      });
    }

    syncPageFromScroll() {
      if (!this.slides.length) {
        return;
      }

      const currentLeft = this.viewport.scrollLeft;
      const pageOffsets = this.getPageOffsets();
      let nearestPage = 0;
      let smallestDistance = Number.POSITIVE_INFINITY;

      pageOffsets.forEach((offsetLeft, page) => {
        const distance = Math.abs(offsetLeft - currentLeft);
        if (distance < smallestDistance) {
          smallestDistance = distance;
          nearestPage = page;
        }
      });

      this.currentPage = nearestPage;
      this.updateControls();
      this.updateDots();
      this.updateStatus();
    }

    updateStatus() {
      if (!this.statusNode) {
        return;
      }

      const pageCount = this.getPageCount();
      this.statusNode.textContent = `Page ${this.currentPage + 1} of ${pageCount}`;
    }

    handleKeydown(event) {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        this.goToPage(this.currentPage - 1);
        return;
      }

      if (event.key === "ArrowRight") {
        event.preventDefault();
        this.goToPage(this.currentPage + 1);
      }
    }

    handleResize() {
      this.syncUi();
    }
  }

  const registry = new Map();

  function getRootById(id) {
    if (!id) {
      return null;
    }

    return document.querySelector(`[data-carousel-id="${CSS.escape(id)}"]`);
  }

  function init(root) {
    if (!root) {
      return null;
    }

    const existingId = root.dataset.carouselId;
    if (existingId && registry.has(existingId)) {
      return registry.get(existingId);
    }

    const instance = new CarrouselController(root);
    instance.mount();

    if (existingId) {
      registry.set(existingId, instance);
    }

    return instance;
  }

  function initById(id) {
    const root = getRootById(id);
    return init(root);
  }

  window.GeaCarrousel = window.GeaCarrousel || {
    init,
    initById,
    registry,
  };

  const pending = window.GeaCarrouselQueue || [];
  pending.forEach((id) => initById(id));
  window.GeaCarrouselQueue = [];
})();
