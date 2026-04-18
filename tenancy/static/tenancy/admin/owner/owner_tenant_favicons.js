(function () {
  "use strict";

  function applyThemeAwareFavicons() {
    var faviconLinks = Array.from(
      document.head.querySelectorAll('link[rel="icon"]')
    );

    if (faviconLinks.length !== 2) {
      return;
    }

    if (faviconLinks[0].hasAttribute("media") && faviconLinks[1].hasAttribute("media")) {
      return;
    }

    if (!faviconLinks[0].getAttribute("href") || !faviconLinks[1].getAttribute("href")) {
      return;
    }

    var faviconDefinitions = [
      {
        href: faviconLinks[0].getAttribute("href"),
        type: faviconLinks[0].getAttribute("type"),
        sizes: faviconLinks[0].getAttribute("sizes"),
        media: "(prefers-color-scheme: light)",
      },
      {
        href: faviconLinks[1].getAttribute("href"),
        type: faviconLinks[1].getAttribute("type"),
        sizes: faviconLinks[1].getAttribute("sizes"),
        media: "(prefers-color-scheme: dark)",
      },
    ];

    faviconLinks.forEach(function (link) {
      link.remove();
    });

    faviconDefinitions.forEach(function (favicon) {
      var link = document.createElement("link");
      link.setAttribute("rel", "icon");
      link.setAttribute("href", favicon.href);

      if (favicon.type) {
        link.setAttribute("type", favicon.type);
      }

      if (favicon.sizes) {
        link.setAttribute("sizes", favicon.sizes);
      }

      link.setAttribute("media", favicon.media);
      document.head.appendChild(link);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyThemeAwareFavicons);
    return;
  }

  applyThemeAwareFavicons();
})();
