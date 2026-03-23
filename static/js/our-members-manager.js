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

    function destroyQuoteEditors(listId) {
        if (!window.tinyMCE) return;
        var list = document.getElementById(listId);
        if (!list) return;
        list.querySelectorAll('textarea.quote-tinymce').forEach(function (ta) {
            var editor = tinyMCE.get(ta.id);
            if (editor) {
                editor.save();
                editor.remove();
            }
        });
    }

    function initQuoteEditors(listId) {
        if (!window.tinyMCE) return;
        var list = document.getElementById(listId);
        if (!list) return;
        list.querySelectorAll('textarea.quote-tinymce').forEach(function (ta) {
            // Only init visible rows (not deleted ones)
            var row = ta.closest('.quote-row');
            if (row && row.style.display !== 'none') {
                initTinyMCE(ta);
            }
        });
    }

    // -- Sortable: top quotes -------------------------------------------------

    function initTopQuoteSortable() {
        var list = document.getElementById('top-quote-list');
        if (!list) return;
        Sortable.create(list, {
            handle: '.quote-drag-handle',
            animation: 150,
            onStart: function () {
                destroyQuoteEditors('top-quote-list');
            },
            onEnd: function () {
                initQuoteEditors('top-quote-list');
                updateSortOrders('top-quote-list', '.quote-row');
                markDirty();
            }
        });
    }

    // -- Sortable: bottom quotes ----------------------------------------------

    function initBottomQuoteSortable() {
        var list = document.getElementById('bottom-quote-list');
        if (!list) return;
        Sortable.create(list, {
            handle: '.quote-drag-handle',
            animation: 150,
            onStart: function () {
                destroyQuoteEditors('bottom-quote-list');
            },
            onEnd: function () {
                initQuoteEditors('bottom-quote-list');
                updateSortOrders('bottom-quote-list', '.quote-row');
                markDirty();
            }
        });
    }

    // -- Sortable: institutions -----------------------------------------------

    function initInstitutionSortable() {
        var list = document.getElementById('institution-list');
        if (!list) return;
        Sortable.create(list, {
            handle: '.institution-drag-handle',
            animation: 150,
            onEnd: function () {
                updateSortOrders('institution-list', '.institution-row');
                markDirty();
            }
        });
    }

    // -- Sort order helpers ---------------------------------------------------

    function updateSortOrders(listId, rowSelector) {
        var list = document.getElementById(listId);
        if (!list) return;
        var rows = list.querySelectorAll(rowSelector);
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

    // -- Delete institution ---------------------------------------------------

    function initDeleteInstitution(btn) {
        btn.addEventListener('click', function () {
            if (!confirm('Remove this institution?')) return;
            var row = btn.closest('.institution-row');
            var deleteCheckbox = row.querySelector('input[name$="-DELETE"]');
            if (deleteCheckbox) {
                // Existing row — mark for deletion
                deleteCheckbox.checked = true;
                row.style.display = 'none';
            } else {
                // New row — remove from DOM
                row.remove();
            }
            markDirty();
        });
    }

    // -- Add quote ------------------------------------------------------------

    function addQuote(prefix, listId, templateId) {
        var listEl = document.getElementById(listId);
        var template = document.getElementById(templateId);
        if (!listEl || !template) return;

        var totalForms = document.querySelector('#id_' + prefix + '-TOTAL_FORMS');
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
            textarea.id = 'id_' + prefix + '-' + count + '-quote_text';
            initTinyMCE(textarea);
        }

        markDirty();
    }

    // -- Add institution ------------------------------------------------------

    function addInstitution() {
        var listEl = document.getElementById('institution-list');
        var template = document.getElementById('institution-template');
        if (!listEl || !template) return;

        var totalForms = document.querySelector('#id_institutions-TOTAL_FORMS');
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

        initDeleteInstitution(newRow.querySelector('.btn-delete-institution'));

        markDirty();
    }

    // -- Alphabetize institutions ---------------------------------------------

    function alphabetizeInstitutions() {
        var list = document.getElementById('institution-list');
        if (!list) return;

        var rows = Array.from(list.querySelectorAll('.institution-row'));
        // Only sort visible rows (not deleted)
        var visible = rows.filter(function (row) {
            return row.style.display !== 'none';
        });
        var hidden = rows.filter(function (row) {
            return row.style.display === 'none';
        });

        visible.sort(function (a, b) {
            var nameA = (a.querySelector('input[name$="-name"]') || {}).value || '';
            var nameB = (b.querySelector('input[name$="-name"]') || {}).value || '';
            return nameA.toLowerCase().localeCompare(nameB.toLowerCase());
        });

        // Re-append in sorted order (visible first, then hidden)
        visible.forEach(function (row) { list.appendChild(row); });
        hidden.forEach(function (row) { list.appendChild(row); });

        updateSortOrders('institution-list', '.institution-row');
        markDirty();
    }

    // -- CSV import -----------------------------------------------------------

    function getExistingInstitutionNames() {
        var list = document.getElementById('institution-list');
        if (!list) return [];
        var names = [];
        list.querySelectorAll('.institution-row').forEach(function (row) {
            if (row.style.display === 'none') return;
            var input = row.querySelector('input[name$="-name"]');
            if (input && input.value.trim()) {
                names.push(input.value.trim().toLowerCase());
            }
        });
        return names;
    }

    function handleCSVImport(file) {
        var reader = new FileReader();
        reader.onload = function (e) {
            var text = e.target.result;
            var lines = text.split(/\r?\n/);
            var existingNames = getExistingInstitutionNames();

            lines.forEach(function (line) {
                // Split by comma to handle CSV cells
                var cells = line.split(',');
                cells.forEach(function (cell) {
                    var name = cell.trim();
                    if (!name) return;
                    if (existingNames.indexOf(name.toLowerCase()) !== -1) return;

                    // Add new institution row
                    var listEl = document.getElementById('institution-list');
                    var template = document.getElementById('institution-template');
                    if (!listEl || !template) return;

                    var totalForms = document.querySelector('#id_institutions-TOTAL_FORMS');
                    var count = parseInt(totalForms.value, 10);

                    var newRow = template.content.firstElementChild.cloneNode(true);

                    var allInputs = newRow.querySelectorAll('input, textarea, select');
                    allInputs.forEach(function (el) {
                        if (el.name) el.name = el.name.replace(/__prefix__/g, count);
                        if (el.id) el.id = el.id.replace(/__prefix__/g, count);
                    });
                    var allLabels = newRow.querySelectorAll('label');
                    allLabels.forEach(function (el) {
                        if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/__prefix__/g, count);
                    });

                    var sortInput = newRow.querySelector('input[name$="-sort_order"]');
                    if (sortInput) sortInput.value = count;

                    // Set the name value
                    var nameInput = newRow.querySelector('input[name$="-name"]');
                    if (nameInput) nameInput.value = name;

                    listEl.appendChild(newRow);
                    totalForms.value = count + 1;

                    initDeleteInstitution(newRow.querySelector('.btn-delete-institution'));

                    // Track the new name so duplicates within the CSV are skipped
                    existingNames.push(name.toLowerCase());
                });
            });

            markDirty();
        };
        reader.readAsText(file);
    }

    // -- Init -----------------------------------------------------------------

    document.addEventListener('DOMContentLoaded', function () {
        // Sortables
        initTopQuoteSortable();
        initBottomQuoteSortable();
        initInstitutionSortable();

        // Delete buttons for existing rows
        document.querySelectorAll('.btn-delete-quote').forEach(initDeleteQuote);
        document.querySelectorAll('.btn-delete-institution').forEach(initDeleteInstitution);

        // Add quote buttons
        var addTopQuoteBtn = document.getElementById('btn-add-top-quote');
        if (addTopQuoteBtn) {
            addTopQuoteBtn.addEventListener('click', function () {
                addQuote('top_quotes', 'top-quote-list', 'top-quote-template');
            });
        }

        var addBottomQuoteBtn = document.getElementById('btn-add-bottom-quote');
        if (addBottomQuoteBtn) {
            addBottomQuoteBtn.addEventListener('click', function () {
                addQuote('bottom_quotes', 'bottom-quote-list', 'bottom-quote-template');
            });
        }

        // Add institution button
        var addInstitutionBtn = document.getElementById('btn-add-institution');
        if (addInstitutionBtn) {
            addInstitutionBtn.addEventListener('click', addInstitution);
        }

        // Alphabetize button
        var alphabetizeBtn = document.getElementById('btn-alphabetize-institutions');
        if (alphabetizeBtn) {
            alphabetizeBtn.addEventListener('click', alphabetizeInstitutions);
        }

        // CSV import
        var csvBtn = document.getElementById('btn-csv-import');
        var csvInput = document.getElementById('csv-file-input');
        if (csvBtn && csvInput) {
            csvBtn.addEventListener('click', function () {
                csvInput.click();
            });
            csvInput.addEventListener('change', function () {
                if (csvInput.files && csvInput.files[0]) {
                    handleCSVImport(csvInput.files[0]);
                    // Reset so the same file can be imported again if needed
                    csvInput.value = '';
                }
            });
        }

        // Track edits as dirty
        var form = document.getElementById('our-members-form');
        if (form) {
            form.addEventListener('input', markDirty);

            // Sync TinyMCE and update sort orders on form submit
            form.addEventListener('submit', function () {
                dirty = false;
                syncAllTinyMCE();
                updateSortOrders('top-quote-list', '.quote-row');
                updateSortOrders('bottom-quote-list', '.quote-row');
                updateSortOrders('institution-list', '.institution-row');
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
