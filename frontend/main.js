(function() {
    const burger = document.querySelector('.nav__burger');
    const mobileMenu = document.getElementById('mobile-menu');

    if (!burger || !mobileMenu) return;

    function toggleMenu() {
        const isOpen = burger.classList.toggle('is-open');
        burger.setAttribute('aria-expanded', isOpen);
        burger.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');

        if (isOpen) {
            mobileMenu.removeAttribute('hidden');
        } else {
            mobileMenu.setAttribute('hidden', '');
        }
    }

    burger.addEventListener('click', toggleMenu);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && burger.classList.contains('is-open')) {
            toggleMenu();
        }
    });

    mobileMenu.addEventListener('click', (e) => {
        if (e.target.tagName.toLowerCase() === 'a' || e.target.closest('a') || e.target.closest('.btn')) {
            toggleMenu();
        }
    });
})();
