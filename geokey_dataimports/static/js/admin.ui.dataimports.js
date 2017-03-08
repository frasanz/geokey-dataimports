$(document).ready(function() {
    /*
     * Loader
     *
     * Reacts to a button click, that has data-loader="true" set. Also uses
     * text entered in data-loader-text (separated with commas to have
     * multiple) to show info next to a loader spinner.
    */
    var timeout, interval;

    $('[data-loader="true"]').click(function() {
        var $this = $(this);
        var loaderText = $this.data('loader-text');

        if (loaderText) {
            loaderText = loaderText.split(',');

            if (interval) {
                clearInterval(interval);
            }

            interval = window.setInterval(function() {
                $('p.loader-text').empty().text(loaderText[Math.floor(Math.random() * loaderText.length)]);
            }, 3000);
        }

        if (timeout) {
            clearTimeout(timeout);
        }

        timeout = window.setTimeout(function() {
            var errors = $this.closest('form').find('.has-error');

            if (errors.length === 0) {
                $('#loader').fadeIn();
            }
        }, 1500);
    });

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
