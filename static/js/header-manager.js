(function () {
    'use strict';

    var PREFIX = 'menu_items';

    function getFormCount() {
        var el = document.querySelector('#id_' + PREFIX + '-TOTAL_FORMS');
        return parseInt(el.value, 10);
    }

    function setFormCount(count) {
        var el = document.querySelector('#id_' + PREFIX + '-TOTAL_FORMS');
        el.value = count;
    }

    function initSortable(listEl) {
        if (!listEl) return;
        Sortable.create(listEl, {
            handle: '.drag-handle',
            animation: 150,
            onEnd: function () {
                updateSortOrders(listEl);
            }
        });
    }

    function updateSortOrders(listEl) {
        var rows = listEl.querySelectorAll(':scope > .menu-item-row');
        rows.forEach(function (row, index) {
            var sortInput = row.querySelector(':scope > .item-main input[name$="-sort_order"]');
            if (sortInput) {
                sortInput.value = index;
            }
        });
    }

    function updateAllSortOrders() {
        // Top-level items
        var topList = document.getElementById('menu-items');
        var topRows = topList.querySelectorAll(':scope > .top-level-row');
        topRows.forEach(function (row, index) {
            var sortInput = row.querySelector(':scope > .item-main input[name$="-sort_order"]');
            if (sortInput) {
                sortInput.value = index;
            }
        });

        // Sub-items within each top-level item
        topList.querySelectorAll('.sub-items').forEach(function (subContainer) {
            var subRows = subContainer.querySelectorAll(':scope > .sub-item-row');
            subRows.forEach(function (row, index) {
                var sortInput = row.querySelector('input[name$="-sort_order"]');
                if (sortInput) {
                    sortInput.value = index;
                }
            });
        });
    }

    function replacePrefix(el, count) {
        var fullPrefix = PREFIX + '-' + count;
        var inputs = el.querySelectorAll('input');
        inputs.forEach(function (input) {
            if (input.name) {
                input.name = input.name.replace('__prefix__', fullPrefix);
            }
            if (input.id) {
                input.id = input.id.replace('__prefix__', fullPrefix);
            }
        });
        // Also handle labels
        var labels = el.querySelectorAll('label');
        labels.forEach(function (label) {
            if (label.htmlFor) {
                label.htmlFor = label.htmlFor.replace('__prefix__', fullPrefix);
            }
        });
    }

    function getVisibleSubItemCount(parentRow) {
        var subContainer = parentRow.querySelector('.sub-items');
        if (!subContainer) return 0;
        var subRows = subContainer.querySelectorAll(':scope > .sub-item-row');
        var count = 0;
        subRows.forEach(function (row) {
            if (row.style.display !== 'none') {
                count++;
            }
        });
        return count;
    }

    function updateCtaState(parentRow) {
        var checkbox = parentRow.querySelector('input[name$="-show_cta_in_dropdown"]');
        if (!checkbox || checkbox.type !== 'checkbox') return;
        var hasSubItems = getVisibleSubItemCount(parentRow) > 0;
        checkbox.disabled = !hasSubItems;
        if (!hasSubItems) {
            checkbox.checked = false;
        }
        updateCtaFieldsVisibility(parentRow);
    }

    function updateCtaFieldsVisibility(parentRow) {
        var checkbox = parentRow.querySelector('input[name$="-show_cta_in_dropdown"]');
        var ctaFields = parentRow.querySelector('.cta-fields');
        if (!checkbox || !ctaFields) return;
        if (checkbox.checked) {
            ctaFields.style.display = 'grid';
        } else {
            ctaFields.style.display = 'none';
        }
    }

    function initCtaToggle(row) {
        var checkbox = row.querySelector('input[name$="-show_cta_in_dropdown"]');
        if (!checkbox || checkbox.type !== 'checkbox') return;
        checkbox.addEventListener('change', function () {
            updateCtaFieldsVisibility(row);
        });
        // Set initial state
        updateCtaState(row);
    }

    function addTopLevelItem() {
        var count = getFormCount();
        var template = document.getElementById('top-level-template');
        var newRow = template.content.firstElementChild.cloneNode(true);
        replacePrefix(newRow, count);

        var listEl = document.getElementById('menu-items');
        listEl.appendChild(newRow);
        setFormCount(count + 1);
        initDeleteButton(newRow);
        initExpandCollapse(newRow);
        initAddSubItemButton(newRow);
        initCtaToggle(newRow);

        // Init sortable on sub-items container
        var subContainer = newRow.querySelector('.sub-items');
        if (subContainer) {
            initSortable(subContainer);
        }

        updateAllSortOrders();

        var firstInput = newRow.querySelector('input[type="text"]');
        if (firstInput) {
            firstInput.focus();
        }
    }

    function addSubItem(parentRow) {
        var parentPk = parentRow.getAttribute('data-item-pk');
        if (!parentPk) return;

        var count = getFormCount();
        var template = document.getElementById('sub-item-template');
        var newRow = template.content.firstElementChild.cloneNode(true);
        replacePrefix(newRow, count);

        // Set parent
        var parentInput = newRow.querySelector('input[name$="-parent"]');
        if (parentInput) {
            parentInput.value = parentPk;
        }

        var subContainer = parentRow.querySelector('.sub-items');
        subContainer.appendChild(newRow);
        setFormCount(count + 1);
        initDeleteButton(newRow);
        updateAllSortOrders();
        updateCtaState(parentRow);

        var firstInput = newRow.querySelector('input[type="text"]');
        if (firstInput) {
            firstInput.focus();
        }
    }

    function initDeleteButton(row) {
        var btn = row.querySelector(':scope > .item-main .btn-delete-link');
        if (!btn) return;
        btn.addEventListener('click', function () {
            if (!confirm('Remove this item?')) return;
            var checkbox = row.querySelector(':scope > .item-main input[name$="-DELETE"]');
            if (checkbox) {
                checkbox.checked = true;
                row.style.display = 'none';

                // If deleting a top-level item, also mark its sub-items for deletion
                if (row.classList.contains('top-level-row')) {
                    var subRows = row.querySelectorAll('.sub-item-row');
                    subRows.forEach(function (subRow) {
                        var subCheckbox = subRow.querySelector('input[name$="-DELETE"]');
                        if (subCheckbox) {
                            subCheckbox.checked = true;
                            subRow.style.display = 'none';
                        }
                    });
                }

                // If deleting a sub-item, update the parent's CTA state
                if (row.classList.contains('sub-item-row')) {
                    var parentRow = row.closest('.top-level-row');
                    if (parentRow) {
                        updateCtaState(parentRow);
                    }
                }
            } else {
                // If deleting a sub-item, find parent before removing
                var parentRow = row.closest('.top-level-row');
                row.remove();
                updateAllSortOrders();
                if (parentRow) {
                    updateCtaState(parentRow);
                }
            }
        });
    }

    function initExpandCollapse(row) {
        var btn = row.querySelector('.btn-expand-toggle');
        if (!btn) return;
        btn.addEventListener('click', function () {
            var expanded = btn.getAttribute('aria-expanded') === 'true';
            btn.setAttribute('aria-expanded', !expanded);
            var icon = btn.querySelector('i');
            icon.className = expanded ? 'bi bi-chevron-right' : 'bi bi-chevron-down';

            var subContainer = row.querySelector('.sub-items');
            var addSubBtn = row.querySelector('.btn-add-sub-item');
            var ctaFields = row.querySelector('.cta-fields');
            if (subContainer) {
                subContainer.style.display = expanded ? 'none' : '';
            }
            if (addSubBtn) {
                addSubBtn.style.display = expanded ? 'none' : '';
            }
            if (ctaFields) {
                // Only show CTA fields if both expanded and checkbox checked
                var checkbox = row.querySelector('input[name$="-show_cta_in_dropdown"]');
                if (expanded) {
                    ctaFields.style.display = 'none';
                } else if (checkbox && checkbox.checked) {
                    ctaFields.style.display = 'grid';
                }
            }
        });
    }

    function initAddSubItemButton(row) {
        var btn = row.querySelector('.btn-add-sub-item');
        if (!btn) return;
        btn.addEventListener('click', function () {
            addSubItem(row);
        });
    }

    // Organize items: move sub-items into their parent's .sub-items container
    function organizeItems() {
        var allRows = document.querySelectorAll('#menu-items > .menu-item-row');
        var parentMap = {};

        // Build map of pk -> row for top-level items
        allRows.forEach(function (row) {
            if (row.classList.contains('top-level-row')) {
                var pk = row.getAttribute('data-item-pk');
                if (pk) {
                    parentMap[pk] = row;
                }
            }
        });

        // Move sub-items into their parent's container
        allRows.forEach(function (row) {
            if (row.classList.contains('sub-item-row')) {
                var parentInput = row.querySelector('input[name$="-parent"]');
                if (parentInput && parentInput.value) {
                    var parentRow = parentMap[parentInput.value];
                    if (parentRow) {
                        var subContainer = parentRow.querySelector('.sub-items');
                        if (subContainer) {
                            subContainer.appendChild(row);
                        }
                    }
                }
            }
        });
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', function () {
        organizeItems();

        // Init sortable on top-level list
        initSortable(document.getElementById('menu-items'));

        // Init sortable on each sub-items container
        document.querySelectorAll('.sub-items').forEach(function (el) {
            initSortable(el);
        });

        // Init delete buttons
        document.querySelectorAll('.menu-item-row').forEach(initDeleteButton);

        // Init expand/collapse
        document.querySelectorAll('.top-level-row').forEach(initExpandCollapse);

        // Init add sub-item buttons
        document.querySelectorAll('.top-level-row').forEach(initAddSubItemButton);

        // Init CTA toggles
        document.querySelectorAll('.top-level-row').forEach(initCtaToggle);

        // Add top-level item button
        var addBtn = document.getElementById('btn-add-top-level');
        if (addBtn) {
            addBtn.addEventListener('click', addTopLevelItem);
        }

        // On form submit, update all sort orders
        var form = document.getElementById('header-form');
        if (form) {
            form.addEventListener('submit', function () {
                updateAllSortOrders();
                // Re-enable disabled checkboxes so their values are submitted
                document.querySelectorAll('input[name$="-show_cta_in_dropdown"][disabled]').forEach(function (cb) {
                    cb.disabled = false;
                });
            });
        }
    });
})();
