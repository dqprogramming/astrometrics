document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menu-toggle');
    const closeNav = document.getElementById('close-nav');
    const fullscreenNav = document.getElementById('fullscreen-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    const dropdownTrigger = document.querySelector('.landing-nav-dropdown > .landing-nav-link');
    const dropdown = document.querySelector('.landing-nav-dropdown');

    // --- Dropdown aria-expanded + Escape to close ---
    if (dropdownTrigger && dropdown) {
        dropdown.addEventListener('mouseenter', function () {
            dropdown.classList.remove('dropdown-closed');
            dropdownTrigger.setAttribute('aria-expanded', 'true');
        });
        dropdown.addEventListener('mouseleave', function () {
            dropdownTrigger.setAttribute('aria-expanded', 'false');
        });
        dropdown.addEventListener('focusin', function () {
            dropdown.classList.remove('dropdown-closed');
            dropdownTrigger.setAttribute('aria-expanded', 'true');
        });
        dropdown.addEventListener('focusout', function (e) {
            if (!dropdown.contains(e.relatedTarget)) {
                dropdown.classList.remove('dropdown-closed');
                dropdownTrigger.setAttribute('aria-expanded', 'false');
            }
        });
        dropdown.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                dropdown.classList.add('dropdown-closed');
                dropdownTrigger.setAttribute('aria-expanded', 'false');
                dropdownTrigger.focus();
                return;
            }

            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                var items = dropdown.querySelectorAll('.landing-dropdown-item, .landing-dropdown-cta');
                if (items.length === 0) return;

                var currentIndex = Array.prototype.indexOf.call(items, document.activeElement);

                if (e.key === 'ArrowDown') {
                    // If on trigger or not in the menu yet, go to first item
                    var nextIndex = currentIndex < 0 ? 0 : Math.min(currentIndex + 1, items.length - 1);
                    items[nextIndex].focus();
                } else {
                    // ArrowUp: if on first item or trigger, focus trigger
                    if (currentIndex <= 0) {
                        dropdownTrigger.focus();
                    } else {
                        items[currentIndex - 1].focus();
                    }
                }
            }
        });
    }

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

        menuToggle.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openMenu();
            }
        });
    }

    // --- Close button ---
    if (closeNav && fullscreenNav) {
        closeNav.addEventListener('click', closeMenu);

        closeNav.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                closeMenu();
            }
        });
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
                    'a[href], button, [tabindex]:not([tabindex="-1"]), [role="button"]'
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

    // --- Focus trap within fullscreen nav ---
    if (fullscreenNav) {
        fullscreenNav.addEventListener('keydown', function (event) {
            if (event.key !== 'Tab') return;

            var focusable = fullscreenNav.querySelectorAll(
                'a[href], button, [tabindex]:not([tabindex="-1"]), [role="button"]'
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
