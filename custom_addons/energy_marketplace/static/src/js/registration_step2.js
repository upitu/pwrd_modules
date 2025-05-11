odoo.define('energy_marketplace.registration_step2', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.RegistrationStep2 = publicWidget.Widget.extend({
        selector: '.oe_website_registration_step2',
        start: function () {
            console.log("🚀 registration_step2.js loaded");

            const $emirateSelect = $('#emirate-select');
            const $continueButton = $('.btn-continue');
            const $requiredInputs = $('input[required="1"], select[required="1"]').not('#emirate-select');

            $emirateSelect.select2({
                placeholder: "Select Emirates",
                width: '100%'
            });

            function validateForm() {
                let isValid = true;

                $requiredInputs.each(function () {
                    const val = $(this).val();
                    if (!val || val.trim() === '') {
                        isValid = false;
                    }
                });

                const emiratesSelected = $emirateSelect.val();
                if (!emiratesSelected || emiratesSelected.length === 0) {
                    isValid = false;
                }

                if (isValid) {
                    $continueButton.removeAttr('disabled');
                } else {
                    $continueButton.attr('disabled', 'disabled');
                }

                console.log("✅ Form valid?", isValid);
            }

            $requiredInputs.on('input change', validateForm);
            $emirateSelect.on('change', validateForm);

            validateForm();

            return this._super.apply(this, arguments);
        }
    });

    return publicWidget.registry.RegistrationStep2;
});