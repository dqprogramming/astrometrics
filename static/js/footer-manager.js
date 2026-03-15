(function () {
    'use strict';

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
        var rows = listEl.querySelectorAll('.link-row');
        rows.forEach(function (row, index) {
            var sortInput = row.querySelector('input[name$="-sort_order"]');
            if (sortInput) {
                sortInput.value = index;
            }
        });
    }

    function getFormCount(prefix) {
        var totalForms = document.querySelector('#id_' + prefix + '-TOTAL_FORMS');
        return parseInt(totalForms.value, 10);
    }

    function setFormCount(prefix, count) {
        var totalForms = document.querySelector('#id_' + prefix + '-TOTAL_FORMS');
        totalForms.value = count;
    }

    function addLink(targetId, prefix) {
        var listEl = document.getElementById(targetId);
        var count = getFormCount(prefix);
        var template = document.getElementById('link-row-template');
        var newRow = template.content.firstElementChild.cloneNode(true);

        // Replace __prefix__ placeholders with the actual prefix-index
        var fullPrefix = prefix + '-' + count;
        var inputs = newRow.querySelectorAll('input');
        inputs.forEach(function (input) {
            if (input.name) {
                input.name = input.name.replace('__prefix__', fullPrefix);
            }
            if (input.id) {
                input.id = input.id.replace('__prefix__', fullPrefix);
            }
        });

        // Set sort order
        var sortInput = newRow.querySelector('input[name$="-sort_order"]');
        if (sortInput) {
            sortInput.value = count;
        }

        listEl.appendChild(newRow);
        setFormCount(prefix, count + 1);
        initDeleteButton(newRow);
        updateSortOrders(listEl);
    }

    function initDeleteButton(row) {
        var btn = row.querySelector('.btn-delete-link');
        if (!btn) return;
        btn.addEventListener('click', function () {
            if (!confirm('Remove this link?')) return;
            var checkbox = row.querySelector('input[name$="-DELETE"]');
            if (checkbox) {
                checkbox.checked = true;
                row.style.display = 'none';
            } else {
                // New unsaved row — just remove from DOM
                var listEl = row.parentNode;
                row.remove();
                var prefix = listEl.id === 'col1-links' ? 'col1_links' : 'col2_links';
                updateSortOrders(listEl);
            }
        });
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', function () {
        initSortable(document.getElementById('col1-links'));
        initSortable(document.getElementById('col2-links'));

        // Init delete buttons
        document.querySelectorAll('.link-row').forEach(initDeleteButton);

        // Init add buttons
        document.querySelectorAll('.btn-add-link').forEach(function (btn) {
            btn.addEventListener('click', function () {
                addLink(btn.dataset.target, btn.dataset.prefix);
            });
        });

        // On form submit, update sort orders
        var form = document.getElementById('footer-form');
        if (form) {
            form.addEventListener('submit', function () {
                updateSortOrders(document.getElementById('col1-links'));
                updateSortOrders(document.getElementById('col2-links'));
            });
        }
    });
})();
