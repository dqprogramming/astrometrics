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

        var sortInput = newRow.querySelector('input[name$="-sort_order"]');
        if (sortInput) {
            sortInput.value = count;
        }

        listEl.appendChild(newRow);
        setFormCount(prefix, count + 1);
        initDeleteButton(newRow);
        updateSortOrders(listEl);

        var firstInput = newRow.querySelector('input[type="email"]');
        if (firstInput) {
            firstInput.focus();
        }
    }

    function initDeleteButton(row) {
        var btn = row.querySelector('.btn-delete-link');
        if (!btn) return;
        btn.addEventListener('click', function () {
            if (!confirm('Remove this recipient?')) return;
            var checkbox = row.querySelector('input[name$="-DELETE"]');
            if (checkbox) {
                checkbox.checked = true;
                row.style.display = 'none';
            } else {
                var listEl = row.parentNode;
                row.remove();
                updateSortOrders(listEl);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initSortable(document.getElementById('recipient-list'));

        document.querySelectorAll('.link-row').forEach(initDeleteButton);

        document.querySelectorAll('.btn-add-link').forEach(function (btn) {
            btn.addEventListener('click', function () {
                addLink(btn.dataset.target, btn.dataset.prefix);
            });
        });

        var form = document.getElementById('contact-form-settings');
        if (form) {
            form.addEventListener('submit', function () {
                updateSortOrders(document.getElementById('recipient-list'));
            });
        }
    });
})();
