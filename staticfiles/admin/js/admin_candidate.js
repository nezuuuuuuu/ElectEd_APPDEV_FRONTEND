// document.addEventListener('DOMContentLoaded', function() {
//     const electionSelect = document.querySelector('#id_election');
//     const positionSelect = document.querySelector('#id_position');

//     electionSelect.addEventListener('change', function() {
//         const electionId = electionSelect.value;
//         if (electionId) {
//             fetch(`/admin/get_positions/${electionId}/`)
//                 .then(response => response.json())
//                 .then(data => {
//                     // Clear existing options
//                     positionSelect.innerHTML = '';

//                     // Add the new options
//                     data.positions.forEach(function(position) {
//                         const option = document.createElement('option');
//                         option.value = position.id;
//                         option.textContent = position.title;
//                         positionSelect.appendChild(option);
//                     });
//                 });
//         } else {
//             // If no election is selected, clear the positions dropdown
//             positionSelect.innerHTML = '';
//         }
//     });
// });