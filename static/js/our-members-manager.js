(function () {
    'use strict';

    var dirty = false;
    var CSV_PARSE_URL = '';

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
            if (row && !isRowHidden(row)) {
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

    function isRowHidden(row) {
        return row.style.display === 'none' || row.classList.contains('d-none');
    }

    function hideRow(row) {
        // Bootstrap utility classes like .d-flex use !important, so
        // row.style.display='none' alone is overridden. Add d-none and
        // remove d-flex to ensure the row is hidden.
        row.classList.add('d-none');
        row.classList.remove('d-flex');
        row.style.display = 'none';
    }

    function initDeleteInstitution(btn) {
        btn.addEventListener('click', function () {
            if (!confirm('Remove this institution?')) return;
            var row = btn.closest('.institution-row');
            var deleteCheckbox = row.querySelector('input[name$="-DELETE"]');
            if (deleteCheckbox) {
                // Existing row — mark for deletion
                deleteCheckbox.checked = true;
                hideRow(row);
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
            return !isRowHidden(row);
        });
        var hidden = rows.filter(function (row) {
            return isRowHidden(row);
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
            if (isRowHidden(row)) return;
            var input = row.querySelector('input[name$="-name"]');
            if (input && input.value.trim()) {
                names.push(input.value.trim().toLowerCase());
            }
        });
        return names;
    }

    function addInstitutionRow(name, existingNames) {
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

        var nameInput = newRow.querySelector('input[name$="-name"]');
        if (nameInput) nameInput.value = name;

        listEl.appendChild(newRow);
        totalForms.value = count + 1;

        initDeleteInstitution(newRow.querySelector('.btn-delete-institution'));

        existingNames.push(name.toLowerCase());
    }

    function handleCSVImport(file) {
        var formData = new FormData();
        formData.append('file', file);

        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        fetch(CSV_PARSE_URL, {
            method: 'POST',
            headers: {'X-CSRFToken': csrfToken ? csrfToken.value : ''},
            body: formData
        })
        .then(function (resp) { return resp.json(); })
        .then(function (data) {
            if (data.error) {
                alert('CSV import error: ' + data.error);
                return;
            }
            var existingNames = getExistingInstitutionNames();
            (data.names || []).forEach(function (name) {
                if (existingNames.indexOf(name.toLowerCase()) !== -1) return;
                addInstitutionRow(name, existingNames);
            });
            markDirty();
        })
        .catch(function () {
            alert('CSV import failed. Please check the file format.');
        });
    }

    // -- Section visibility toggles -------------------------------------------

    function applySectionToggle(checkbox) {
        var fieldName = checkbox.name;
        var content = document.querySelector('[data-section-content="' + fieldName + '"]');
        if (!content) return;
        if (checkbox.checked) {
            content.classList.remove('section-disabled');
        } else {
            content.classList.add('section-disabled');
        }
    }

    function initSectionToggles() {
        var checkboxes = document.querySelectorAll(
            'input[name="show_header"],' +
            'input[name="show_who_we_are"],' +
            'input[name="show_who_we_are_cta"],' +
            'input[name="show_top_carousel"],' +
            'input[name="show_members_grid"],' +
            'input[name="show_members_grid_cta"],' +
            'input[name="show_bottom_carousel"]'
        );
        checkboxes.forEach(function (cb) {
            // Apply initial state
            applySectionToggle(cb);
            // Listen for changes
            cb.addEventListener('change', function () {
                applySectionToggle(cb);
                markDirty();
            });
        });
    }

    // -- Section reordering ---------------------------------------------------

    function destroyAllEditors() {
        if (!window.tinyMCE) return;
        document.querySelectorAll('#section-list textarea.quote-tinymce').forEach(function (ta) {
            var editor = tinyMCE.get(ta.id);
            if (editor) {
                editor.save();
                editor.remove();
            }
        });
        // Also destroy the Who We Are TinyMCE editors (circle bodies)
        document.querySelectorAll('#section-list .tox-tinymce').forEach(function (wrapper) {
            var ta = wrapper.previousElementSibling;
            if (ta && ta.tagName === 'TEXTAREA' && !ta.classList.contains('quote-tinymce')) {
                var editor = tinyMCE.get(ta.id);
                if (editor) {
                    editor.save();
                    editor.remove();
                }
            }
        });
    }

    function reinitAllEditors() {
        if (!window.tinyMCE) return;
        // Reinit all TinyMCE instances that Django rendered (they have IDs)
        document.querySelectorAll('#section-list textarea[id]').forEach(function (ta) {
            // Skip textareas in hidden (deleted) rows
            var row = ta.closest('.quote-row');
            if (row && isRowHidden(row)) return;
            // Skip if already initialized
            if (tinyMCE.get(ta.id)) return;
            // Only init textareas that had TinyMCE (they have mce-related classes or were TinyMCE targets)
            if (ta.classList.contains('quote-tinymce') || ta.id.match(/id_circle_\d+_body/)) {
                initTinyMCE(ta);
            }
        });
        // Re-init quote editors in both lists
        initQuoteEditors('top-quote-list');
        initQuoteEditors('bottom-quote-list');
    }

    function updateSectionOrder() {
        var list = document.getElementById('section-list');
        var input = document.getElementById('id_section_order');
        if (!list || !input) return;
        var order = [];
        list.querySelectorAll('.section-card[data-section-key]').forEach(function (card) {
            order.push(card.dataset.sectionKey);
        });
        input.value = JSON.stringify(order);
    }

    function initSectionSortable() {
        var list = document.getElementById('section-list');
        if (!list) return;
        Sortable.create(list, {
            handle: '.section-drag-handle',
            animation: 150,
            draggable: '.section-card',
            ghostClass: 'sortable-ghost',
            onStart: function () {
                destroyAllEditors();
            },
            onEnd: function () {
                reinitAllEditors();
                updateSectionOrder();
                markDirty();
            }
        });
    }

    // -- Init -----------------------------------------------------------------

    document.addEventListener('DOMContentLoaded', function () {
        var formEl = document.getElementById('our-members-form');
        if (formEl) CSV_PARSE_URL = formEl.dataset.csvParseUrl || '';

        // Section visibility toggles
        initSectionToggles();

        // Section reordering — restore saved order from hidden field
        var sectionOrderInput = document.getElementById('id_section_order');
        var sectionList = document.getElementById('section-list');
        if (sectionOrderInput && sectionList && sectionOrderInput.value) {
            try {
                var savedOrder = JSON.parse(sectionOrderInput.value);
                if (Array.isArray(savedOrder) && savedOrder.length) {
                    savedOrder.forEach(function (key) {
                        var card = sectionList.querySelector('.section-card[data-section-key="' + key + '"]');
                        if (card) sectionList.appendChild(card);
                    });
                }
            } catch (e) {
                // ignore parse errors
            }
        }
        initSectionSortable();
        updateSectionOrder();

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
                updateSectionOrder();
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
