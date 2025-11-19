document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menu-toggle');
    const closeNav = document.getElementById('close-nav');
    const fullscreenNav = document.getElementById('fullscreen-nav');
    const navLinks = document.querySelectorAll('.nav-link');

    if (menuToggle && fullscreenNav) {
        menuToggle.addEventListener('click', function () {
            fullscreenNav.classList.add('active');
            document.body.style.overflow = 'hidden';
        });

        // Keyboard accessibility for toggle
        menuToggle.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                menuToggle.click();
            }
        });
    }

    if (closeNav && fullscreenNav) {
        closeNav.addEventListener('click', function () {
            fullscreenNav.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    navLinks.forEach(link => {
        link.addEventListener('click', function () {
            fullscreenNav.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
});