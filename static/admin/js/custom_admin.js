document.addEventListener('DOMContentLoaded', function () {
    const departmentContainer = document.querySelector('#id_departments'); // Adjust to match your container's ID

    if (!departmentContainer) {
        console.error("The #id_departments container was not found.");
        return;
    }

    // Get all checkbox inputs inside the container
    const checkboxes = Array.from(departmentContainer.querySelectorAll('input[type="checkbox"]'));
    const allCheckbox = checkboxes.find(checkbox => checkbox.value === "ALL");

    if (!allCheckbox) {
        console.error("The 'ALL' checkbox was not found.");
        return;
    }

    // Event listener for changes to any checkbox
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            if (checkbox === allCheckbox) {
                // If 'ALL' is selected, select/deselect all checkboxes
                checkboxes.forEach(cb => cb.checked = allCheckbox.checked);
            } else if (!checkbox.checked) {
                // If any other checkbox is unchecked, uncheck 'ALL'
                allCheckbox.checked = false;
            } else if (checkboxes.every(cb => cb.checked || cb === allCheckbox)) {
                // If all checkboxes are checked, check 'ALL'
                allCheckbox.checked = true;
            }
        });
    });
});