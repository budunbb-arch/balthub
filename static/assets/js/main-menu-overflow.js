(() => {
    const menus = document.querySelectorAll('.js-overflow-menu');
    const desktop = window.matchMedia('(min-width: 992px)');

    menus.forEach((menu) => {
        const items = Array.from(menu.children).filter((item) => item.classList.contains('nav-item'));
        const dropdown = document.createElement('li');
        dropdown.className = 'nav-item dropdown';
        dropdown.hidden = true;

        const toggle = document.createElement('button');
        toggle.className = 'btn btn-text text-small';
        toggle.type = 'button';
        toggle.setAttribute('data-bs-toggle', 'dropdown');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.append(document.createTextNode(`${menu.dataset.overflowLabel} `));

        const icon = document.createElement('i');
        icon.className = 'fa-solid fa-ellipsis';
        icon.setAttribute('aria-hidden', 'true');
        toggle.append(icon);
        dropdown.append(toggle);

        const dropdownMenu = document.createElement('ul');
        dropdownMenu.className = 'dropdown-menu dropdown-menu-end';
        dropdown.append(dropdownMenu);
        menu.append(dropdown);

        const clearOverflow = () => {
            if (dropdown.classList.contains('show')) {
                bootstrap.Dropdown.getInstance(toggle)?.hide();
            }

            items.forEach((item) => {
                item.hidden = false;
            });
            dropdownMenu.replaceChildren();
            dropdown.hidden = true;
            toggle.classList.remove('active');
        };

        const updateOverflow = () => {
            clearOverflow();

            if (!desktop.matches || menu.clientWidth === 0) {
                return;
            }

            if (menu.scrollWidth <= menu.clientWidth + 1) {
                return;
            }

            dropdown.hidden = false;
            for (let index = items.length - 1; index >= 0; index -= 1) {
                if (menu.scrollWidth <= menu.clientWidth + 1) {
                    break;
                }

                const item = items[index];
                const copy = item.cloneNode(true);
                copy.classList.remove('nav-item');
                copy.hidden = false;

                copy.querySelectorAll('a').forEach((link) => {
                    link.classList.remove('nav-link', 'state', 'btn', 'menu-btn');
                    link.classList.add('dropdown-item');
                });

                if (copy.querySelector('[aria-current="page"], .state')) {
                    toggle.classList.add('active');
                }

                dropdownMenu.prepend(copy);
                item.hidden = true;
            }
        };

        window.addEventListener('resize', updateOverflow);
        desktop.addEventListener('change', updateOverflow);
        if ('ResizeObserver' in window) {
            new ResizeObserver(updateOverflow).observe(menu.parentElement);
        }
        if (document.fonts?.ready) {
            document.fonts.ready.then(updateOverflow);
        }
        updateOverflow();
    });
})();
