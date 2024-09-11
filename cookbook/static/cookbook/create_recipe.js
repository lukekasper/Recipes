document.addEventListener('DOMContentLoaded', function() {

    num_ingredients = 0;
    direction_num = 0;
    directions_list = [];
    ingredients_list = [];
    notes_list = [];

    // run when Add Ingredient is clicked
    document.querySelector('#ingredients-button').addEventListener('click', add_ingredient);

    // run when Add Direction is clicked
    document.querySelector('#instructions-button').addEventListener('click', add_direction);

    // run when Add Note is clicked
    document.querySelector('#notes-button').addEventListener('click', add_note);

    // run when form is submitted
    document.querySelector('#new_recipe-button').addEventListener('click', () => {

          new_recipe();
    });
});

function add_ingredient() {

    // create a blank list to add ingredients to and get the value of the ingredients input form
    let ingredients = document.querySelector('#ingredients_entry').value;

    // split by ';' so user can input multiple ingredients at once
    ingredients = ingredients.split(";");

    ingredients.forEach((ingredient) => {

        // trim whitespace and add each ingredient to the overall list
        ingredient.trim();

        if (ingredient != " " && ingredient != "") {

            // add ingredient to the list of ingredients and increment number of ingredients
            ingredients_list.push(ingredient);
            num_ingredients++;

            // create a li element to append each ingredient to
            const ingredient_li = document.createElement('li');
            ingredient_li.setAttribute('class', 'ing-li');
            ingredient_li.innerHTML = ingredient;

            // split into two columns
            if (num_ingredients <= 18) {
                document.querySelector('#ul_1').append(ingredient_li);
            }
            else {
                document.querySelector('#ul_2').append(ingredient_li);
            }
            document.querySelector('#ingredients_entry').value = "";

            // run when ingredient is clicked
            ingredient_li.addEventListener('click', () => {
                document.querySelector('#ingredients_entry').value = ingredient_li.innerHTML;
                ingredient_li.remove();
            });
        }
    });
}

function add_direction() {

    // get the value of the directions input form
    let direction_new = document.querySelector('#instructions_entry').value;

    document.querySelector('#directions-list').innerHTML = '';

    // add direction and direction number to dict
    directions_list.push(direction_new);

    // loop through the list and look for the blank entry (which means direction was clicked on for editing)
    for (dir in directions_list) {

        let current_direction = directions_list[dir]

        // run if direction is being edited
        if (current_direction == '@') {

            if (direction_new == '') {
                directions_list.pop();
                directions_list.splice(dir,1);
                dir--;
                continue;
            }

            else {
                // assign the li element html to the user input direction and update the dict
                directions_list[dir] = direction_new;
                directions_list.pop();
                current_direction = directions_list[dir]
            }
        }

        else if (current_direction == '' || current_direction == ' ') {
            directions_list.pop();
            break
        }

        // create html for direction and append to list
        create_dir_li(current_direction, dir);

        // find html element for direction
        const id_str = '#dir-li' + dir.toString();
        const direction_li = document.querySelector(id_str);

        // increment direction number to the next value
        direction_num++;

        // clear the textarea
        document.querySelector('#instructions_entry').value = "";

        const index = dir;
        direction_li.addEventListener('click', () => click_direction(index));
    }
}

function click_direction(ind) {

    // find html element for direction
    const id_str = '#dir-li' + ind.toString();
    const direction_li = document.querySelector(id_str);

    // change color and font weight to give user click feedback
    direction_li.style.color = "RoyalBlue";
    direction_li.style.fontWeight = "700";

    // move direction to textarea and clear directions list
    let direction = direction_li.innerHTML;
    document.querySelector('#instructions_entry').value = direction;
    let index = directions_list.indexOf(direction);
    directions_list[index] = '@';

    direction_li.removeEventListener('click', () => click_direction(ind));
}

function create_dir_li(text, num) {

    // create html for direction list and append to the ol
    const direction_li = document.createElement('li');
    direction_li.setAttribute('class', 'dir-li');
    const id = 'dir-li' + num.toString();
    direction_li.setAttribute('id', id);
    direction_li.innerHTML = text;
    document.querySelector('#directions-list').append(direction_li);
}

function add_note() {

    // create a blank list to add notes to and get the value of the note input form
    let note = document.querySelector('#note_entry').value;

    if (note != " " && note != "") {

        // add note to the list of notes
        notes_list.push(note);

        // create a li element to append each note to
        const note_li = document.createElement('li');
        note_li.setAttribute('class', 'note-li');
        note_li.innerHTML = note;
        document.querySelector('#notes-list').append(note_li);
        document.querySelector('#note_entry').value = "";

        // run when note is clicked
        note_li.addEventListener('click', () => {
            document.querySelector('#note_entry').value = note_li.innerHTML;
            note_li.remove();
        });
    }
}

async function new_recipe() {

    // get info from input field
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

    // send POST request to /new_post API
    fetch('/add_recipe', options)

    .then(response => {
        if (!response.ok) {
          throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message);
        if (data.message === "Recipe added.") {
            window.location.href = "/";
        }
    })

    return false;
}