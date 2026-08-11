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
        var $form = $input.closest('.feedback-form');
        $input.val(formatPhone($input.val(), phonePrefix($form)));
    }

    // Форматируем при вводе.
    $(document).on('input', '.feedback-form .phone-input', function () {
        maskPhone($(this));
    });

    // При смене страны проставляем префикс в поля телефона.
    $(document).on('change', '.feedback-form .phone-country', function () {
        var $form = $(this).closest('.feedback-form');
        var prefix = phonePrefix($form);
        $form.find('.phone-input').each(function () {
            $(this).val('+' + prefix);
            maskPhone($(this));
        });
    });

    // ---------- Отправка формы ----------

    $('.feedback-form').on('submit', function (e) {
        e.preventDefault();
        var $form = $(this);
        var moduleId = $form.data('module-id');

        // Нормализуем телефон в E.164 перед отправкой.
        $form.find('.phone-input').each(function () {
            var prefix = phonePrefix($form);
            if ($(this).val() && prefix) {
                $(this).val(normalizePhone($(this).val(), prefix));
            }
        });

        // Если включена капча Turnstile — проверяем, что токен получен.
        var hasTurnstile = $form.find('.cf-turnstile').length > 0;
        if (hasTurnstile) {
            var cfToken = $form.find('input[name="cf-turnstile-response"]').val() || '';
            if (!cfToken) {
                toastr.error('Слава роботам?');
                return;
            }
        }

        // Собираем поля формы в объект и отправляем в формате JSON
        // (view /feedback/send/ читает тело запроса через json.loads).
        var payload = {};
        $form.serializeArray().forEach(function (item) {
            // Не даём пустому значению затереть уже заполненное поле
            // (например, два типа дают name="phone").
            if (item.value !== '' || !(item.name in payload)) {
                payload[item.name] = item.value;
            }
        });
        payload.module_id = moduleId;

        $.ajax({
            url: '/feedback/send/',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(payload),
            headers: {
                'X-CSRFToken': $form.find('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                if (data.success) {
                    $form[0].reset();
                    // Сброс виджета капчи, чтобы можно было отправить ещё раз.
                    if (window.turnstile) {
                        try { window.turnstile.reset(); } catch (err) {}
                    }
                    // Прячем форму и показываем сообщение об успехе.
                    $form.hide();
                    $form.closest('.feedback-module').find('.success-form').show();
                } else {
                    toastr.error(data.error || 'Ошибка отправки');
                }
            },
            error: function () {
                toastr.error('Ошибка отправки');
            },
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
});