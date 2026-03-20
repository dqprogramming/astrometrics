(function () {
    'use strict';

    // ── Helpers ─────────────────────────────────────────────────────────────

    function setPreviewImage(preview, url) {
        while (preview.firstChild) preview.removeChild(preview.firstChild);
        var img = document.createElement('img');
        img.src = url;
        img.style.cssText = 'width:100%;height:100%;object-fit:cover;';
        img.alt = 'Team member photo';
        preview.appendChild(img);
    }

    function setPreviewPlaceholder(preview) {
        while (preview.firstChild) preview.removeChild(preview.firstChild);
        var icon = document.createElement('i');
        icon.className = 'bi bi-person-square';
        icon.style.cssText = 'font-size:1.5rem;color:#999;';
        preview.appendChild(icon);
    }

    // ── Sortable: sections ──────────────────────────────────────────────────

    function initSectionSortable() {
        var list = document.getElementById('section-list');
        if (!list) return;
        Sortable.create(list, {
            handle: '.section-drag-handle',
            animation: 150,
            onEnd: function () {
                var cards = list.querySelectorAll('.section-card');
                cards.forEach(function (card, idx) {
                    var input = card.querySelector('.section-sort-order');
                    if (input) input.value = idx;
                });
            }
        });
    }

    // ── Sortable: members within each section ───────────────────────────────

    function initMemberSortable(listEl) {
        if (!listEl) return;
        Sortable.create(listEl, {
            handle: '.member-drag-handle',
            animation: 150,
            onEnd: function () {
                updateMemberSortOrders(listEl);
            }
        });
    }

    function updateMemberSortOrders(listEl) {
        var rows = listEl.querySelectorAll('.member-row');
        rows.forEach(function (row, idx) {
            var input = row.querySelector('input[name$="-sort_order"]');
            if (input) input.value = idx;
        });
    }

    // ── Delete section ──────────────────────────────────────────────────────

    window.deleteSection = function (pk) {
        if (!confirm('Delete this entire section and all its members? This cannot be undone.')) return;
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/manager/cms/our-team/section/' + pk + '/delete/';
        var csrf = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrf) {
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = csrf.value;
            form.appendChild(input);
        }
        document.body.appendChild(form);
        form.submit();
    };

    // ── Delete member ───────────────────────────────────────────────────────

    function initDeleteMember(btn) {
        btn.addEventListener('click', function () {
            if (!confirm('Remove this team member? This cannot be undone.')) return;
            var row = btn.closest('.member-row');
            var deleteCheckbox = row.querySelector('input[name$="-DELETE"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                row.style.display = 'none';
            } else {
                row.remove();
            }
        });
    }

    // ── Add member ──────────────────────────────────────────────────────────

    function addMember(sectionPk, prefix) {
        var listEl = document.getElementById('member-list-' + sectionPk);
        var template = document.getElementById('member-template-' + sectionPk);
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

        // Update data-target on file inputs
        var fileInputs = newRow.querySelectorAll('.member-image-file');
        fileInputs.forEach(function (el) {
            if (el.dataset.target) {
                el.dataset.target = el.dataset.target.replace(/__prefix__/g, count);
            }
        });

        // Set sort order
        var sortInput = newRow.querySelector('input[name$="-sort_order"]');
        if (sortInput) sortInput.value = count;

        listEl.appendChild(newRow);
        totalForms.value = count + 1;

        initDeleteMember(newRow.querySelector('.btn-delete-member'));
        initImageUpload(newRow.querySelector('.member-image-file'));

        var firstInput = newRow.querySelector('input[type="text"]');
        if (firstInput) firstInput.focus();
    }

    // ── Image upload ────────────────────────────────────────────────────────

    function initImageUpload(fileInput) {
        if (!fileInput) return;
        fileInput.addEventListener('change', function () {
            var file = fileInput.files[0];
            if (!file) return;

            var formData = new FormData();
            formData.append('image', file);

            var targetId = fileInput.dataset.target;
            var hiddenInput = document.getElementById(targetId);

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/manager/cms/our-team/member-image-upload/');
            var csrf = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrf) xhr.setRequestHeader('X-CSRFToken', csrf.value);

            xhr.onload = function () {
                if (xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    if (hiddenInput) hiddenInput.value = data.url;

                    var row = fileInput.closest('.member-row');
                    if (row) {
                        var preview = row.querySelector('.team-image-preview');
                        if (preview) setPreviewImage(preview, data.url);
                    }
                }
            };
            xhr.send(formData);
        });
    }

    // ── Clear image ─────────────────────────────────────────────────────────

    function initClearImage(btn) {
        btn.addEventListener('click', function () {
            var targetId = btn.dataset.target;
            var hiddenInput = document.getElementById(targetId);
            if (hiddenInput) hiddenInput.value = '';

            var row = btn.closest('.member-row');
            if (row) {
                var preview = row.querySelector('.team-image-preview');
                if (preview) setPreviewPlaceholder(preview);
            }
            btn.remove();
        });
    }

    // ── Init ────────────────────────────────────────────────────────────────

    document.addEventListener('DOMContentLoaded', function () {
        initSectionSortable();

        document.querySelectorAll('.member-list').forEach(initMemberSortable);
        document.querySelectorAll('.btn-delete-member').forEach(initDeleteMember);
        document.querySelectorAll('.member-image-file').forEach(initImageUpload);
        document.querySelectorAll('.btn-clear-image').forEach(initClearImage);

        document.querySelectorAll('.btn-add-member').forEach(function (btn) {
            btn.addEventListener('click', function () {
                addMember(btn.dataset.sectionPk, btn.dataset.prefix);
            });
        });

        // Update sort orders on form submit
        var form = document.getElementById('our-team-form');
        if (form) {
            form.addEventListener('submit', function () {
                document.querySelectorAll('.member-list').forEach(updateMemberSortOrders);
            });
        }
    });
})();
