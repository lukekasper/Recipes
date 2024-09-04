document.addEventListener('DOMContentLoaded', function() {

    // default load all recipes
    load_recipes(user='', cuisine='');

    // run when username is clicked
    if (document.querySelector('#usrname')) {
        document.querySelector('#usrname').addEventListener('click', () => {
            let usrname = document.querySelector('#name').innerHTML;
            load_recipes(user=usrname, cuisine='');
            history.pushState({}, '', "/" + usrname);
        });
    }

    // run when cuisines is clicked
    document.querySelector('#Cuisines-link').addEventListener('click', () => {
        generate_page('Cuisines', '/cuisines', '#cuisines');
        history.pushState({}, '', "/categories");
    });

    // run when favorites is clicked
    document.querySelector('#Favoirtes-link').addEventListener('click', () => {
        generate_page('My Favorites', '/favorites', '#favorites');
        history.pushState({}, '', "/favorites");
    });

    // run when search icon is clicked
    document.querySelector('#search-button').addEventListener('click', search_recipes);
    if (document.querySelector('#search_box').value != '') {
        document.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
              search_recipes();
            }
        });
    }
});

/////////////////////////////////////////////////////////////////////////////////
///////////////////////// ALL RECIPES HOME PAGE /////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////

function generate_page(title, api_path, id) {

    // update page title
    document.querySelector("#recipes-title").innerHTML = title;

     // send API request to get cuisine info
    fetch(`${api_path}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {

        // show cuisines view and hide all others
        document.querySelector('#all_recipes').style.display = 'none';
        document.querySelector('#recipe-view').style.display = 'none';
        document.querySelector('#matched_recipes-view').style.display = 'none';

        if (title == "Cuisines") {
            document.querySelector('#cuisines-view').style.display = 'block';
            document.querySelector('#favorites-view').style.display = 'none';
        }
        else {
            document.querySelector('#cuisines-view').style.display = 'none';
            document.querySelector('#favorites-view').style.display = 'block';
        }

        // clean div
        document.querySelector(id).innerHTML = '';

        data.list.forEach(object => {

            // set the content depending upon search
            let content = object.title;
            if (title == "Cuisines") {
                content = object;
            }

            // make list html and append to ul
            let element = make_html_element(content, content+'_li', 'li_item', 'li');
            document.querySelector(id).append(element);

            // add event listener to link to clicked recipes page and change color when mouseover
            element.addEventListener('mouseover', () => {element.style.color = "Blue";});
            element.addEventListener('mouseout', () => {element.style.color = "Black";});

            if (title == "Cuisines") {
                // load all recipes with that category
                element.addEventListener('click', () => load_recipes(user='', cuisine=content));
            }
            else {
                // load that recipes page when name is clicked
                element.addEventListener('click', () => load_recipe(content));
            }
        });
    })
    .catch(error => {
        console.error('Network Error: ', error);
    });
}

function load_recipes(user, cuisine) {

    // clean errors
    //document.querySelector("#query_error").innerHTML = '';
    //document.querySelector("#search_error").innerHTML = '';

    let start = 0;
    let end = start + 9;

    // hide recipe view and show all recipes
    document.querySelector('#all_recipes').style.display = 'block';
    document.querySelector('#recipe-view').style.display = 'none';
    document.querySelector('#matched_recipes-view').style.display = 'none';
    document.querySelector('#cuisines-view').style.display = 'none';
    document.querySelector('#favorites-view').style.display = 'none';

    // clear all recipes html
    document.querySelector('#all_recipes').innerHTML = '';

    // get requested recipes and generate html (user recipes, recipes by cuisine, or all recipes)
    if (user != '') {
        query_recipes('/my_recipes', 'user_recipes', user+"'s Recipes", start, end);
    }
    else if (cuisine != '') {
        query_recipes('/cuisine_recipes/'+cuisine, 'cuisine_recipes', '"' + cuisine + '" Recipes', start, end);
    }
    else {
        query_recipes('/all_recipes', 'recipes', 'All Recipes', start, end);
    }

    // if bottom of screen is reached, load the next 10 recipes
    window.onscroll = () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
            start += 10; // update counter
            end += 10;

            // get requested recipes and generate html (user recipes, recipes by cuisine, or all recipes)
            if (user != '') {
                query_recipes('/my_recipes', 'user_recipes', user+"'s Recipes", start, end);
            }
            else if (cuisine != '') {
                query_recipes('/cuisine_recipes/'+cuisine, 'cuisine_recipes', '"' + cuisine + '" Recipes', start, end);
            }
            else {
                query_recipes('/all_recipes', 'recipes', 'All Recipes', start, end);
            }
        }
    };
}

// query recipes and generate html
async function query_recipes(api_path, key, title, start, end) {

    // Send API request to get recipes
    const responseJSON = await getData(api_path, 'start', start, 'end', end);

    if (!responseJSON.responseError) {

        // render a div for each post, displaying relevant info
        const data = responseJSON.responseData;
        data[key].forEach(recipe => {

            // run function to generate html
            make_recipe_html(recipe);
        });

        // update page title
        document.querySelector('#recipes-title').innerHTML = title;
    }

    // display response error on front end
    else {
        const error = responseJSON.responseError;
        document.querySelector("#query_error").innerHTML = error;
    }
}


function make_recipe_html(recipe) {

    // create an outer div for to contain image and post's info
    const outerDiv = make_html_element('', 'outer-div_'+recipe.title, 'outer-div', 'div');
    const imageDiv = make_html_element('', 'image-div_'+recipe.title, 'image-div', 'div');
    const infoDiv = make_html_element('', 'info-div_'+recipe.title, 'info-div', 'div');

    // make comments div
    const commentsDiv = make_html_element('', 'comments-div_'+recipe.title, 'comments-div', 'div');
    commentsDiv.append(make_html_element('Comments:', '', 'comments-header', 'h6'));
    commentsDiv.append(make_html_element('', 'comments-container_'+recipe.title, 'comments-container', 'div'));
    commentsDiv.append(make_html_element('', 'comments-inner_'+recipe.title, 'comments-inner', 'div'));

    // add star rating system
    let stars = make_stars(recipe);

    // create comments button
    const comments_button = make_html_element('Show Comments', 'comments-button_'+recipe.title, 'comments-button', 'button');
    comments_button.addEventListener('click', () => show_comments(recipe.comments, recipe.title));

    // make html
    const line_hr = document.createElement('hr');
    const title = make_html_element(recipe.title, 'title_'+recipe.title, 'title', 'p');
    const image = make_image_html(recipe.image, 'image');

    // append info to outer div
    imageDiv.append(image);
    infoDiv.append(title);
    infoDiv.append(make_html_element("Category: " + recipe.category, recipe.title+'_category', 'category', 'p'));
    infoDiv.append(make_html_element(recipe.timestamp, recipe.title+'_timestamp', 'timestamp', 'p'));
    infoDiv.append(stars);
    infoDiv.append(comments_button);
    outerDiv.append(imageDiv);
    outerDiv.append(infoDiv);
    document.querySelector("#all_recipes").append(outerDiv);
    document.querySelector("#all_recipes").append(commentsDiv);
    document.querySelector("#all_recipes").append(line_hr);

    // default to hiding comments
    document.querySelector('#comments-div_'+recipe.title).style.display = 'none';

    // add event listener for poster to change color when moused over
    title.addEventListener('mouseover', () => {title.style.color = "Blue";});
    title.addEventListener('mouseout', () => {title.style.color = "Black";});

    // do the same for for clicking image or title of recipe
    title.addEventListener('click', () => load_recipe(recipe.title));
    image.addEventListener('click', () => load_recipe(recipe.title));
}

// create star rating system
function make_stars(recipe) {

    const stars = document.createElement('p');
    const s1 = document.createElement('span');
    const s2 = document.createElement('span');
    const s3 = document.createElement('span');
    const s4 = document.createElement('span');
    const s5 = document.createElement('span');

    let span_list = [s1, s2, s3, s4, s5];

    // loop through the star spans, and check the number based on the recipe rating
    for (let i=0; i<5; i++) {
        if (i+1 <= Math.round(recipe.rating)) {
            span_list[i].setAttribute('class', 'fa fa-star checked');
        }
        else {
            span_list[i].setAttribute('class', 'fa fa-star');
        }
        span_list[i].setAttribute('id', recipe.title+'_star_'+i);

        // only allow a user rating if signed in
        if (document.querySelector('#usrname')) {
            span_list[i].addEventListener('mouseover', () => color_stars(recipe.title, i, span_list));
            span_list[i].addEventListener('mouseout', () => uncolor_stars(recipe.title, recipe.rating, span_list));
            span_list[i].addEventListener('click', () => update_rating(recipe.title, i));
        }
        stars.append(span_list[i]);
    }

    // add average and number of ratings and append to stars div
    const rating = make_html_element(recipe.rating, recipe.title+'_rating', 'rating', 'span');
    const num_ratings = make_html_element("("+recipe.num_ratings+")", recipe.title+'num_ratings', 'num_ratings', 'span');
    stars.append(rating);
    stars.append(num_ratings);

    return stars
}

// create html for showing comments section or hiding it
function show_comments(comments, title) {

    if (document.querySelector('#comments-button_'+title).innerHTML == 'Show Comments') {

        // show comments div
        document.querySelector('#comments-div_'+title).style.display = 'block';
        document.querySelector('#comments-div_'+title).animate(
            {
                height: ["5px", "5px", "220px"],
                width: ["0%", "38%", "38%"],
                lineHeight: ["0%", "0%", "100%"],
                lineWidth: ["0%", "100%", "100%"],
                padding: ["0px", "0px", "10px"],
            },
            400
        );

        document.querySelector('#comments-inner_'+title).innerHTML = '';
        document.querySelector('#comments-container_'+title).innerHTML = '';

        if (comments != null) {
            comments.forEach(comment => {
                // make html for each comment and append to comments div
                make_comment_html(comment, title);
            });
        }

        // make textarea to add a comment
        const add_comment_box = make_html_element('', 'add_comment-box_'+title, 'add_comment_box', 'textarea');
        add_comment_box.setAttribute('placeholder','Add a comment...');
        document.querySelector('#comments-inner_'+title).append(add_comment_box);

        // make button to add comment
        const add_comment_button = make_html_element('Add Comment', 'add_comment-but_'+title, 'btn btn-sm btn-outline-primary', 'button');
        document.querySelector('#comments-inner_'+title).append(add_comment_button);
        add_comment_button.style.width = "95px";
        add_comment_button.style.height = "25px";
        add_comment_button.style.fontSize = "11px";

        // if the user has something written in the textarea, submit comment and append html when 'Add Button' is clicked
        add_comment_button.addEventListener('click', () => {
            if (add_comment_box.value.length > 1) {
                add_comment(add_comment_box.value, title);
            }
        });

        // change button html
        document.querySelector('#comments-button_'+title).innerHTML = 'Hide Comments';
    }

    else {
        // hide comments div
        document.querySelector('#comments-div_'+title).animate(
            {
                height: ["220px", "220px", "5px"],
                width: ["38%", "38%", "0%"],
                lineHeight: ["100%", "0%", "0%"],
                lineWidth: ["100%", "0%", "0%"],
                padding: ["10px", "0px", "0px"],
            },
            200
        );
        setTimeout(()=> {document.querySelector('#comments-div_'+title).style.display = 'none'},180);
        document.querySelector('#comments-button_'+title).innerHTML = 'Show Comments'
    }
}

function make_comment_html(comment, title) {

    // make html for comment
    const comment_p = make_html_element('', 'comment-p_'+comment.id, 'comment-p', 'p');
    const poster = make_html_element(comment.poster + ':&nbsp;', comment.poster+'comment', 'comment-poster', 'span');
    const comment_txt = make_html_element(comment.comment, comment.id, 'comment_txt', 'span');
    comment_p.append(poster);
    comment_p.append(comment_txt);

    // add an option to delete comment if it the signed in user posted it
    let usrname = document.querySelector('#name').innerHTML;
    const x = make_image_html("https://icons.veryicon.com/png/o/miscellaneous/kqt/close-116.png", 'x'+comment.id);
    x.setAttribute('class','x');
    comment_p.append(x);
    x.style.display = 'none';
    document.querySelector('#comments-container_'+title).prepend(comment_p);

    if (typeof usrname !== 'undefined' && usrname == comment.poster) {

        // display when mouseover
        comment_p.addEventListener('mouseover', () => {x.style.display = 'block'});

        // hide when mouse-off
        comment_p.addEventListener('mouseout', () => {x.style.display = 'none'});

        // if clicked, delete comment from front-end and backend
        x.addEventListener('click', () => remove_comment(comment, comment_p));
    }
}

function remove_comment(comment, comment_p) {

    // send API request to remove comment from backend
    fetch(`/remove_comment/${comment.id}`)
    .then(response => {
        if (!response.ok) {
          throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(() => {
        comment_p.remove();
    })
    .catch(error => {
        console.error('Netwrok Error: ', error);
    });
}

// update comment model on backend
function add_comment(comment_txt, title) {

    fetch('/add_comment/'+title, {
        method: 'POST',
        body: JSON.stringify({
            comment: `${comment_txt}`
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        make_comment_html(data.comment, title);
        document.querySelector('#add_comment-box_'+title).value = '';
    })
    .catch(error => {
        console.error('Netwrok Error: ', error);
    });
}

// make standard html text element
function make_html_element(text, id, cls, element_type) {

    const element = document.createElement(element_type);
    element.innerHTML = text;
    element.setAttribute('id', id);
    element.setAttribute('class', cls);
    return element
}

// make image html element
function make_image_html(image_src, id) {

    const element = document.createElement('img');
    element.src = image_src;
    element.setAttribute('id', id);
    return element
}

//update rating in django model and style css accordingly
function update_rating(title, i) {

    // update the rating on the backend
    fetch('/update_rating/'+title, {
        method: 'PUT',
        body: JSON.stringify({
            rating: i+1
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {

        // update avg rating html for selected recipe and reload recipes
        document.querySelector('#'+title+'_rating').innerHTML = data.avg_rating;
        load_recipes(user='', cuisine='');
    })
    .catch(error => {
        console.error('Netwrok Error: ', error);
    });
}

// color stars when mouse over
function color_stars(title, i, span_list) {

    // style stars according to user rating to provide front-end feedback
    for (j=0; j<5; j++) {

        if (j<=i) {
            span_list[j].style.color = 'RoyalBlue';
        }
        else {
            span_list[j].style.color = 'Black';
        }
    }
}

//uncolor stars when mouse is off stars
function uncolor_stars(title, rating, span_list) {

    // style stars according to user rating to provide front-end feedback
    for (j=0; j<5; j++) {

        if (j<rating) {
            span_list[j].style.color = 'Orange';
        }
        else {
            span_list[j].style.color = 'Black';
        }
    }
}

/////////////////////////////////////////////////////////////////////////////////
///////////////////////// LOAD INDIVIDUAL RECIPES PAGE //////////////////////////
/////////////////////////////////////////////////////////////////////////////////

// load recipe page
function load_recipe(title) {

    // show user profile view and hide others
    document.querySelector('#all_recipes').style.display = 'none';
    document.querySelector('#recipe-view').style.display = 'block';
    document.querySelector('#matched_recipes-view').style.display = 'none';
    document.querySelector('#cuisines-view').style.display = 'none';
    document.querySelector('#favorites-view').style.display = 'none';

    // send API request to get recipe info
    fetch('/recipe_page/'+title)
    .then(response => {
        if (!response.ok) {
          throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {

        document.querySelector('#recipe-image-div').innerHTML = '';
        document.querySelector('#top-recipe-info').innerHTML = '';
        document.querySelector('#recipe-info-lists').innerHTML = '';

        // create recipe html
        const image = make_image_html(data.recipe.image, 'recipe-image');

        // add title to page header and make buttons
        const title = make_html_element(data.recipe.title, 'recipe-title', 'recipe-title', 'h2');
        const title_container = make_html_element('', 'title-container', 'title-container', 'div');

        if (data.remove_flag == "True") {
            const delete_button = make_html_element("Delete Recipe", 'delete-recipe', 'btn btn-sm btn-outline-danger', 'button');
            const modify_button = make_html_element("Modify Recipe", 'modify-recipe', 'btn btn-sm btn-outline-primary', 'button');

            // Event listeners for modification/deletion of recipe
            delete_button.addEventListener('click', () => delete_recipe(data.recipe.title));

            title_container.append(delete_button);
            title_container.append(title);
            title_container.append(modify_button);
        }
        else {
            title_container.append(title);
        }

        // make recipe header
        let stars = make_stars(data.recipe);
        stars.setAttribute('id','single-recipe-stars');
        const poster_container = make_html_element("|&nbsp;&nbsp;&nbsp;&nbsp;Recipe by ", 'poster-container', '', 'p');
        const poster = make_html_element(data.recipe.poster, 'recipe-poster', '', 'span');
        poster_container.append(poster);
        const timestamp = make_html_element("|&nbsp;&nbsp;&nbsp;&nbsp;" + data.recipe.timestamp, 'recipe-timestamp', '', 'p');
        const top_div = make_html_element('', 'top-div', '', 'div');
        top_div.append(stars);
        top_div.append(poster_container);
        top_div.append(timestamp);

        // split strings into lists
        const ingredients_list = data.recipe.ingredients.split(',');
        const directions_list = data.recipe.instructions.split(',');
        const notes_list = data.recipe.note.split(',');

        // make outer list html
        const ing_ul = make_html_element('', 'ing_ul', 'recipe_list_items', 'ul');
        const dir_ol = make_html_element('', 'dir_ol', 'recipe_list_items', 'ol');
        const notes_ul = make_html_element('', 'notes_ul', 'recipe_list_items', 'ul');

        // append ingredients to ul
        ingredients_list.forEach(ingredient => {

            // trim off extra " and ] characters
            ingredient = trim_chars(ingredient);
            ing_ul.append(make_html_element(ingredient, 'ing_li', '', 'li'));
        })

        // append directions to ol
        directions_list.forEach(direction => {
            direction = trim_chars(direction);
            dir_ol.append(make_html_element(direction, 'dir_li', '', 'li'));
        })

        // append notes to ul
        notes_list.forEach(note => {

            // if note is not empty
            if (note != '') {
                note = trim_chars(note);
                notes_ul.append(make_html_element(note, 'note_li', 'recipe_list_items', 'li'));
            }
        })

        const category = make_html_element(data.recipe.category, '', 'info', 'div');
        const cooktime = make_html_element(data.recipe.cooktime, '', 'info', 'div');

        // make box for category and time
        const cat_container = make_html_element('', 'cat-container', 'recipe-container', 'div');
        const time_container = make_html_element('', 'time-container', 'recipe-container', 'div');
        const info_box = make_html_element('', 'recipe-info_box', '', 'div');

        const cat_title = make_html_element('Category:', 'cat-title', 'title', 'div');
        const time_title = make_html_element('Cooktime:', 'time-title', 'title', 'div');

        cat_container.append(cat_title);
        cat_container.append(category);
        time_container.append(time_title);
        time_container.append(cooktime);

        info_box.append(cat_container);
        info_box.append(time_container);

        const box_div = make_html_element('', 'box_div', 'box_div', 'div');
        box_div.append(info_box);

        // make containers and add info for ingredients, directions
        const ing_div = make_html_element('Ingredients:', 'ing_div', 'recipe_list_div', 'div');
        ing_div.append(ing_ul);

        const dir_div = make_html_element('Directions:', 'dir_div', 'recipe_list_div', 'div');
        dir_div.append(dir_ol);

        // append recipe info and image to index layout
        document.querySelector("#recipe-image-div").append(image);
        document.querySelector("#top-recipe-info").append(title_container);
        document.querySelector("#top-recipe-info").append(top_div);
        document.querySelector("#top-recipe-info").append(box_div);
        document.querySelector("#recipe-info-lists").append(make_html_element('', 'hr-box', '', 'hr'));
        document.querySelector("#recipe-info-lists").append(ing_div);
        document.querySelector("#recipe-info-lists").append(dir_div);

        // if notes exist, append a div for them
         if (notes_list.length != 0) {
            const notes_div = make_html_element('Notes:', 'notes_div', 'recipe_list_div', 'div');
            notes_div.append(notes_ul);
            document.querySelector("#recipe-info-lists").append(notes_div);
         }

        // widget to add/remove recipe from favorites
        if (data.favorite_flag == "None") {

            // hide favorites button if user is not signed in
            document.querySelector('#favorites-div').style.display = 'none';
        }
        else {

            // show favorites button
            document.querySelector('#favorites-div').style.display = 'block';

            // determine if recipe is already in user's favorited list
            if (data.favorite_flag == "True") {
                document.querySelector('#favorites-button').innerHTML = "Remove from Favorites";
            }
            else {
                document.querySelector('#favorites-button').innerHTML = "Add to Favorites";
            }

            // update user's favorites when button is clicked
            document.querySelector('#favorites-button').addEventListener('click', () =>
            update_favorites(data.recipe.title, data.favorite_flag), true);
        }
    })
    .catch(error => {
        console.error('Netwrok Error: ', error);
    });
}

// Delete recipe from database
function delete_recipe(title) {
    fetch('/delete_recipe/'+title)
    .then(response => {
        if (!response.ok) {
          throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message);
        if (data.message === "Recipe deleted.") {
            window.location.href = "/";
        }
    })
    .catch(error => {
        console.error('Netwrok Error: ', error);
    });
}

// update user's favorite recipes
function update_favorites(title, flag) {

    // send API request to update user's favorite recipes list
    fetch('/update_favorites/'+title)

    // reload recipe page
    .then(response => {
        if (!response.ok) {
          throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {

        // update button logic to opposite state
        if (data.flag == "True") {
            document.querySelector('#favorites-button').innerHTML = "Remove from Favorites";
        }
        else {
            document.querySelector('#favorites-button').innerHTML = "Add to Favorites";
        }
    })
    .catch(error => {
        console.error('Netwrok Error: ', error);
    });
}

// trim off extra characters
function trim_chars(text) {

    // trim off extra " and ] characters
    text = text.slice(1, -1);
    if (text[0] == '"') {
        text = text.slice(1,);
    }
    if (text.charAt(text.length-1) == '"') {
        text = text.slice(0,-1);
    }
    return text
}

// send API request to search for recipes with listed ingredients
function search_recipes() {

    // get list of ingredients from search input box
    const search = document.querySelector("#search_box").value;

    // send API request to get recipes with listed ingredients
    fetch('/search_recipes', {
        method: 'POST',
        body: JSON.stringify({
            search: `${search}`
        })
    })
    .then(response => {
        if (!response.ok) {
          throw new Error('Error: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {

        // show matched recipes view
        document.querySelector('#all_recipes').style.display = 'none';
        document.querySelector('#recipe-view').style.display = 'none';
        document.querySelector('#matched_recipes-view').style.display = 'block';
        document.querySelector('#cuisines-view').style.display = 'none';
        document.querySelector('#favorites-view').style.display = 'none';

        document.querySelector("#ul1").innerHTML = '';
        document.querySelector("#ul2").innerHTML = '';

        let rec1 = document.querySelector("#ul1");
        let rec2 = document.querySelector("#ul2");
        let recipe_side = 1;

        // display html block and add search to header
        document.querySelector('#header').innerHTML = search;

        // show matched ingredients view if API request returns elements
        if (data.matched_recipes.length != 0) {

            // loop through matched recipes
            data.matched_recipes.forEach(recipe => {

                // make html li elements for recipe and append to matched recipes div
                let recipe_el = make_html_element(recipe, recipe+'_li', 'matched_recipe-list', 'li');

                // split into two columns
                if (recipe_side == 1) {
                    rec1.append(recipe_el);
                }
                else {
                    rec2.append(recipe_el);
                }

                recipe_side *= -1;

                // add event listener to link to clicked recipes page and change color when mouseover
                recipe_el.addEventListener('mouseover', () => {recipe_el.style.color = "Blue";});
                recipe_el.addEventListener('mouseout', () => {recipe_el.style.color = "Black";});

                // load that recipes page when name is clicked
                recipe_el.addEventListener('click', () => load_recipe(recipe));
            });
        }

        // clear search bar
        document.querySelector('#search_box').value = '';
    })
    .catch(error => {
        console.error('Netwrok Error: ', error);
    });
}

// GET request
async function getData(url, param1Name = '', data1 = '', param2Name = '', data2 = '') {
    let responseJSON = {responseData: '', responseError: ''};

    // Append the data as a query parameter to the URL
    let urlWithParams = `${url}`;
    if (param2Name.length != 0) {
        urlWithParams = `${url}?${param1Name}=${encodeURIComponent(data1)}&${param2Name}=${encodeURIComponent(data2)}`;
    }
    else if (param1Name.length != 0) {
        urlWithParams = `${url}?${param1Name}=${encodeURIComponent(data1)}`;
    }

    try {
        const response = await fetch(urlWithParams, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // used to handle HTTP Error Responses
        if (!response.ok) {
            // If the response is not OK, handle the error
            const errorMessage = await response.text();
            console.error('Error:', errorMessage);
            responseJSON.responseError = errorMessage;
            return responseJSON
        }

        // if response is ok, return the data
        responseJSON.responseData = await response.json();
        return responseJSON
    }
    catch (error) {
        // Handle the error that occurred during the asynchronous operation
        console.error('Network error:', error);
        responseJSON.responseError = error;
        return responseJSON
    }
}