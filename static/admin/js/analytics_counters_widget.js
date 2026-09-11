(function () {
    'use strict';

    function updateHiddenInput(widget) {
        var items = [];
        widget.querySelectorAll('.analytics-counter-item').forEach(function (item) {
            var name = item.querySelector('.phone-label').value.trim();
            var code = item.querySelector('.analytics-counter-code').value;
            if (name || code) {
                items.push({name: name, code: code});
            }
        });
        widget.querySelector('input[type="hidden"]').value = JSON.stringify(items);
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.analytics-counters-widget').forEach(function (widget) {
            widget.querySelector('.phone-add').addEventListener('click', function () {
                var list = widget.querySelector('.phone-list');
                var item = document.createElement('div');
                item.className = 'phone-item analytics-counter-item';
                item.innerHTML =
                    '<input type="text" class="phone-label" placeholder="Название" data-field="name">' +
                    '<textarea class="phone-value analytics-counter-code" placeholder="HTML-код счётчика" data-field="code"></textarea>' +
                    '<button type="button" class="phone-remove">×</button>';
                list.appendChild(item);
                updateHiddenInput(widget);
            });

            widget.addEventListener('click', function (event) {
                if (event.target.classList.contains('phone-remove')) {
                    event.target.closest('.analytics-counter-item').remove();
                    updateHiddenInput(widget);
                }
            });

            widget.addEventListener('input', function () {
                updateHiddenInput(widget);
            });
        });
    });
})();