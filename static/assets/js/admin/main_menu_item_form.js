(function ($) {
    function updateFields(row) {
        var isSection = row.find('select[name$="-type"]').val() === "section";
        row.find(".field-section_url").toggle(isSection);
        row.find(".field-link_url").toggle(!isSection);
    }

    $(function () {
        $("tr.form-row").each(function () {
            updateFields($(this));
        });
    });

    $(document).on("change", 'select[name$="-type"]', function () {
        updateFields($(this).closest("tr"));
    });

    $(document).on("formset:added", function (event, row) {
        updateFields(row);
    });
})(django.jQuery);
