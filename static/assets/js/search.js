(function() {
    const citySelect = document.querySelector('select[name="city"]');
    const districtSelect = document.querySelector('select[name="district"]');
    if (!citySelect || !districtSelect) return;
    const chooseCityText = districtSelect.dataset.chooseCity || '';
    const districtLabel = districtSelect.dataset.districtLabel || '';

    const districts = Array.from(districtSelect.options).map(opt => ({
        id: opt.value,
        cityId: opt.getAttribute('data-city-id'),
        name: opt.text
    }));

    function resetDistricts() {
        districtSelect.replaceChildren(new Option(chooseCityText, ''));
        districtSelect.disabled = true;
    }

    function filterDistricts() {
        const cityId = citySelect.value;
        const previousDistrict = districtSelect.value;
        resetDistricts();
        if (!cityId) return;

        const options = districts
            .filter(d => d.cityId === cityId)
            .map(d => new Option(d.name, d.id));

        districtSelect.replaceChildren(new Option(districtLabel, ''), ...options);
        districtSelect.disabled = false;

        // Восстанавливаем выбранный район, если он совпадает с новым списком
        if (previousDistrict && Array.from(districtSelect.options).some(opt => opt.value === previousDistrict)) {
            districtSelect.value = previousDistrict;
        }
    }

    citySelect.addEventListener('change', filterDistricts);

    // При загрузке страницы, если город уже выбран — включить районы
    if (citySelect.value) {
        filterDistricts();
    } else {
        resetDistricts();
    }

    // Если район уже выбран в URL — включаем select
    if (districtSelect.value) {
        districtSelect.disabled = false;
    }
})();
