(function () {
    'use strict';

    var button = document.querySelector('.slide-to-top');
    if (!button) {
        return;
    }

    function updateVisibility() {
        var scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
        var threshold = scrollableHeight * 0.1;
        button.classList.toggle('is-visible', scrollableHeight > 0 && window.scrollY > threshold);
    }

    window.addEventListener('scroll', updateVisibility, {passive: true});
    window.addEventListener('resize', updateVisibility);
    button.addEventListener('click', function () {
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
    updateVisibility();
})();