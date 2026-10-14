(function () {
    var CAPTCHA_TOLERANCE = 3;

    function positionTarget(captcha) {
        var slider = captcha.querySelector('[data-captcha-slider]');
        var scale = captcha.querySelector('.slider-captcha__scale');
        var marker = captcha.querySelector('.slider-captcha__target');
        var sliderRect = slider.getBoundingClientRect();
        var scaleRect = scale.getBoundingClientRect();

        if (!sliderRect.width || !scaleRect.width) return;

        var thumbSize = parseFloat(
            getComputedStyle(captcha).getPropertyValue('--captcha-thumb-size')
        ) || 16;
        var target = Number(captcha.dataset.target);
        var trackWidth = Math.max(0, sliderRect.width - thumbSize);
        var thumbCenter = sliderRect.left - scaleRect.left
            + thumbSize / 2
            + trackWidth * target / 100;

        marker.style.left = thumbCenter + 'px';
    }

    function updateCaptcha(captcha) {
        var slider = captcha.querySelector('[data-captcha-slider]');
        var value = captcha.querySelector('[data-captcha-value]');
        var status = captcha.querySelector('[data-captcha-status]');
        var target = Number(captcha.dataset.target);
        var passed = Math.abs(Number(slider.value) - target) <= CAPTCHA_TOLERANCE;

        positionTarget(captcha);
        value.value = passed ? slider.value : '';
        captcha.classList.toggle('is-passed', passed);
        status.innerHTML = passed ? '<span class="captcha-yes"><i class="fa-solid fa-check"></i></span>' : '<span class="captcha-no"><i class="fa-solid fa-xmark"></i></span>';
        slider.setAttribute('aria-valuetext', slider.value + '%');

        var form = captcha.closest('form');
        if (form) {
            var submit = form.querySelector('button[type="submit"]');
            if (submit) submit.disabled = !passed;
        }
    }

    function init() {
        document.querySelectorAll('[data-slider-captcha]').forEach(function (captcha) {
            var slider = captcha.querySelector('[data-captcha-slider]');
            slider.addEventListener('input', function () { updateCaptcha(captcha); });
            if (window.ResizeObserver) {
                var observer = new ResizeObserver(function () {
                    positionTarget(captcha);
                });
                observer.observe(captcha.querySelector('.slider-captcha__scale'));
            } else {
                window.addEventListener('resize', function () {
                    positionTarget(captcha);
                });
            }
            updateCaptcha(captcha);
        });
    }

    document.addEventListener('DOMContentLoaded', init);
})();