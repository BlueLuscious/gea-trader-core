(function () {
    "use strict";

    const mobileMenu = document.querySelector(".top-nav__mobile-menu");

    if (!mobileMenu) {
        return;
    }

    const closeMenu = () => {
        mobileMenu.removeAttribute("open");
    };

    document.addEventListener("click", (event) => {
        if (!mobileMenu.hasAttribute("open")) {
            return;
        }

        if (!mobileMenu.contains(event.target)) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            closeMenu();
        });
    });
})();
