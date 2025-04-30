document.addEventListener('DOMContentLoaded', function() {

    // Autocomplete feature
    const category = document.querySelector('#id_category');
    category.addEventListener('input', () => suggestions(category));

    // Run when form is submitted
    document.querySelector('#new_recipe-form').addEventListener('submit', (event) => new_recipe(event));
    document.querySelector('#search_bar').style.backgroundColor = "transparent";
    document.querySelector('#search_box').placeholder = "Search disabled on this page.";

    document.addEventListener('click', function(event) {
        let inputs = document.querySelectorAll('.input_width');
        inputs.forEach((input) => {
            if (input.id == "id_meal" || input.id == "id_category")
            {
                let suggestionsContainer = document.getElementById('suggestions-' + input.id);
                if (!input.contains(event.target) && !suggestionsContainer.contains(event.target)) {
                    suggestionsContainer.innerHTML = '';
                }
            }
        });
    });
});

async function new_recipe(event) {

    // Process lists
    event.preventDefault();
    ingredients_list = process_list('ingredients_entry');
    notes_list = process_list('note_entry');
    directions_list = process_list('instructions_entry');

    let formData = new FormData();

    // Check if image was uploaded
    const fileInput = document.querySelector('#id_image');
    if (fileInput.files.length === 0) {
        console.log("No file uploaded, assigning fallback image.");
    
        const fallbackImagePath = "/static/images/no_image.jpeg"; // Adjust path if needed
    
        fetch(fallbackImagePath)
            .then(response => response.blob()) // Convert fallback image to Blob
            .then(blob => {
                const fallbackFile = new File([blob], "no_image.jpeg", { type: "image/jpeg" });
    
                // Simulate file selection
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(fallbackFile);
                fileInput.files = dataTransfer.files;

                if (fileInput.files.length != 0) {
                    console.log("Fallback image assigned to file input!");
                }
                else
                {
                    console.log("Still not working");
                }

                formData.append('image', fileInput.files[0]);
            })
            .catch(error => console.error("Error loading fallback image:", error));
    }
    else {
        console.log("User uploaded an image.");
        formData.append('image', fileInput.files[0]);
    }

    // Assemble form data
    // if (validateForm()) {
    formData.append('title', document.querySelector('#id_title').value);
    formData.append('image', document.querySelector('#id_image').files[0]);
    formData.append('category', document.querySelector('#id_category').value);
    formData.append('meal', document.querySelector('#id_meal').value);
    formData.append('cooktime', document.querySelector('#id_cooktime').value);
    formData.append('ingredients', JSON.stringify(ingredients_list));
    formData.append('instructions', JSON.stringify(directions_list));
    formData.append('notes', JSON.stringify(notes_list));

    const csrftoken = getCookie('csrftoken');

    const options = {
        method: 'POST',
        headers: {
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
    str_list = str_list.replace(/\n/g, ";")
    str_list = str_list.split(";");

    str_list.forEach((item) => {

        item = item.trim();

        if (item[0] == "-") {
            item = item.slice(1);
            item = item.trim();
        }

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

async function suggestions(category)
{
    if (category.value.length >= 0) {
        const response = await fetch_autocomplete(category.value, 'category');
        let suggestionsContainer = document.getElementById('suggestions-id_category');
        suggestionsContainer.innerHTML = '';

        response.matched_fields.forEach(match => {
            let suggestionDiv = document.createElement('div');
            suggestionDiv.textContent = match;
            suggestionDiv.addEventListener('click', function() {
                document.getElementById('id_category').value = this.textContent;
                suggestionsContainer.innerHTML = '';
            });
            suggestionsContainer.appendChild(suggestionDiv);
        })
    }
}


async function fetch_autocomplete(query, field)
{
    try {
        const response = await fetch(`/autocomplete/?query=${query}&field=${field}`);

        if (!response.ok) {
            // If the response is not OK, handle the error
            throw new Error('Error: ', response.statusText);
        }

        const responseData = await response.json();
        return responseData;
    }
    catch (error) {
        // Handle the error that occurred during the asynchronous operation
        console.error('Error:', error);
    }
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