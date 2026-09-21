(function () {
    var CAPTCHA_TOLERANCE = 3;

    function updateCaptcha(captcha) {
        var slider = captcha.querySelector('[data-captcha-slider]');
        var value = captcha.querySelector('[data-captcha-value]');
        var status = captcha.querySelector('[data-captcha-status]');
        var target = Number(captcha.dataset.target);
        var passed = Math.abs(Number(slider.value) - target) <= CAPTCHA_TOLERANCE;

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
            updateCaptcha(captcha);
        });
    }

    document.addEventListener('DOMContentLoaded', init);
})();