$(document).ready(function() {
    // Toggle all checkboxes
    $('input.toggle').change(function() {
        $('input[name="ids"]').prop('checked', this.checked).trigger('change');
    });

    // Toggle required fields when field is checked/unchecked
    $('input[name="ids"]').change(function() {
        var tr = $(this).parents('tr');

        if (!this.checked) {
            tr.find('.form-group').removeClass('has-error');
            tr.find('.help-block').remove();
        }

        tr.find('input[name*="fieldname"], select[name*="fieldtype"]').prop('required', this.checked);
    });

    // Toggle selecting an existing field
    $('select[name*="existingfield"]').change(function() {
        var tr = $(this).parents('tr');
        var value = $(this).val();

        tr.find('input[name*="fieldname"], select[name*="fieldtype"]').prop('disabled', value ? true : false);

        if (value) {
            tr.find('.form-group').removeClass('has-error');
            tr.find('.help-block').remove();
            $('select[name!="' + this.name + '"] option[value="' + value + '"]:selected').prop('selected', false).trigger('change');
        }
    });
});
