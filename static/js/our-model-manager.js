(function () {
    'use strict';

    // ── Helpers ─────────────────────────────────────────────────────────
    var TH_STYLE = 'padding:0.35rem 0.5rem; text-align:left; border-bottom:1px solid var(--border);';
    var TD_STYLE = 'padding:0.25rem 0.5rem;';

    /** Return an array of {id, heading, isNew} for every live (non-deleted) column. */
    function getLiveColumns() {
        var cols = [];
        document.querySelectorAll('#column-formset .column-form-row').forEach(function (row) {
            var delCb = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
            if (delCb && delCb.checked) return;
            var headingInput = row.querySelector('input[name$="-heading"]');
            if (!headingInput) return;
            var idInput = row.querySelector('input[name$="-id"]');
            var colId = (idInput && idInput.value) ? idInput.value : 'new_' + row.dataset.colIndex;
            cols.push({ id: colId, heading: headingInput.value || '(untitled)', isNew: !idInput || !idInput.value });
        });
        return cols;
    }

    /** Rebuild all grid table headers and ensure every row has the right cells. */
    function syncGridsToColumns() {
        var cols = getLiveColumns();
        document.querySelectorAll('.data-grid-table').forEach(function (table) {
            var tablePk = table.dataset.tablePk;
            syncOneGrid(table, tablePk, cols);
        });
    }

    function syncOneGrid(table, tablePk, cols) {
        // Rebuild <thead>
        var headerRow = table.querySelector('thead tr');
        if (!headerRow) return;
        headerRow.innerHTML = '';
        cols.forEach(function (col) {
            var th = document.createElement('th');
            th.className = 'grid-col-header';
            th.dataset.colId = col.id;
            th.style.cssText = TH_STYLE;
            th.textContent = col.heading;
            headerRow.appendChild(th);
        });
        // Actions column
        var thAct = document.createElement('th');
        thAct.style.cssText = TH_STYLE + ' width:60px;';
        headerRow.appendChild(thAct);

        // Sync each body row
        var tbody = table.querySelector('tbody');
        if (!tbody) return;
        tbody.querySelectorAll('tr').forEach(function (tr) {
            syncRowCells(tr, tablePk, cols);
        });
    }

    /** Ensure a <tr> has exactly the right <td>s for the current columns. */
    function syncRowCells(tr, tablePk, cols) {
        // Build a map of existing cells by col-id
        var existingCells = {};
        tr.querySelectorAll('td.grid-cell').forEach(function (td) {
            existingCells[td.dataset.colId] = td;
        });

        // Find the actions <td> (last cell without .grid-cell)
        var actionsTd = tr.querySelector('td:last-child:not(.grid-cell)');

        // Remove all grid-cell TDs
        tr.querySelectorAll('td.grid-cell').forEach(function (td) { td.remove(); });

        // Re-insert in correct order
        cols.forEach(function (col) {
            var td;
            if (existingCells[col.id]) {
                td = existingCells[col.id];
            } else {
                // New column — create empty cell
                td = document.createElement('td');
                td.className = 'grid-cell';
                td.dataset.colId = col.id;
                td.style.cssText = TD_STYLE;
                // Determine the input name prefix based on existing row inputs
                var existingInput = tr.querySelector('td.grid-cell input[type="text"], input[type="text"][name^="cell_"], input[type="text"][name^="new_cell_"]');
                var inputName;
                if (existingInput && existingInput.name.startsWith('new_cell_')) {
                    // New row — use new_cell naming
                    var parts = existingInput.name.split('_');
                    inputName = 'new_cell_' + tablePk + '_' + parts[3] + '_' + col.id;
                } else if (existingInput && existingInput.name.startsWith('cell_')) {
                    var parts2 = existingInput.name.split('_');
                    inputName = 'cell_' + tablePk + '_' + parts2[2] + '_' + col.id;
                } else {
                    // Fallback — shouldn't happen often
                    inputName = 'cell_' + tablePk + '_0_' + col.id;
                }
                td.innerHTML = '<input type="text" name="' + inputName + '" value="" class="mgr-input" style="width:100%;">';
            }
            if (actionsTd) {
                tr.insertBefore(td, actionsTd);
            } else {
                tr.appendChild(td);
            }
        });
    }

    // ── Show/hide custom colour fields based on preset ──────────────────
    function toggleCustomColours(presetSelect) {
        var card = presetSelect.closest('.table-form-card');
        if (!card) return;
        var fields = card.querySelectorAll('.custom-colour-field');
        var show = presetSelect.value === 'custom';
        fields.forEach(function (el) {
            el.style.display = show ? '' : 'none';
        });
    }

    document.querySelectorAll('select[name$="colour_preset"]').forEach(function (sel) {
        toggleCustomColours(sel);
        sel.addEventListener('change', function () {
            toggleCustomColours(this);
        });
    });

    // ── Column heading changes sync to grid headers ─────────────────────
    document.getElementById('column-formset').addEventListener('input', function (e) {
        if (e.target.name && e.target.name.endsWith('-heading')) {
            syncGridsToColumns();
        }
    });

    // Column delete checkbox toggles
    document.getElementById('column-formset').addEventListener('change', function (e) {
        if (e.target.type === 'checkbox' && e.target.name && e.target.name.endsWith('-DELETE')) {
            syncGridsToColumns();
        }
    });

    // ── Add column ──────────────────────────────────────────────────────
    var addColumnBtn = document.getElementById('add-column-btn');
    if (addColumnBtn) {
        addColumnBtn.addEventListener('click', function () {
            var totalInput = document.querySelector('[name="columns-TOTAL_FORMS"]');
            var total = parseInt(totalInput.value, 10);
            var container = document.getElementById('column-formset');
            var div = document.createElement('div');
            div.className = 'column-form-row';
            div.dataset.colId = '';
            div.dataset.colIndex = total;
            div.style.cssText = 'display:flex; gap:0.75rem; align-items:center; margin-bottom:0.5rem;';
            div.innerHTML =
                '<input type="hidden" name="columns-' + total + '-id" value="">' +
                '<input type="hidden" name="columns-' + total + '-sort_order" value="' + total + '">' +
                '<div style="flex:1;"><input type="text" name="columns-' + total + '-heading" class="mgr-input" aria-label="Column heading" placeholder="New column heading"></div>' +
                '<label style="display:flex; align-items:center; gap:0.25rem; font-size:0.8rem; color:var(--muted);">' +
                '<input type="checkbox" name="columns-' + total + '-DELETE"> Delete</label>';
            container.appendChild(div);
            totalInput.value = total + 1;

            // Sync grids to show the new column
            syncGridsToColumns();
        });
    }

    // ── Add table ───────────────────────────────────────────────────────
    var addTableBtn = document.getElementById('add-table-btn');
    if (addTableBtn) {
        addTableBtn.addEventListener('click', function () {
            var totalInput = document.querySelector('[name="tables-TOTAL_FORMS"]');
            var total = parseInt(totalInput.value, 10);
            var wrapper = this.parentElement;
            var div = document.createElement('div');
            div.className = 'table-form-card';
            div.style.cssText = 'border:1px solid var(--border); border-radius:8px; padding:1rem; margin-bottom:1rem;';

            // Build the grid header with current columns
            var cols = getLiveColumns();
            var headerHtml = '';
            cols.forEach(function (col) {
                headerHtml += '<th class="grid-col-header" data-col-id="' + col.id + '" style="' + TH_STYLE + '">' + escapeHtml(col.heading) + '</th>';
            });
            headerHtml += '<th style="' + TH_STYLE + ' width:60px;"></th>';

            div.innerHTML =
                '<input type="hidden" name="tables-' + total + '-id" value="">' +
                '<input type="hidden" name="tables-' + total + '-sort_order" value="' + total + '">' +
                '<div class="mgr-field"><label class="mgr-label">Title</label>' +
                '<input type="text" name="tables-' + total + '-title" class="mgr-input"></div>' +
                '<div class="mgr-field"><label class="mgr-label">Description</label>' +
                '<textarea name="tables-' + total + '-description" class="mgr-textarea" rows="2"></textarea></div>' +
                '<div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:0.75rem; margin-bottom:1rem;">' +
                '<div class="mgr-field" style="margin-bottom:0;"><label class="mgr-label">Colour Preset</label>' +
                '<select name="tables-' + total + '-colour_preset" class="mgr-input">' +
                '<option value="pink">Pink</option><option value="green">Green</option>' +
                '<option value="blue">Blue</option><option value="custom">Custom</option></select></div>' +
                '<div class="mgr-field custom-colour-field" style="margin-bottom:0; display:none;"><label class="mgr-label">Header BG</label>' +
                '<input type="color" name="tables-' + total + '-custom_header_bg" class="mgr-input" style="max-width:80px;"></div>' +
                '<div class="mgr-field custom-colour-field" style="margin-bottom:0; display:none;"><label class="mgr-label">Row BG</label>' +
                '<input type="color" name="tables-' + total + '-custom_row_bg" class="mgr-input" style="max-width:80px;"></div>' +
                '<div class="mgr-field custom-colour-field" style="margin-bottom:0; display:none;"><label class="mgr-label">Text Colour</label>' +
                '<input type="color" name="tables-' + total + '-custom_text_colour" class="mgr-input" style="max-width:80px;"></div></div>' +
                '<div class="mgr-help" style="margin-bottom:0.5rem;">Data Grid</div>' +
                '<div style="overflow-x:auto;">' +
                '<table class="data-grid-table" data-table-pk="new_' + total + '" style="width:100%; border-collapse:collapse; font-size:0.85rem;">' +
                '<thead><tr>' + headerHtml + '</tr></thead>' +
                '<tbody id="grid-new_' + total + '"></tbody></table></div>' +
                '<button type="button" class="btn-mgr-secondary add-row-btn" data-table-pk="new_' + total + '" style="margin-top:0.5rem; font-size:0.8rem;">' +
                '<i class="bi bi-plus"></i> Add Row</button>' +
                '<div class="mgr-help" style="margin-top:0.5rem;">Save the form to persist this table, then add rows.</div>';
            wrapper.insertBefore(div, this);
            totalInput.value = total + 1;

            // Bind colour toggle on new select
            var sel = div.querySelector('select[name$="colour_preset"]');
            if (sel) {
                sel.addEventListener('change', function () {
                    toggleCustomColours(this);
                });
            }
        });
    }

    // ── Add row to an existing table ────────────────────────────────────
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.add-row-btn');
        if (!btn) return;
        var tablePk = btn.dataset.tablePk;
        var tbody = document.getElementById('grid-' + tablePk);
        if (!tbody) return;

        var cols = getLiveColumns();
        if (cols.length === 0) return;

        // Determine new row index (count existing new_ rows for this table)
        var newIdx = 0;
        tbody.querySelectorAll('tr').forEach(function (tr) {
            var inp = tr.querySelector('input[type="text"][name^="new_cell_"]');
            if (inp) newIdx++;
        });

        var tr = document.createElement('tr');
        cols.forEach(function (col) {
            var td = document.createElement('td');
            td.className = 'grid-cell';
            td.dataset.colId = col.id;
            td.style.cssText = TD_STYLE;
            td.innerHTML = '<input type="text" name="new_cell_' + tablePk + '_' + newIdx + '_' + col.id + '" value="" class="mgr-input" style="width:100%;">';
            tr.appendChild(td);
        });
        var delTd = document.createElement('td');
        delTd.style.cssText = TD_STYLE;
        delTd.innerHTML = '<span style="font-size:0.75rem; color:var(--muted);">New</span>';
        tr.appendChild(delTd);
        tbody.appendChild(tr);
    });

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
})();
