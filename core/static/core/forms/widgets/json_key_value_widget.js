(function () {
  "use strict";

  const widgetSelector = "[data-json-key-value-widget]";
  const rowsSelector = "[data-json-key-value-rows]";
  const rowSelector = "[data-json-key-value-row]";
  const addSelector = "[data-json-key-value-add]";
  const removeSelector = "[data-json-key-value-remove]";
  const templateSelector = "[data-json-key-value-template]";
  const inputSelector = "[data-json-key-value-key], [data-json-key-value-value]";
  const emptyFormSelector = ".empty-form";

  function clearRow(row) {
    row.querySelectorAll(inputSelector).forEach((input) => {
      input.value = "";
    });
  }

  function getRows(widget) {
    return Array.from(widget.querySelectorAll(rowSelector));
  }

  function addRow(widget) {
    const rowsContainer = widget.querySelector(rowsSelector);
    const template = widget.querySelector(templateSelector);
    if (!rowsContainer || !template) {
      return;
    }

    const fragment = template.content.cloneNode(true);
    rowsContainer.appendChild(fragment);
  }

  function removeRow(widget, row) {
    const rows = getRows(widget);
    if (rows.length <= 1) {
      clearRow(row);
      return;
    }

    row.remove();
  }

  function initWidget(widget) {
    if (widget.closest(emptyFormSelector)) {
      return;
    }

    if (widget.dataset.jsonKeyValueInitialized === "true") {
      return;
    }

    widget.dataset.jsonKeyValueInitialized = "true";
    widget.addEventListener("click", (event) => {
      const addButton = event.target.closest(addSelector);
      if (addButton) {
        event.preventDefault();
        addRow(widget);
        return;
      }

      const removeButton = event.target.closest(removeSelector);
      if (removeButton) {
        event.preventDefault();
        const row = removeButton.closest(rowSelector);
        if (row) {
          removeRow(widget, row);
        }
      }
    });
  }

  function resetClonedWidgets(root) {
    if (!root.querySelectorAll) {
      return;
    }

    if (root.matches && root.matches(widgetSelector)) {
      delete root.dataset.jsonKeyValueInitialized;
    }

    root.querySelectorAll(widgetSelector).forEach((widget) => {
      delete widget.dataset.jsonKeyValueInitialized;
    });
  }

  function initAll(root) {
    if (root.matches && root.matches(widgetSelector)) {
      initWidget(root);
    }

    root.querySelectorAll(widgetSelector).forEach(initWidget);
  }

  document.addEventListener("DOMContentLoaded", () => initAll(document));
  document.addEventListener("formset:added", (event) => {
    resetClonedWidgets(event.target);
    initAll(event.target);
  });
})();
