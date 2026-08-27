(function () {
    'use strict';

    function updateHiddenInput(widget) {
        var items = [];
        widget.querySelectorAll('.phone-item').forEach(function (el) {
            var label = el.querySelector('.phone-label').value.trim();
            var value = el.querySelector('.phone-value').value.trim();
            if (value) {
                items.push({label: label, value: value});
            }
        });
        var hidden = widget.querySelector('input[type="hidden"]');
        hidden.value = JSON.stringify(items);
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.phone-widget').forEach(function (widget) {
            var addBtn = widget.querySelector('.phone-add');
            addBtn.addEventListener('click', function () {
                var list = widget.querySelector('.phone-list');
                var count = list.querySelectorAll('.phone-item').length;
                var item = document.createElement('div');
                item.className = 'phone-item';
                item.setAttribute('data-index', count);
                item.innerHTML =
                    '<input type="text" class="phone-label" placeholder="Подпись" data-field="label">' +
                    '<input type="text" class="phone-value" placeholder="Телефон" data-field="value">' +
                    '<button type="button" class="phone-remove">×</button>';
                list.appendChild(item);
                updateHiddenInput(widget);
            });

            widget.addEventListener('click', function (e) {
                if (e.target.classList.contains('phone-remove')) {
                    e.target.closest('.phone-item').remove();
                    updateHiddenInput(widget);
                }
            });

            widget.addEventListener('input', function () {
                updateHiddenInput(widget);
            });
        });
    });
})();
