(function () {
  "use strict";

  const widgetSelector = "[data-nested-json-key-value-widget]";
  const rowsSelector = "[data-nested-json-key-value-rows]";
  const rowSelector = "[data-nested-json-key-value-row]";
  const addRootSelector = "[data-nested-json-key-value-add-root]";
  const addChildSelector = "[data-nested-json-key-value-add-child]";
  const removeSelector = "[data-nested-json-key-value-remove]";
  const templateSelector = "[data-nested-json-key-value-template]";
  const rowIdInputSelector = "[data-nested-json-key-value-row-id-input]";
  const parentIdInputSelector = "[data-nested-json-key-value-parent-id-input]";
  const valueInputSelector = "[data-nested-json-key-value-value]";
  const emptyFormSelector = ".empty-form";

  function getRows(widget) {
    return Array.from(widget.querySelectorAll(rowSelector));
  }

  function getRowId(row) {
    return row.dataset.nestedJsonKeyValueRowId || "";
  }

  function getParentId(row) {
    return row.dataset.nestedJsonKeyValueParentId || "";
  }

  function getDepth(row) {
    return Number.parseInt(row.dataset.nestedJsonKeyValueDepth || "1", 10);
  }

  function getMaxDepth(widget) {
    return Number.parseInt(widget.dataset.nestedJsonKeyValueMaxDepth || "2", 10);
  }

  function createRowId(widget) {
    const nextId = Number.parseInt(widget.dataset.nestedJsonKeyValueNextId || "1", 10);
    widget.dataset.nestedJsonKeyValueNextId = String(nextId + 1);
    return `nested-row-${Date.now()}-${nextId}`;
  }

  function syncNextId(widget) {
    const existingCount = getRows(widget).length + 1;
    widget.dataset.nestedJsonKeyValueNextId = String(existingCount);
  }

  function updateChildButton(row, maxDepth) {
    const childButton = row.querySelector(addChildSelector);
    if (!childButton) {
      return;
    }

    childButton.hidden = getDepth(row) >= maxDepth;
  }

  function updateValueInput(row, hasChildren) {
    const valueInput = row.querySelector(valueInputSelector);
    if (!valueInput) {
      return;
    }

    row.dataset.nestedJsonKeyValueHasChildren = hasChildren ? "true" : "false";
    valueInput.hidden = hasChildren;
    if (hasChildren) {
      valueInput.value = "";
    }
  }

  function setRowMetadata(row, rowId, parentId, depth, maxDepth) {
    row.dataset.nestedJsonKeyValueRowId = rowId;
    row.dataset.nestedJsonKeyValueParentId = parentId;
    row.dataset.nestedJsonKeyValueDepth = String(depth);
    row.dataset.nestedJsonKeyValueHasChildren = "false";
    row.style.setProperty("--nested-json-key-value-depth", String(depth));

    const rowIdInput = row.querySelector(rowIdInputSelector);
    if (rowIdInput) {
      rowIdInput.value = rowId;
    }

    const parentIdInput = row.querySelector(parentIdInputSelector);
    if (parentIdInput) {
      parentIdInput.value = parentId;
    }

    updateChildButton(row, maxDepth);
  }

  function cloneTemplateRow(widget, parentId, depth) {
    const template = widget.querySelector(templateSelector);
    if (!template) {
      return null;
    }

    const fragment = template.content.cloneNode(true);
    const row = fragment.querySelector(rowSelector);
    if (!row) {
      return null;
    }

    setRowMetadata(row, createRowId(widget), parentId, depth, getMaxDepth(widget));
    return row;
  }

  function getDescendantRows(widget, row) {
    const rowId = getRowId(row);
    const rows = getRows(widget);
    const rowsByParentId = new Map();
    const descendants = [];

    rows.forEach((candidate) => {
      if (candidate === row) {
        return;
      }

      const parentId = getParentId(candidate);
      if (!rowsByParentId.has(parentId)) {
        rowsByParentId.set(parentId, []);
      }
      rowsByParentId.get(parentId).push(candidate);
    });

    function collectChildren(parentId) {
      const childRows = rowsByParentId.get(parentId) || [];
      childRows.forEach((childRow) => {
        if (descendants.includes(childRow)) {
          return;
        }

        descendants.push(childRow);
        collectChildren(getRowId(childRow));
      });
    }

    if (!rowId) {
      return descendants;
    }

    collectChildren(rowId);
    return descendants;
  }

  function ensureEditableRow(widget) {
    const rowsContainer = widget.querySelector(rowsSelector);
    if (!rowsContainer || getRows(widget).length > 0) {
      return;
    }

    const row = cloneTemplateRow(widget, "", 1);
    if (!row) {
      return;
    }

    rowsContainer.appendChild(row);
  }

  function refreshValueInputs(widget) {
    getRows(widget).forEach((row) => {
      updateValueInput(row, getDescendantRows(widget, row).length > 0);
    });
  }

  function refreshRows(widget) {
    const maxDepth = getMaxDepth(widget);
    getRows(widget).forEach((row) => {
      updateChildButton(row, maxDepth);
    });
    ensureEditableRow(widget);
    refreshValueInputs(widget);
  }

  function findInsertReference(widget, row) {
    const descendants = getDescendantRows(widget, row);
    if (descendants.length > 0) {
      return descendants[descendants.length - 1];
    }

    return row;
  }

  function addRootRow(widget) {
    const rowsContainer = widget.querySelector(rowsSelector);
    const row = cloneTemplateRow(widget, "", 1);
    if (!rowsContainer || !row) {
      return;
    }

    rowsContainer.appendChild(row);
  }

  function addChildRow(widget, row) {
    const rowsContainer = widget.querySelector(rowsSelector);
    const depth = getDepth(row);
    const maxDepth = getMaxDepth(widget);
    if (!rowsContainer || depth >= maxDepth) {
      return;
    }

    updateValueInput(row, true);

    const childRow = cloneTemplateRow(widget, getRowId(row), depth + 1);
    if (!childRow) {
      return;
    }

    const referenceRow = findInsertReference(widget, row);
    referenceRow.after(childRow);
    refreshRows(widget);
  }

  function clearRow(row) {
    row.querySelectorAll("input").forEach((input) => {
      if (input.type !== "hidden") {
        input.value = "";
      }
    });
  }

  function removeRow(widget, row) {
    const rows = getRows(widget);
    if (rows.length <= 1) {
      clearRow(row);
      return;
    }

    getDescendantRows(widget, row).forEach((descendant) => descendant.remove());
    row.remove();
    refreshRows(widget);
  }

  function normalizeExistingRows(widget) {
    refreshRows(widget);
    syncNextId(widget);
  }

  function initWidget(widget) {
    if (widget.closest(emptyFormSelector)) {
      return;
    }

    if (widget.dataset.nestedJsonKeyValueInitialized === "true") {
      return;
    }

    widget.dataset.nestedJsonKeyValueInitialized = "true";
    normalizeExistingRows(widget);
    widget.addEventListener("click", (event) => {
      const addRootButton = event.target.closest(addRootSelector);
      if (addRootButton) {
        event.preventDefault();
        addRootRow(widget);
        return;
      }

      const addChildButton = event.target.closest(addChildSelector);
      if (addChildButton) {
        event.preventDefault();
        const row = addChildButton.closest(rowSelector);
        if (row) {
          addChildRow(widget, row);
        }
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
      delete root.dataset.nestedJsonKeyValueInitialized;
    }

    root.querySelectorAll(widgetSelector).forEach((widget) => {
      delete widget.dataset.nestedJsonKeyValueInitialized;
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
