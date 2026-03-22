(function () {
    'use strict';

    var dirty = false;

    function markDirty() {
        dirty = true;
    }

    // -- Sortable: quotes -----------------------------------------------------

    function initQuoteSortable() {
        var list = document.getElementById('quote-list');
        if (!list) return;
        Sortable.create(list, {
            handle: '.quote-drag-handle',
            animation: 150,
            onEnd: function () {
                updateQuoteSortOrders();
                markDirty();
            }
        });
    }

    function updateQuoteSortOrders() {
        var list = document.getElementById('quote-list');
        if (!list) return;
        var rows = list.querySelectorAll('.quote-row');
        rows.forEach(function (row, idx) {
            var input = row.querySelector('input[name$="-sort_order"]');
            if (input) input.value = idx;
        });
    }

    // -- Delete quote ---------------------------------------------------------

    function initDeleteQuote(btn) {
        btn.addEventListener('click', function () {
            if (!confirm('Remove this quote?')) return;
            var row = btn.closest('.quote-row');
            var deleteCheckbox = row.querySelector('input[name$="-DELETE"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                row.style.display = 'none';
            } else {
                row.remove();
            }
            markDirty();
        });
    }

    // -- Add quote ------------------------------------------------------------

    function addQuote() {
        var listEl = document.getElementById('quote-list');
        var template = document.getElementById('quote-template');
        if (!listEl || !template) return;

        var totalForms = document.querySelector('#id_quotes-TOTAL_FORMS');
        var count = parseInt(totalForms.value, 10);

        var newRow = template.content.firstElementChild.cloneNode(true);

        // Replace __prefix__ with actual index
        var allInputs = newRow.querySelectorAll('input, textarea, select');
        allInputs.forEach(function (el) {
            if (el.name) el.name = el.name.replace(/__prefix__/g, count);
            if (el.id) el.id = el.id.replace(/__prefix__/g, count);
        });
        var allLabels = newRow.querySelectorAll('label');
        allLabels.forEach(function (el) {
            if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/__prefix__/g, count);
        });

        // Set sort order
        var sortInput = newRow.querySelector('input[name$="-sort_order"]');
        if (sortInput) sortInput.value = count;

        listEl.appendChild(newRow);
        totalForms.value = count + 1;

        initDeleteQuote(newRow.querySelector('.btn-delete-quote'));

        var firstInput = newRow.querySelector('textarea');
        if (firstInput) firstInput.focus();

        markDirty();
    }

    // -- Init -----------------------------------------------------------------

    document.addEventListener('DOMContentLoaded', function () {
        initQuoteSortable();

        document.querySelectorAll('.btn-delete-quote').forEach(initDeleteQuote);

        var addBtn = document.getElementById('btn-add-quote');
        if (addBtn) {
            addBtn.addEventListener('click', addQuote);
        }

        // Track edits as dirty
        var form = document.getElementById('about-us-form');
        if (form) {
            form.addEventListener('input', markDirty);

            // Update sort orders on form submit
            form.addEventListener('submit', function () {
                dirty = false;
                updateQuoteSortOrders();
            });
        }

        // Warn on navigation with unsaved changes
        window.addEventListener('beforeunload', function (e) {
            if (dirty) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    });
})();
