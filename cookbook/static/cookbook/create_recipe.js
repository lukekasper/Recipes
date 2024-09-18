document.addEventListener('DOMContentLoaded', function() {

    // run when form is submitted
    document.querySelector('#new_recipe-form').addEventListener('submit', (event) => new_recipe(event));
});

async function new_recipe(event) {

    // Process lists
    event.preventDefault();
    ingredients_list = process_list(document.querySelector('#ingredients_entry').value);
    directions_list = process_list(document.querySelector('#instructions_entry').value);
    notes_list = process_list(document.querySelector('#note_entry').value);

    // Assemble form data
    if (validateForm()) {
        let formData = new FormData();
        formData.append('title', document.querySelector('#id_title').value);
        formData.append('image', document.querySelector('#id_image').files[0]);
        formData.append('category', document.querySelector('#id_category').value);
        formData.append('cooktime', document.querySelector('#id_cooktime').value);
        formData.append('ingredients', JSON.stringify(ingredients_list));
        formData.append('instructions', JSON.stringify(directions_list));
        formData.append('notes', JSON.stringify(notes_list));

        const options = {
            method: 'POST',
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
    }

    else {
        alert('Please fill out all required fields.');
    }
}

// Process input form lists
function process_list(str_list) {

    let list = [];

    // Split by ';' so user can input multiple items at once
    str_list = str_list.split(";");

    str_list.forEach((item) => {

        item = item.trim();

        if (item != " " && item != "") {

            let processed_item = item.charAt(0).toUpperCase() + item.slice(1);

            // Add item to the list capitalizing first letter
            list.push(processed_item);
        }
    })
    return list;
}

// Function to check if all required fields are filled
function validateForm() {
    let isValid = true;
    const requiredFields = document.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value) {
            isValid = false;
            field.classList.add('error'); // Add a class to highlight the error
        } else {
            field.classList.remove('error');
        }
    });

    return isValid;
}