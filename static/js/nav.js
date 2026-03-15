document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menu-toggle');
    const closeNav = document.getElementById('close-nav');
    const fullscreenNav = document.getElementById('fullscreen-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    // --- Dropdown aria-expanded + Escape to close ---
    document.querySelectorAll('.landing-nav-dropdown').forEach(function (dropdown) {
        var trigger = dropdown.querySelector('.landing-nav-link');
        if (!trigger) return;

        var escapedDropdown = false;

        dropdown.addEventListener('mouseenter', function () {
            dropdown.classList.remove('dropdown-closed');
            trigger.setAttribute('aria-expanded', 'true');
        });
        dropdown.addEventListener('mouseleave', function () {
            trigger.setAttribute('aria-expanded', 'false');
        });
        dropdown.addEventListener('focusin', function () {
            if (escapedDropdown) {
                escapedDropdown = false;
                return;
            }
            dropdown.classList.remove('dropdown-closed');
            trigger.setAttribute('aria-expanded', 'true');
        });
        dropdown.addEventListener('focusout', function (e) {
            if (!dropdown.contains(e.relatedTarget)) {
                dropdown.classList.remove('dropdown-closed');
                trigger.setAttribute('aria-expanded', 'false');
            }
        });
        dropdown.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                escapedDropdown = true;
                dropdown.classList.add('dropdown-closed');
                trigger.setAttribute('aria-expanded', 'false');
                trigger.focus();
                return;
            }

            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                var items = dropdown.querySelectorAll('.landing-dropdown-item, .landing-dropdown-cta');
                if (items.length === 0) return;

                var currentIndex = Array.prototype.indexOf.call(items, document.activeElement);

                if (e.key === 'ArrowDown') {
                    var nextIndex = currentIndex < 0 ? 0 : Math.min(currentIndex + 1, items.length - 1);
                    items[nextIndex].focus();
                } else {
                    if (currentIndex <= 0) {
                        trigger.focus();
                    } else {
                        items[currentIndex - 1].focus();
                    }
                }
            }
        });
    });

    // --- Mobile menu open/close helpers ---
    function openMenu() {
        fullscreenNav.classList.add('active');
        fullscreenNav.setAttribute('aria-hidden', 'false');
        menuToggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
        fullscreenNav.addEventListener('transitionend', function handler() {
            fullscreenNav.removeEventListener('transitionend', handler);
            closeNav.focus();
        });
    }

    function closeMenu() {
        fullscreenNav.classList.remove('active');
        fullscreenNav.setAttribute('aria-hidden', 'true');
        menuToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        menuToggle.focus();
    }

    // --- Menu toggle (hamburger) ---
    if (menuToggle && fullscreenNav) {
        menuToggle.addEventListener('click', openMenu);
    }

    // --- Close button ---
    if (closeNav && fullscreenNav) {
        closeNav.addEventListener('click', closeMenu);
    }

    // --- Close on nav link click ---
    navLinks.forEach(function (link) {
        link.addEventListener('click', closeMenu);
    });

    // --- Escape key closes menu ---
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && fullscreenNav && fullscreenNav.classList.contains('active')) {
            closeMenu();
        }
    });

    // --- Arrow key navigation within fullscreen nav ---
    if (fullscreenNav) {
        fullscreenNav.addEventListener('keydown', function (event) {
            if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
                var items = fullscreenNav.querySelectorAll(
                    'a[href], button, [tabindex]:not([tabindex="-1"])'
                );
                if (items.length === 0) return;

                var currentIndex = Array.prototype.indexOf.call(items, document.activeElement);

                if (event.key === 'ArrowDown') {
                    event.preventDefault();
                    var nextIndex = currentIndex < 0 ? 0 : Math.min(currentIndex + 1, items.length - 1);
                    items[nextIndex].focus();
                } else {
                    event.preventDefault();
                    var prevIndex = currentIndex <= 0 ? 0 : currentIndex - 1;
                    items[prevIndex].focus();
                }
            }
        });
    }

    // --- Mobile accordion toggles ---
    document.querySelectorAll('.mobile-nav-toggle').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var expanded = btn.getAttribute('aria-expanded') === 'true';
            btn.setAttribute('aria-expanded', !expanded);
            var submenu = btn.nextElementSibling;
            if (submenu) {
                submenu.hidden = expanded;
            }
        });
    });

    // --- Focus trap within fullscreen nav ---
    if (fullscreenNav) {
        fullscreenNav.addEventListener('keydown', function (event) {
            if (event.key !== 'Tab') return;

            var focusable = fullscreenNav.querySelectorAll(
                'a[href], button, [tabindex]:not([tabindex="-1"])'
            );
            if (focusable.length === 0) return;

            var first = focusable[0];
            var last = focusable[focusable.length - 1];

            if (event.shiftKey) {
                if (document.activeElement === first) {
                    event.preventDefault();
                    last.focus();
                }
            } else {
                if (document.activeElement === last) {
                    event.preventDefault();
                    first.focus();
                }
            }
        });
    }
});
