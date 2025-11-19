document.addEventListener('DOMContentLoaded', function () {
    let lastFocusedAudienceId = null;

    function setupAudienceButtons(container) {
        if (!container || !container.querySelectorAll) {
            return;
        }

        const buttons = container.querySelectorAll('.audience-btn');
        buttons.forEach(btn => {
            if (!btn || btn.dataset.a11yBound === 'true') {
                return;
            }

            btn.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    lastFocusedAudienceId = btn.getAttribute('data-focus-id');
                    htmx.trigger(btn, 'click');
                }
            });

            btn.addEventListener('click', function () {
                lastFocusedAudienceId = btn.getAttribute('data-focus-id');
            });

            btn.dataset.a11yBound = 'true';
        });
    }

    document.body.addEventListener('htmx:afterSwap', function (event) {
        const container = event.target;

        // Only proceed if the container is a valid element
        if (!(container instanceof Element)) {
            return;
        }

        // Only apply if the container includes an audience button
        if (container.querySelector('.audience-btn')) {
            setupAudienceButtons(container);

            if (lastFocusedAudienceId) {
                const btnToFocus = container.querySelector(
                    `.audience-btn[data-focus-id="${lastFocusedAudienceId}"]`
                );
                if (btnToFocus) {
                    btnToFocus.focus();
                }
            }
        }
    });
});
