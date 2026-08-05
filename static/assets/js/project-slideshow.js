// Slideshow functionality
document.addEventListener('DOMContentLoaded', function () {
    const slideshows = document.querySelectorAll('[data-slideshow]');

    slideshows.forEach(function (slideshow) {
        const slideLink = slideshow.querySelector('.slideshow-link');
        let mainImage = slideshow.querySelector('.slideshow-main-image');
        const thumbs = slideshow.querySelectorAll('.slideshow-thumb');
        const counterCurrent = slideshow.querySelector('[data-current]');
        const mainContainer = slideshow.querySelector('.slideshow-main');
        const nextBtn = slideshow.querySelector('[data-action="next"]');
        const prevBtn = slideshow.querySelector('[data-action="prev"]');
        
        let currentIndex = 0;
        let autoplayInterval = null;
        const autoplayDelay = 5000; // 5 seconds

        function updateSlide(index, direction = 'next') {
            if (thumbs.length === 0) return;

            index = (index + thumbs.length) % thumbs.length;
            currentIndex = index;

            if (slideLink) {
                slideLink.dataset.full = thumbs[index].dataset.full || thumbs[index].dataset.src;
            }

            thumbs.forEach((thumb, idx) => {
                thumb.classList.toggle('is-active', idx === index);
            });

            const mainImageSrc = thumbs[index].dataset.src;
            if (!mainImageSrc) return;

            const imageContainer = slideLink || slideshow.querySelector('.slideshow-track');
            const currentImage = mainImage;

            const nextImage = document.createElement('img');
            nextImage.className = 'slideshow-next-image';
            nextImage.src = mainImageSrc;
            nextImage.style.position = 'absolute';
            nextImage.style.top = '0';
            nextImage.style.left = '0';
            nextImage.style.width = '100%';
            nextImage.style.height = '100%';
            nextImage.style.objectFit = 'cover';
            nextImage.style.objectPosition = 'center';
            nextImage.style.transition = 'transform 0.35s ease';
            nextImage.style.transform = direction === 'next'
                ? 'translateX(100%)'
                : 'translateX(-100%)';

            currentImage.style.transition = 'transform 0.35s ease';
            currentImage.style.transform = 'translateX(0)';

            imageContainer.appendChild(nextImage);

            // Форсируем layout, чтобы браузер видел начальное положение
            nextImage.getBoundingClientRect();

            currentImage.style.transform = direction === 'next'
                ? 'translateX(-100%)'
                : 'translateX(100%)';
            nextImage.style.transform = 'translateX(0)';

            nextImage.addEventListener('transitionend', function handler() {
                nextImage.removeEventListener('transitionend', handler);
                currentImage.remove();
                nextImage.className = 'slideshow-main-image';
                mainImage = nextImage;
            }, { once: true });

            if (counterCurrent) {
                counterCurrent.textContent = index + 1;
            }
        }

        // Thumb click handler
        thumbs.forEach((thumb, index) => {
            thumb.addEventListener('click', function () {
                updateSlide(index);
                resetAutoplay();
            });
        });

        // Next/Prev button handlers
        if (nextBtn) {
            nextBtn.addEventListener('click', function (e) {
                e.preventDefault();
                updateSlide(currentIndex + 1, 'next');
                resetAutoplay();
            });
        }
        if (prevBtn) {
            prevBtn.addEventListener('click', function (e) {
                e.preventDefault();
                updateSlide(currentIndex - 1, 'prev');
                resetAutoplay();
            });
        }

        function nextSlide() {
            updateSlide(currentIndex + 1);
        }

        function startAutoplay() {
            if (thumbs.length > 1) {
                autoplayInterval = setInterval(nextSlide, autoplayDelay);
            }
        }

        function pauseAutoplay() {
            clearInterval(autoplayInterval);
            autoplayInterval = null;
        }

        function resetAutoplay() {
            pauseAutoplay();
            startAutoplay();
        }

        // Pause on hover
        mainContainer.addEventListener('mouseenter', pauseAutoplay);
        mainContainer.addEventListener('mouseleave', startAutoplay);

        // Start autoplay
        startAutoplay();

        // Open modal on main image click
        if (slideLink) {
            slideLink.addEventListener('click', function (e) {
                if (typeof bootstrap !== 'undefined' && document.getElementById('projectSlideshowModal')) {
                    e.preventDefault();
                    openBootstrapModalAt(currentIndex, Array.from(thumbs), slideLink);
                }
            });
        }
    });

    // requires bootstrap JS to be loaded
    function openBootstrapModalAt(index, thumbs, slideLink) {
        const modalEl = document.getElementById('projectSlideshowModal');
        if (!modalEl || typeof bootstrap === 'undefined') return;

        const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);

        modalEl.addEventListener('hidden.bs.modal', () => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
            document.body.classList.remove('modal-open');
        });

        const imgEl = modalEl.querySelector('#projectSlideshowModalImage');
        index = (index + thumbs.length) % thumbs.length;

        const slide = thumbs[index];
        let full = slide && (slide.dataset.full || slide.dataset.src);
        if (!full && slideLink) {
            full = slideLink.dataset.full || slideLink.dataset.src;
        }

        if (imgEl) {
            imgEl.src = full || '';
        }
        modalInstance.show();
    }

    // modal helpers (Bootstrap)
    (function () {
        const modalEl = document.getElementById('projectSlideshowModal');
        if (!modalEl) return;
        const modalImg = modalEl.querySelector('#projectSlideshowModalImage');
        const modalThumbs = Array.from(modalEl.querySelectorAll('.modal-thumb'));
        let modalIndex = 0;
        function setModalImage(index) {
            index = (index + modalThumbs.length) % modalThumbs.length;
            modalIndex = index;
            const full = modalThumbs[index].dataset.full || modalThumbs[index].dataset.src;
            if (modalImg) modalImg.src = full;
            modalThumbs.forEach((t, i) => t.classList.toggle('is-active', i === index));
        }
        // click on modal thumbs
        modalThumbs.forEach((btn, idx) => {
            btn.addEventListener('click', () => setModalImage(idx));
        });
        // keyboard navigation while modal open
        modalEl.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') setModalImage(modalIndex + 1);
            if (e.key === 'ArrowLeft') setModalImage(modalIndex - 1);
        });
        // sync when opening via our helper
        modalEl.addEventListener('shown.bs.modal', () => {
            // If you pass index to openBootstrapModalAt, you can store it and call setModalImage
            // For now, if modalImg.src set, try to highlight matching thumb
            const src = modalImg && modalImg.src;
            const found = modalThumbs.findIndex(t => (t.dataset.full === src) || (t.dataset.src === src));
            if (found >= 0) setModalImage(found);
            // focus for keyboard
            modalEl.focus();
        });
    })();
});
