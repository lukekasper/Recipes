document.addEventListener('DOMContentLoaded', function() {

    // run when form is submitted
    document.querySelector('#new_recipe-form').addEventListener('submit', (event) => new_recipe(event));
    document.querySelector('#search_bar').style.backgroundColor = "transparent";
    document.querySelector('#search_box').placeholder = "Search disabled on this page.";

});

async function new_recipe(event) {

    // Process lists
    event.preventDefault();
    ingredients_list = process_list('ingredients_entry');
    notes_list = process_list('note_entry');
    directions_list = process_list('instructions_entry');

    // Assemble form data
    // if (validateForm()) {
    let formData = new FormData();
    formData.append('title', document.querySelector('#id_title').value);
    formData.append('image', document.querySelector('#id_image').files[0]);
    formData.append('category', document.querySelector('#id_category').value);
    formData.append('meal', document.querySelector('#id_meal').value);
    formData.append('cooktime', document.querySelector('#id_cooktime').value);
    formData.append('ingredients', JSON.stringify(ingredients_list));
    formData.append('instructions', JSON.stringify(directions_list));
    formData.append('notes', JSON.stringify(notes_list));

    const csrftoken = getCookie('csrftoken');

    console.log(csrftoken);

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: formData
    };

    // Send POST request to back end
    fetch('/add_recipe', options)

    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.error);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.message === "Recipe added.") {
            window.location.href = "/";
        }
    })
    .catch(error => {
        console.error('Error: ', error);
        document.querySelector('.error-message').innerHTML = error.message;
    });
    // }

    // else {
    //     alert('Please fill out all required fields.');
    // }
}

// Process input form lists
function process_list(id) {

    let list = [];
    let str_list = document.querySelector('#' + id).value;

    // Split by ';' so user can input multiple items at once
    str_list = str_list.split(";");

    str_list.forEach((item) => {

        item = item.trim();

        if (item != " " && item != "") {

            let processed_item = item.charAt(0).toUpperCase() + item.slice(1);

            if (id.includes("note") || id.includes("instruction")) {
                if (processed_item.at(-1) != ".") {
                    processed_item += ".";
                }
            }

            // Add item to the list capitalizing first letter
            list.push(processed_item);
        }
    })
    return list;
}

// Get csrf token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// // Function to check if all required fields are filled
// function validateForm() {
//     let isValid = true;
//     const requiredFields = document.querySelectorAll('[required]');

//     requiredFields.forEach(field => {
//         if (!field.value) {
//             isValid = false;
//             field.classList.add('error'); // Add a class to highlight the error
//         } else {
//             field.classList.remove('error');
//         }
//     });

//     return isValid;
// }