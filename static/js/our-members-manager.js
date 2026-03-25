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

    function destroyAllEditors() {
        if (!window.tinyMCE) return;
        document.querySelectorAll('#block-list textarea').forEach(function (ta) {
            if (!ta.id) return;
            var editor = tinyMCE.get(ta.id);
            if (editor) {
                editor.save();
                editor.remove();
            }
        });
    }

    function reinitAllEditors() {
        if (!window.tinyMCE) return;
        document.querySelectorAll('#block-list textarea[id]').forEach(function (ta) {
            var row = ta.closest('.quote-row');
            if (row && isRowHidden(row)) return;
            if (tinyMCE.get(ta.id)) return;
            initTinyMCE(ta);
        });
    }

    function destroyEditorsIn(container) {
        if (!window.tinyMCE || !container) return;
        container.querySelectorAll('textarea').forEach(function (ta) {
            if (!ta.id) return;
            var editor = tinyMCE.get(ta.id);
            if (editor) {
                editor.save();
                editor.remove();
            }
        });
    }

    function initEditorsIn(container) {
        if (!window.tinyMCE || !container) return;
        container.querySelectorAll('textarea[id]').forEach(function (ta) {
            var row = ta.closest('.quote-row');
            if (row && isRowHidden(row)) return;
            if (tinyMCE.get(ta.id)) return;
            initTinyMCE(ta);
        });
    }

    // -- Sort order helpers ---------------------------------------------------

    function updateSortOrders(listEl, rowSelector) {
        if (!listEl) return;
        var rows = listEl.querySelectorAll(rowSelector);
        rows.forEach(function (row, idx) {
            var input = row.querySelector('input[name$="-sort_order"]');
            if (input) input.value = idx;
        });
    }

    // -- Row visibility helpers -----------------------------------------------

    function isRowHidden(row) {
        return row.style.display === 'none' || row.classList.contains('d-none');
    }

    function hideRow(row) {
        row.classList.add('d-none');
        row.classList.remove('d-flex');
        row.style.display = 'none';
    }

    // -- Delete quote ---------------------------------------------------------

    function initDeleteQuote(btn) {
        btn.addEventListener('click', function () {
            if (!confirm('Remove this quote?')) return;
            var row = btn.closest('.quote-row');
            var deleteCheckbox = row.querySelector('input[name$="-DELETE"]');
            if (deleteCheckbox) {
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
                deleteCheckbox.checked = true;
                hideRow(row);
            } else {
                row.remove();
            }
            markDirty();
        });
    }

    // -- Add quote (scoped by block) ------------------------------------------

    function addQuoteToBlock(blockCard) {
        var template = blockCard.querySelector('.quote-template');
        var listEl = blockCard.querySelector('.quote-list');
        if (!template || !listEl) return;

        var prefix = template.dataset.prefix;
        var totalForms = blockCard.querySelector('input[name="' + prefix + '-TOTAL_FORMS"]');
        if (!totalForms) return;
        var count = parseInt(totalForms.value, 10);

        var newRow = template.content.firstElementChild.cloneNode(true);

        newRow.querySelectorAll('input, textarea, select').forEach(function (el) {
            if (el.name) el.name = el.name.replace(/__prefix__/g, count);
            if (el.id) el.id = el.id.replace(/__prefix__/g, count);
        });
        newRow.querySelectorAll('label').forEach(function (el) {
            if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/__prefix__/g, count);
        });

        var sortInput = newRow.querySelector('input[name$="-sort_order"]');
        if (sortInput) sortInput.value = count;

        listEl.appendChild(newRow);
        totalForms.value = count + 1;

        initDeleteQuote(newRow.querySelector('.btn-delete-quote'));

        var textarea = newRow.querySelector('textarea.quote-tinymce');
        if (textarea) {
            textarea.id = 'id_' + prefix + '-' + count + '-quote_text';
            initTinyMCE(textarea);
        }

        markDirty();
    }

    // -- Add institution (scoped by block) ------------------------------------

    function addInstitutionToBlock(blockCard) {
        var template = blockCard.querySelector('.institution-template');
        var listEl = blockCard.querySelector('.institution-list');
        if (!template || !listEl) return;

        var prefix = template.dataset.prefix;
        var totalForms = blockCard.querySelector('input[name="' + prefix + '-TOTAL_FORMS"]');
        if (!totalForms) return;
        var count = parseInt(totalForms.value, 10);

        var newRow = template.content.firstElementChild.cloneNode(true);

        newRow.querySelectorAll('input, textarea, select').forEach(function (el) {
            if (el.name) el.name = el.name.replace(/__prefix__/g, count);
            if (el.id) el.id = el.id.replace(/__prefix__/g, count);
        });
        newRow.querySelectorAll('label').forEach(function (el) {
            if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/__prefix__/g, count);
        });

        var sortInput = newRow.querySelector('input[name$="-sort_order"]');
        if (sortInput) sortInput.value = count;

        listEl.appendChild(newRow);
        totalForms.value = count + 1;

        initDeleteInstitution(newRow.querySelector('.btn-delete-institution'));

        markDirty();
    }

    // -- Alphabetize institutions (scoped by block) ---------------------------

    function alphabetizeInstitutions(blockCard) {
        var list = blockCard.querySelector('.institution-list');
        if (!list) return;

        var rows = Array.from(list.querySelectorAll('.institution-row'));
        var visible = rows.filter(function (row) { return !isRowHidden(row); });
        var hidden = rows.filter(function (row) { return isRowHidden(row); });

        visible.sort(function (a, b) {
            var nameA = (a.querySelector('input[name$="-name"]') || {}).value || '';
            var nameB = (b.querySelector('input[name$="-name"]') || {}).value || '';
            return nameA.toLowerCase().localeCompare(nameB.toLowerCase());
        });

        visible.forEach(function (row) { list.appendChild(row); });
        hidden.forEach(function (row) { list.appendChild(row); });

        updateSortOrders(list, '.institution-row');
        markDirty();
    }

    // -- CSV import (scoped by block) -----------------------------------------

    function getExistingInstitutionNames(blockCard) {
        var list = blockCard.querySelector('.institution-list');
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

    function addInstitutionRow(blockCard, name, existingNames) {
        var template = blockCard.querySelector('.institution-template');
        var listEl = blockCard.querySelector('.institution-list');
        if (!template || !listEl) return;

        var prefix = template.dataset.prefix;
        var totalForms = blockCard.querySelector('input[name="' + prefix + '-TOTAL_FORMS"]');
        if (!totalForms) return;
        var count = parseInt(totalForms.value, 10);

        var newRow = template.content.firstElementChild.cloneNode(true);

        newRow.querySelectorAll('input, textarea, select').forEach(function (el) {
            if (el.name) el.name = el.name.replace(/__prefix__/g, count);
            if (el.id) el.id = el.id.replace(/__prefix__/g, count);
        });
        newRow.querySelectorAll('label').forEach(function (el) {
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

    function handleCSVImport(blockCard, file) {
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
            var existingNames = getExistingInstitutionNames(blockCard);
            (data.names || []).forEach(function (name) {
                if (existingNames.indexOf(name.toLowerCase()) !== -1) return;
                addInstitutionRow(blockCard, name, existingNames);
            });
            markDirty();
        })
        .catch(function () {
            alert('CSV import failed. Please check the file format.');
        });
    }

    // -- Block visibility toggle ----------------------------------------------

    function applyBlockVisibility(card) {
        var checkbox = card.querySelector('.block-visible-check');
        var content = card.querySelector('[data-block-content]');
        if (!checkbox || !content) return;
        if (checkbox.checked) {
            content.classList.remove('section-disabled');
        } else {
            content.classList.add('section-disabled');
        }
    }

    // -- CTA visibility toggle ------------------------------------------------

    function applyCTAToggle(checkbox) {
        var card = checkbox.closest('.section-card') || checkbox.closest('[data-block-content]');
        if (!card) return;
        var ctaContent = card.querySelector('[data-cta-content]');
        if (!ctaContent) return;
        if (checkbox.checked) {
            ctaContent.classList.remove('section-disabled');
        } else {
            ctaContent.classList.add('section-disabled');
        }
    }

    // -- Colour reset ---------------------------------------------------------

    function initColorReset(btn) {
        btn.addEventListener('click', function () {
            var card = btn.closest('.section-card');
            if (!card) return;
            var defaults;
            try {
                defaults = JSON.parse(card.dataset.colorDefaults || '{}');
            } catch (e) {
                return;
            }
            Object.keys(defaults).forEach(function (key) {
                var input = card.querySelector('input[name$="-' + key + '"]');
                if (input) input.value = defaults[key];
            });
            markDirty();
        });
    }

    // -- Block deletion (server-side) -----------------------------------------

    function deleteBlock(btn) {
        if (!confirm('Delete this block? Any unsaved changes on this page will also be saved.')) return;
        var card = btn.closest('.section-card');
        if (!card) return;
        var pk = parseInt(card.dataset.blockPk, 10);
        var form = document.getElementById('delete-block-form');
        if (!form) return;
        // Build the URL by replacing the placeholder "0" at the end
        var baseUrl = form.dataset.baseUrl;
        form.action = baseUrl.replace(/\/0\/$/, '/' + pk + '/');
        dirty = false; // suppress beforeunload warning
        form.submit();
    }

    // -- Block order ----------------------------------------------------------

    function updateBlockOrder() {
        var list = document.getElementById('block-list');
        var input = document.getElementById('block-order-field');
        if (!list || !input) return;
        var order = [];
        list.querySelectorAll('.section-card[data-block-pk]').forEach(function (card) {
            // Skip deleted blocks
            if (card.classList.contains('block-deleted')) return;
            var checkbox = card.querySelector('.block-visible-check');
            order.push({
                pk: parseInt(card.dataset.blockPk, 10),
                visible: checkbox ? checkbox.checked : true
            });
        });
        input.value = JSON.stringify(order);
    }

    // -- Block-level Sortable -------------------------------------------------

    function initBlockSortable() {
        var list = document.getElementById('block-list');
        if (!list) return;
        Sortable.create(list, {
            handle: '.section-drag-handle',
            animation: 150,
            draggable: '.section-card:not(.block-deleted)',
            ghostClass: 'sortable-ghost',
            onStart: function () {
                destroyAllEditors();
            },
            onEnd: function () {
                reinitAllEditors();
                updateBlockOrder();
                markDirty();
            }
        });
    }

    // -- Per-block child Sortables --------------------------------------------

    function initChildSortables() {
        // Quote lists
        document.querySelectorAll('.quote-list').forEach(function (list) {
            Sortable.create(list, {
                handle: '.quote-drag-handle',
                animation: 150,
                onStart: function () {
                    destroyEditorsIn(list);
                },
                onEnd: function () {
                    initEditorsIn(list);
                    updateSortOrders(list, '.quote-row');
                    markDirty();
                }
            });
        });

        // Institution lists
        document.querySelectorAll('.institution-list').forEach(function (list) {
            Sortable.create(list, {
                handle: '.institution-drag-handle',
                animation: 150,
                onEnd: function () {
                    updateSortOrders(list, '.institution-row');
                    markDirty();
                }
            });
        });
    }

    // -- Delete block ---------------------------------------------------------

    function initDeleteBlock() {
        document.querySelectorAll('.block-delete-btn[data-delete-block-pk]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                deleteBlock(btn);
            });
        });
    }

    // -- Add block ------------------------------------------------------------

    function initAddBlock() {
        document.querySelectorAll('.add-block-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var blockType = btn.dataset.blockType;
                var typeInput = document.getElementById('add-block-type');
                var form = document.getElementById('add-block-form');
                if (typeInput && form) {
                    typeInput.value = blockType;
                    form.submit();
                }
            });
        });
    }

    // -- Reset page defaults --------------------------------------------------

    function initResetDefaults() {
        var btn = document.getElementById('btn-reset-page-defaults');
        var form = document.getElementById('reset-defaults-form');
        if (!btn || !form) return;
        btn.addEventListener('click', function () {
            if (confirm('Reset the entire page to defaults? All current blocks will be deleted.')) {
                form.submit();
            }
        });
    }

    // -- Init -----------------------------------------------------------------

    document.addEventListener('DOMContentLoaded', function () {
        var formEl = document.getElementById('our-members-form');
        if (formEl) CSV_PARSE_URL = formEl.dataset.csvParseUrl || '';

        // Block visibility toggles
        document.querySelectorAll('.section-card').forEach(function (card) {
            applyBlockVisibility(card);
            var checkbox = card.querySelector('.block-visible-check');
            if (checkbox) {
                checkbox.addEventListener('change', function () {
                    applyBlockVisibility(card);
                    markDirty();
                });
            }
        });

        // CTA toggles (show_cta checkboxes within blocks)
        document.querySelectorAll('input[name$="-show_cta"]').forEach(function (cb) {
            applyCTAToggle(cb);
            cb.addEventListener('change', function () {
                applyCTAToggle(cb);
                markDirty();
            });
        });

        // Colour reset buttons
        document.querySelectorAll('.btn-reset-colors').forEach(initColorReset);

        // Block-level sortable
        initBlockSortable();
        updateBlockOrder();

        // Per-block child sortables
        initChildSortables();

        // Delete buttons for existing rows
        document.querySelectorAll('.btn-delete-quote').forEach(initDeleteQuote);
        document.querySelectorAll('.btn-delete-institution').forEach(initDeleteInstitution);

        // Add quote buttons (scoped per block)
        document.querySelectorAll('.btn-add-quote').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var card = btn.closest('.section-card');
                if (card) addQuoteToBlock(card);
            });
        });

        // Add institution buttons (scoped per block)
        document.querySelectorAll('.btn-add-institution').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var card = btn.closest('.section-card');
                if (card) addInstitutionToBlock(card);
            });
        });

        // Alphabetize buttons (scoped per block)
        document.querySelectorAll('.btn-alphabetize-institutions').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var card = btn.closest('.section-card');
                if (card) alphabetizeInstitutions(card);
            });
        });

        // CSV import (scoped per block)
        document.querySelectorAll('.btn-csv-import').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var card = btn.closest('.section-card');
                if (!card) return;
                var csvInput = card.querySelector('.csv-file-input');
                if (csvInput) csvInput.click();
            });
        });
        document.querySelectorAll('.csv-file-input').forEach(function (csvInput) {
            csvInput.addEventListener('change', function () {
                if (csvInput.files && csvInput.files[0]) {
                    var card = csvInput.closest('.section-card');
                    if (card) handleCSVImport(card, csvInput.files[0]);
                    csvInput.value = '';
                }
            });
        });

        // Delete block confirmation
        initDeleteBlock();

        // Add block dropdown
        initAddBlock();

        // Reset page defaults
        initResetDefaults();

        // Track edits as dirty
        var form = document.getElementById('our-members-form');
        if (form) {
            form.addEventListener('input', markDirty);

            form.addEventListener('submit', function () {
                dirty = false;
                syncAllTinyMCE();
                // Update sort orders for all child lists
                document.querySelectorAll('.quote-list').forEach(function (list) {
                    updateSortOrders(list, '.quote-row');
                });
                document.querySelectorAll('.institution-list').forEach(function (list) {
                    updateSortOrders(list, '.institution-row');
                });
                updateBlockOrder();
            });
        }

        // Warn on navigation with unsaved changes
        window.addEventListener('beforeunload', function (e) {
            if (dirty && !window._suppressBeforeUnload) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    });
})();
