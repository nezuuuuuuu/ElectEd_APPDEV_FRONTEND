document.addEventListener('DOMContentLoaded', function () {
    const electionDropdown = document.querySelector('#id_election'); // Adjust ID to match your form field
    const saveContinueButton = document.querySelector('input[name="_continue"]'); // Find the "Save and continue editing" button

    if (electionDropdown && saveContinueButton) {
        electionDropdown.addEventListener('change', function () {
            // Trigger the "Save and continue editing" button
            saveContinueButton.click();
        });
    }
});