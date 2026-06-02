(function () {
    "use strict";

    const initializedWidgets = new WeakSet();

    function parseJsonData(value, fallback) {
        try {
            return JSON.parse(value || "");
        } catch (error) {
            return fallback;
        }
    }

    function findSourceElement(widget, sourceConfig) {
        const selector = sourceConfig.selector || "";
        if (!selector) {
            return null;
        }

        if (sourceConfig.scope === "closest") {
            const closestSelector = sourceConfig.closest_selector || sourceConfig.closestSelector || "";
            const scopeRoot = closestSelector ? widget.closest(closestSelector) : widget.parentElement;
            return scopeRoot ? scopeRoot.querySelector(selector) : null;
        }

        return document.querySelector(selector);
    }

    function getElementValue(element, sourceConfig) {
        if (!element) {
            return "";
        }

        const attributeName = sourceConfig.attribute || "";
        if (attributeName) {
            return element.getAttribute(attributeName) || "";
        }

        return element.value || "";
    }

    function buildParams(widget) {
        const params = new URLSearchParams();
        const staticParams = parseJsonData(widget.dataset.actionInputStaticParams, {});
        const sourceParams = parseJsonData(widget.dataset.actionInputSourceParams, []);

        Object.entries(staticParams).forEach(([name, value]) => {
            params.set(name, String(value));
        });

        sourceParams.forEach((sourceConfig) => {
            const name = sourceConfig.name || "";
            if (!name) {
                return;
            }

            const element = findSourceElement(widget, sourceConfig);
            params.set(name, getElementValue(element, sourceConfig));
        });

        return params;
    }

    function setButtonBusy(button, isBusy) {
        button.disabled = isBusy;
        button.dataset.loading = isBusy ? "true" : "false";
    }

    async function runAction(widget) {
        const actionUrl = widget.dataset.actionInputUrl || "";
        const responseKey = widget.dataset.actionInputResponseKey || "value";
        const input = widget.querySelector("[data-action-input-control]");
        const button = widget.querySelector("[data-action-input-button]");
        if (!actionUrl || !input || !button) {
            return;
        }

        setButtonBusy(button, true);
        try {
            const response = await fetch(`${actionUrl}?${buildParams(widget).toString()}`, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            });
            if (!response.ok) {
                return;
            }

            const payload = await response.json();
            if (Object.prototype.hasOwnProperty.call(payload, responseKey)) {
                input.value = payload[responseKey] || "";
                input.dispatchEvent(new Event("change", { bubbles: true }));
            }
        } finally {
            setButtonBusy(button, false);
        }
    }

    function initWidget(widget) {
        if (initializedWidgets.has(widget)) {
            return;
        }

        initializedWidgets.add(widget);
        const button = widget.querySelector("[data-action-input-button]");
        if (button) {
            button.addEventListener("click", () => runAction(widget));
        }
    }

    function initActionInputWidgets() {
        document.querySelectorAll("[data-action-input-widget]").forEach(initWidget);
    }

    document.addEventListener("DOMContentLoaded", () => {
        initActionInputWidgets();
        const observer = new MutationObserver(initActionInputWidgets);
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    });
})();
