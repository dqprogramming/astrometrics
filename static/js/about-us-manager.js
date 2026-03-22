(function () {
    'use strict';

    var dirty = false;

    var TINYMCE_CONFIG = {
        height: 200,
        menubar: false,
        plugins: '',
        toolbar: 'bold italic underline | sub sup',
        valid_elements: 'p,br,strong/b,em/i,u,sub,sup',
        invalid_elements: 'script,iframe,object,embed,form,input',
        paste_as_text: false,
        paste_word_valid_elements: 'p,br,strong,b,em,i,u,sub,sup',
        formats: {
            underline: {inline: 'u'}
        }
    };

    function markDirty() {
        dirty = true;
    }

    // -- TinyMCE helpers ------------------------------------------------------

    function initTinyMCE(textarea) {
        if (!textarea || !window.tinyMCE) return;
        if (!textarea.id) {
            textarea.id = 'quote-mce-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7);
        }
        // Don't double-init
        if (tinyMCE.get(textarea.id)) return;
        tinyMCE.init(Object.assign({}, TINYMCE_CONFIG, {
            target: textarea,
            setup: function (editor) {
                editor.on('change keyup', markDirty);
            }
        }));
    }

    function syncAllTinyMCE() {
        if (window.tinyMCE) tinyMCE.triggerSave();
    }

    function destroyAllQuoteEditors() {
        if (!window.tinyMCE) return;
        var list = document.getElementById('quote-list');
        if (!list) return;
        list.querySelectorAll('textarea.quote-tinymce').forEach(function (ta) {
            var editor = tinyMCE.get(ta.id);
            if (editor) {
                editor.save();
                editor.remove();
            }
        });
    }

    function initAllQuoteEditors() {
        if (!window.tinyMCE) return;
        var list = document.getElementById('quote-list');
        if (!list) return;
        list.querySelectorAll('textarea.quote-tinymce').forEach(function (ta) {
            // Only init visible rows (not deleted ones)
            var row = ta.closest('.quote-row');
            if (row && row.style.display !== 'none') {
                initTinyMCE(ta);
            }
        });
    }

    // -- Sortable: quotes -----------------------------------------------------

    function initQuoteSortable() {
        var list = document.getElementById('quote-list');
        if (!list) return;
        Sortable.create(list, {
            handle: '.quote-drag-handle',
            animation: 150,
            onStart: function () {
                destroyAllQuoteEditors();
            },
            onEnd: function () {
                initAllQuoteEditors();
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
                // Existing row — sync content, destroy editor, mark for deletion
                var ta = row.querySelector('textarea.quote-tinymce');
                if (ta && window.tinyMCE) {
                    var editor = tinyMCE.get(ta.id);
                    if (editor) {
                        editor.save();
                        editor.remove();
                    }
                }
                deleteCheckbox.checked = true;
                row.style.display = 'none';
            } else {
                // New row — destroy editor and remove from DOM
                var ta2 = row.querySelector('textarea.quote-tinymce');
                if (ta2 && window.tinyMCE) {
                    var ed = tinyMCE.get(ta2.id);
                    if (ed) ed.remove();
                }
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

        // Init TinyMCE on the new textarea
        var textarea = newRow.querySelector('textarea.quote-tinymce');
        if (textarea) {
            textarea.id = 'id_quotes-' + count + '-quote_text';
            initTinyMCE(textarea);
        }

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

            // Sync TinyMCE and update sort orders on form submit
            form.addEventListener('submit', function () {
                dirty = false;
                syncAllTinyMCE();
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
