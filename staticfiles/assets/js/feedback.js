jQuery(function ($) {

    // ---------- Маска телефона и префикс страны ----------

    // Текущий телефонный код выбранной страны (цифры, без "+").
    function phonePrefix($form) {
        return ($form.find('.phone-country').val() || '').replace(/\D/g, '');
    }

    // Форматирует локальные цифры в "+К (XXX) XXX-XX-XX".
    function formatPhone(raw, prefix) {
        var d = (raw || '').replace(/\D/g, '');
        if (prefix && d.indexOf(prefix) === 0) d = d.slice(prefix.length);
        d = d.slice(0, 10);

        var s = '+' + prefix;
        if (d.length > 0) {
            s += ' (' + d.slice(0, 3);
            if (d.length >= 3) s += ')';
        }
        if (d.length > 3) s += ' ' + d.slice(3, 6);
        if (d.length > 6) s += '-' + d.slice(6, 8);
        if (d.length > 8) s += '-' + d.slice(8, 10);
        return s;
    }

    // Нормализует в E.164: "+код + 10 цифр" без пробелов/скобок.
    function normalizePhone(raw, prefix) {
        var d = (raw || '').replace(/\D/g, '');
        if (prefix && d.indexOf(prefix) === 0) d = d.slice(prefix.length);
        d = d.slice(0, 10);
        return '+' + prefix + d;
    }

    function maskPhone($input) {
        var $form = $input.closest('.feedback-form, .project-feedback-form');
        $input.val(formatPhone($input.val(), phonePrefix($form)));
    }

$(document).on('input', '.feedback-form .phone-input, .project-feedback-form .phone-input', function () {
    maskPhone($(this));
});

$(document).on('input', '.order-call-form .phone-input', function () {
    var $input = $(this);
    var formatted = formatPhone($input.val(), '7');
    $input.val(formatted);
});

    $(document).on('change', '.feedback-form .phone-country, .project-feedback-form .phone-country', function () {
        var $form = $(this).closest('.feedback-form, .project-feedback-form');
        var prefix = phonePrefix($form);
        $form.find('.phone-input').each(function () {
            $(this).val('+' + prefix);
            maskPhone($(this));
        });
    });

    function setupProjectFeedbackForm($form) {
        var modalEl = document.getElementById('projectFeedbackModal');
        if (!modalEl) return;

        var titleEl = modalEl.querySelector('#projectFeedbackModalLabel');
        var messageTplEl = $form.find('input[name="message_tpl"]')[0];
        var dateField = modalEl.querySelector('.field-date');
        var turnstileContainer = modalEl.querySelector('.cf-turnstile');
        var turnstileWidgetId = null;

        var headerViewing = modalEl.getAttribute('data-header-viewing') || '';
        var headerInfo = modalEl.getAttribute('data-header-info') || '';
        var tplViewing = modalEl.getAttribute('data-tpl-viewing') || '';
        var tplInfo = modalEl.getAttribute('data-tpl-info') || '';

        function renderTurnstile() {
            if (!turnstileContainer || !window.turnstile) return;
            try {
                turnstileWidgetId = window.turnstile.render(turnstileContainer, {
                    sitekey: turnstileContainer.getAttribute('data-sitekey') || ''
                });
            } catch (e) {
                console.warn('Turnstile render error', e);
            }
        }

        function resetTurnstile() {
            if (turnstileWidgetId && window.turnstile) {
                try { window.turnstile.reset(turnstileWidgetId); } catch (e) {}
            }
        }

        modalEl.addEventListener('show.bs.modal', function(event) {
            var button = event.relatedTarget;
            var formType = button ? button.getAttribute('data-form-type') : 'info';

            if (formType === 'viewing') {
                if (titleEl) titleEl.textContent = headerViewing;
                if (messageTplEl) messageTplEl.value = tplViewing;
                if (dateField) dateField.style.display = 'block';
            } else {
                if (titleEl) titleEl.textContent = headerInfo;
                if (messageTplEl) messageTplEl.value = tplInfo;
                if (dateField) dateField.style.display = 'none';
            }

            setTimeout(renderTurnstile, 50);
        });

        modalEl.addEventListener('hide.bs.modal', function() {
            resetTurnstile();
        });
    }

    $('.project-feedback-form').each(function () {
        setupProjectFeedbackForm($(this));
    });

    $('.project-feedback-form').on('submit', function (e) {
        e.preventDefault();
        var $form = $(this);

        if ($form.data('submitting')) {
            return;
        }
        $form.data('submitting', true);

        var moduleId = $form.data('module-id');

        $form.find('.phone-input').each(function () {
            var prefix = phonePrefix($form);
            if ($(this).val() && prefix) {
                $(this).val(normalizePhone($(this).val(), prefix));
            }
        });

        var hasTurnstile = $form.find('.cf-turnstile').length > 0;
        if (hasTurnstile) {
            var cfToken = $form.find('input[name="cf-turnstile-response"]').val() || '';
            if (!cfToken) {
                toastr.error('Слава роботам?');
                $form.data('submitting', false);
                return;
            }
        }

        var formData = new FormData($form[0]);

        fetch('/project-feedback/send/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': $form.find('input[name="csrfmiddlewaretoken"]').val(),
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            },
            body: formData,
        })
        .then(function (response) {
            return response.json().then(function (data) {
                return {status: response.status, data: data};
            });
        })
        .then(function (result) {
            if (result.status === 200 && result.data.success) {
                $form[0].reset();
                if (window.turnstile) {
                    try { window.turnstile.reset(); } catch (err) {}
                }
                $form.hide();
                $form.closest('.modal').find('.success-form').show();
                toastr.success('Заявка отправлена!');
            } else {
                toastr.error(result.data.error || 'Ошибка отправки');
            }
        })
        .catch(function () {
            toastr.error('Ошибка отправки');
        })
        .always(function () {
            $form.data('submitting', false);
        });
    });

    $(document).on('click', '.document-modal', function (e) {
        e.preventDefault();
        var $link = $(this);
        var url = $link.attr('href');
        if (!url) return;

        var modalEl = document.getElementById('documentModal');
        if (!modalEl) return;

        var BootstrapModal = window.bootstrap ? window.bootstrap.Modal : null;
        var modal = BootstrapModal ? BootstrapModal.getOrCreateInstance(modalEl) : null;
        $('#documentModalTitle').text($link.data('title') || '');
        $('#documentModal .document-modal-content').load(url, function () {
            if (modal) {
                modal.show();
            } else {
                modalEl.style.display = 'block';
            }
        });
    });

    // ---------- Order call modal ----------

    function setupOrderCallForm($form) {
        var modalEl = document.getElementById('orderCallModal');
        if (!modalEl) return;

        var turnstileContainer = modalEl.querySelector('.cf-turnstile');
        var turnstileWidgetId = null;

        function renderTurnstile() {
            if (!turnstileContainer || !window.turnstile) return;
            try {
                turnstileWidgetId = window.turnstile.render(turnstileContainer, {
                    sitekey: turnstileContainer.getAttribute('data-sitekey') || ''
                });
            } catch (e) {
                console.warn('Turnstile render error', e);
            }
        }

        function resetTurnstile() {
            if (turnstileWidgetId && window.turnstile) {
                try { window.turnstile.reset(); } catch (e) {}
            }
        }

        modalEl.addEventListener('show.bs.modal', function() {
            setTimeout(renderTurnstile, 50);
        });

        modalEl.addEventListener('hide.bs.modal', function() {
            resetTurnstile();
        });
    }

    $('.order-call-form').each(function () {
        setupOrderCallForm($(this));
    });

    $('.order-call-form').on('submit', function (e) {
        e.preventDefault();
        var $form = $(this);

        if ($form.data('submitting')) {
            return;
        }
        $form.data('submitting', true);

        $form.find('.phone-input').each(function () {
            var raw = ($(this).val() || '').replace(/\D/g, '');
            if (!raw) return;
            if (raw.length === 11 && (raw[0] === '7' || raw[0] === '8')) {
                raw = '7' + raw.slice(1);
            } else if (raw.length === 10) {
                raw = '7' + raw;
            } else if (raw.length < 10) {
                raw = '7' + raw;
            }
            raw = raw.slice(0, 11);
            $(this).val('+' + raw);
        });

        var hasTurnstile = $form.find('.cf-turnstile').length > 0;
        if (hasTurnstile) {
            var cfToken = $form.find('input[name="cf-turnstile-response"]').val() || '';
            if (!cfToken) {
                toastr.error('Слава роботам?');
                $form.data('submitting', false);
                return;
            }
        }

        var formData = new FormData($form[0]);

        fetch('/order-call/send/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': $form.find('input[name="csrfmiddlewaretoken"]').val(),
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            },
            body: formData,
        })
        .then(function (response) {
            return response.json().then(function (data) {
                return {status: response.status, data: data};
            });
        })
        .then(function (result) {
            if (result.status === 200 && result.data.success) {
                $form[0].reset();
                if (window.turnstile) {
                    try { window.turnstile.reset(); } catch (err) {}
                }
                $form.hide();
                $form.closest('.modal').find('.success-form').show();
                toastr.success('Заявка отправлена!');
            } else {
                toastr.error(result.data.error || 'Ошибка отправки');
            }
        })
        .catch(function (err) {
            toastr.error('Ошибка отправки');
        })
        .always(function () {
            $form.data('submitting', false);
        });
    });
});