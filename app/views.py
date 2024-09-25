import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt


from .models import User, Recipe, Comment


def login_view(request):
    """
    Handles the user login process. If the request method is POST, it attempts
    to authenticate the user using the provided username and password. If the authentication
    is successful, the user is logged in and redirected to the "index" page. If the
    authentication fails, the login page is re-rendered with an error message.

    If the request method is not POST, it simply renders the login page.
    """
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', reverse('index'))
            return HttpResponseRedirect(next_url)
        else:
            return render(request, "app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        next_url = request.GET.get('next', reverse('index'))
        return render(request, "app/login.html", {'next': next_url})


def logout_view(request):
    """
    Logs out the currently authenticated user by using the Django built-in
    `logout` function. After logging out, the user is redirected to the "index" page.
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    Handles the user registration process. If the request method is POST, it
    attempts to create a new user based on the provided username, email, and password. The
    password must match the password confirmation for successful registration. If the
    registration is successful, the user is logged in and redirected to the "index" page.

    If the request method is not POST, it simply renders the registration page.
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "app/register.html")


def index(request):
    """
    Renders the index template (Home page).
    """
    return render(request, "app/index.html")


@login_required
def new_recipe(request):
    """
    Renders the "new_recipe.html" template, which displays the form for
    creating a new recipe. The view is protected by the `@login_required` decorator, which
    ensures that only authenticated users can access the form.
    """
    return render(request, "app/new_recipe.html")


@login_required
def add_recipe(request):
    """
    Allows authenticated users to add a new recipe to the app by
    submitting a POST request. The recipe information, including title, category, cooktime,
    image, ingredients, directions, and optional notes, is extracted from the request data.
    A new `Recipe` model instance is created and saved to the database with the provided
    information.
    """
    # create recipe from POST info
    if request.method == "POST":

        # get recipe info from fetch
        try:
            title = request.POST.get("title")
            title_lst = title.split(" ")
            new_lst = []
            for word in title_lst:
                word = word[0].upper() + word[1:].lower()
                new_lst.append(word)
            title = " ".join(new_lst)

            if Recipe.objects.filter(title=title).exists():
                error_message = "Recipe with this name already exists!  Please choose a new name."
                return JsonResponse({"error": error_message}, status=400)

            user = request.user
            category = request.POST.get("category")
            category = category[0].upper() + category[1:].lower()

            meal = request.POST.get("meal")
            meal = meal[0].upper() + meal[1:].lower()

            cooktime = request.POST.get("cooktime")

            # get image if one was uploaded, otherwise use stock image
            if request.FILES.get("image", False):
                image = request.FILES["image"]
            else:
                image = "images/no_image.jpeg"

            # add ingredients and directions
            ingredients = list(request.POST.get("ingredients").split(","))
            ingredients_str = ''
            for ingredient in ingredients:
                ingredients_str += ingredient + ","
            ingredients_str = ingredients_str[:-1]
            directions = request.POST.get("instructions")

            # create recipe
            recipe = Recipe(user=user, title=title, ingredients=ingredients_str, instructions=directions, category=category,
                            meal=meal, image=image, cooktime=cooktime)

            # add notes to recipe model if notes were uploaded, otherwise leave blank
            if request.POST.get("notes", False):
                notes = request.POST.get("notes")
            else:
                notes = ''
            recipe.note = notes

            # try to create recipie

            recipe.save()
            return JsonResponse({"message": "Recipe added."}, status=200)

        except json.JSONDecodeError:
            error_message = "Invalid JSON data."
            return JsonResponse({"error": error_message}, status=400)

        # catch issues with incomplete model fields
        except IntegrityError:
            # Handle the IntegrityError
            error_message = "Some required fields are missing. Please fill out all the required fields."
            return JsonResponse({"error": error_message}, status=400)

    # For other request methods (e.g., GET, PUT, DELETE, etc.), return HTTP 405 Method Not Allowed
    error_message = "Only POST method is allowed for this URL."
    return HttpResponseNotAllowed(permitted_methods=["POST"], content=error_message)


def all_recipes(request):
    """
    Retrieves all recipes from the database, sorted by the timestamp in
    descending order. The recipes are then serialized into a JSON response, containing the
    start and end points of the requested recipe list. The start and end points are
    determined by the query parameters 'start' and 'end' in the request and used to paginate the response.
    All recipes query is cached for 10 min.
    """
    try:
        recipes = Recipe.objects.all()
        recipes = recipes.order_by("-timestamp").all()
        recipes = paginate_recipes(request, recipes)

        # .serialize() creates a text string for json object
        return JsonResponse({"recipes": [recipe.serialize() for recipe in recipes]})

    # Handle invalid input (e.g., non-integer values for start/end)
    except ValueError:
        return JsonResponse({"error": "Invalid input parameters."}, status=400)

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_recipe(request, title):
    """
    Retrieves a specific recipe from the database based on its title. 
    The recipe is serialized into a JSON response, and if the user is authenticated,
    a "favorite_flag" indicating whether the recipe is in the user's favorites list is also
    included in the response.
    """
    # get requested recipe and set favorite flag
    try:
        recipe = Recipe.objects.get(title=title)
        favorite_flag = "None"
        remove_flag = "None"

        # if the recipe is in the user's list of favorites, set favorite flag to True
        if request.user.is_authenticated:
            if recipe in request.user.favorites.all():
                favorite_flag = "True"
            else:
                favorite_flag = "False"

            if recipe in Recipe.objects.filter(user=request.user):
                remove_flag = "True"

        return JsonResponse({"recipe": recipe.serialize(), "favorite_flag": favorite_flag, "remove_flag": remove_flag})

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
def delete_recipe(request, title):
    """
    Deletes recipe from database based on its title.
    """
    if request.method == "DELETE":
        try:
            recipe = Recipe.objects.get(title=title)
            recipe.delete()
            return JsonResponse({"message": "Recipe deleted."}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({"message": "Recipe not found."}, status=404)

        # return error code if any other exception occurs
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    error_message = "Only DELETE method is allowed for this URL."
    return HttpResponseNotAllowed(permitted_methods=["DELETE"], content=error_message)

@login_required
@csrf_exempt
def update_recipe(request, title):
    """
    Updates recipe with new content.
    """
    if request.method == "POST":
        try:
            recipe = Recipe.objects.get(title=title)

            # Get Form data
            category = request.POST.get("category")
            category = category[0].upper() + category[1:].lower()

            meal = request.POST.get("meal")
            meal = meal[0].upper() + meal[1:].lower()

            cooktime = request.POST.get("cooktime")

            # add ingredients and directions
            ingredients = list(request.POST.get("ingredients").split(","))
            ingredients_str = ''
            for ingredient in ingredients:
                ingredients_str += ingredient + ","
            ingredients_str = ingredients_str[:-1]

            instructions = request.POST.get("instructions")

            # add notes to recipe model if notes were uploaded, otherwise leave blank
            if request.POST.get("notes", False):
                notes = request.POST.get("notes")
            else:
                notes = ''

            # Update recipe
            recipe.ingredients = ingredients_str
            recipe.instructions = instructions
            recipe.category = category
            recipe.meal = meal
            recipe.cooktime = cooktime
            recipe.note = notes
            recipe.save()

            return JsonResponse({"message": "Recipe updated."}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({"message": "Recipe not found."}, status=404)

        # return error code if any other exception occurs
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    # For other request methods (e.g., GET, PUT, DELETE, etc.), return HTTP 405 Method Not Allowed
    error_message = "Only POST method is allowed for this URL."
    return HttpResponseNotAllowed(permitted_methods=["POST"], content=error_message)


@login_required
@csrf_exempt
def update_rating(request, name):
    """
    Allows authenticated users to update the rating of a specific recipe
    by submitting a PUT request. The request should include a JSON object containing the
    "rating" attribute, which represents the new rating value (an integer between 1 and 5).
    """
    # ensure request was a PUT

    if request.method == "PUT":

        # get recipe info and convert user ratings into a dictionary
        recipe = Recipe.objects.get(title=name)

        try:
            rating_dict = recipe.user_rating_dict()
            signed_user = request.user.username
            rating = json.loads(request.body)
            rating = int(rating)

            # check if rating is an int from 1-5
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return JsonResponse({"error": "Invalid rating. Rating must be an integer between 1 and 5."}, status=400)

            # either add new entry or update existing entry and save
            rating_dict[signed_user] = rating
            recipe.user_rating = str(rating_dict)

            recipe.save()
            return JsonResponse({"avg_rating": recipe.avg_rating(), "num_ratings": recipe.num_ratings()})

        # return error code if invalid JSON data
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data in the request body."}, status=400)

        # return error code if any other exception occurs
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    error_message = "Only PUT method is allowed for this URL."
    return HttpResponseNotAllowed(permitted_methods=["PUT"], content=error_message)


@login_required
@csrf_exempt
def search_recipes(_, title):
    """
    Allows authenticated users to search for recipes that contain specific
    ingredients or have titles that match the search query. The search query is provided in
    the request body as a JSON object with the "search" attribute, which contains a comma-
    separated list of ingredients or a single recipe title.
    """
    # get ingredients list and split into individual ingredients
    # try reading the json data
    try:
        recipes = Recipe.objects.all()
        matched_recipes = set()

        search_list = title.split(", ")

        # loop over all recipes
        for recipe in recipes:

            # clean the ingredients data
            recipe_ingredients_list = recipe.ingredients
            recipe_ingredients_list = recipe_ingredients_list[1:-1]
            recipe_ingredients_list = recipe_ingredients_list.replace('"', '')
            recipe_ingredients_list = recipe_ingredients_list.split(",")

            # if the recipe has the ingredients being searched, add it to the list of recipes to return
            if len(search_list) == 1:
                for ingredient in recipe_ingredients_list:
                    if search_list[0].lower() in ingredient.lower():
                        matched_recipes.add(recipe.title)

            if set(search_list).issubset(set(recipe_ingredients_list)):
                matched_recipes.add(recipe.title)

            # check if search matches a recipe title, if so add it to the matched recipes list
            if len(search_list) == 1:
                if search_list[0].lower() in recipe.title.lower():
                    matched_recipes.add(recipe.title)

        return JsonResponse({"matched_recipes": list(matched_recipes)})

    # return error code if invalid JSON data
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data in the request body."}, status=400)

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def my_recipes(request):
    """
    Allows authenticated users to retrieve recipes they posted. The recipes
    are filtered based on the signed-in user and are ordered by the timestamp of their
    creation. The view returns a JSON response containing the requested recipes.  The start and end
    parameters in the query request are used to paginate the response.
    """
    try:
        # get signed-in user recipes posted by that user and order by post time
        user = request.user
        user_recipes = Recipe.objects.filter(user=user)
        user_recipes = user_recipes.order_by("-timestamp").all()
        user_recipes = paginate_recipes(request, user_recipes)

        # .serialize() creates a text string for json object
        return JsonResponse({"user_recipes": [recipe.serialize() for recipe in user_recipes]})

    except ValueError:
        # Handle invalid input (e.g., non-integer values for start/end)
        return JsonResponse({"error": "Invalid input parameters."}, status=400)

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def cuisines(_):
    """
    Retrieves a list of unique cuisines from the database.
    It goes through all the recipes and extracts their categories (cuisines).
    The unique categories are collected in a list and returned as a JSON response.
    """
    # try loading cuisines
    try:

        recipes = Recipe.objects.all()
        cuisines_list = set()

        for recipe in recipes:
            cuisines_list.add(recipe.category)

        return JsonResponse({"list": list(cuisines_list)})

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def meals(_):
    """
    Retrieves a list of unique meals from the database.
    It goes through all the recipes and extracts their meal type.
    The unique meals are collected in a list and returned as a JSON response.
    """
    # try loading cuisines
    try:

        recipes = Recipe.objects.all()
        meals_list = set()

        for recipe in recipes:
            meals_list.add(recipe.meal)

        return JsonResponse({"list": list(meals_list)})

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def cuisine_recipes(request, cuisine):
    """
    Retrieves all of the recipes of a specific cuisine from the database. The cuisine
    is specified in the URL as a parameter. The recipes are ordered by their timestamp in descending order.
    The view returns a JSON response containing the requested recipes.
    The start and end parameters supplied in the url are used to paginate the response.
    """
    # try loading cuisine recipes
    try:
        recipes = Recipe.objects.filter(category=cuisine)
        recipes = recipes.order_by("-timestamp").all()
        recipes = paginate_recipes(request, recipes)

        # .serialize() creates a text string for json object
        return JsonResponse({"cuisine_recipes": [recipe.serialize() for recipe in recipes]})

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def meal_recipes(request, meal):
    """
    Retrieves all of the recipes of a specific meal type from the database. The meal
    is specified in the URL as a parameter. The recipes are ordered by their timestamp in descending order.
    The view returns a JSON response containing the requested recipes.
    The start and end parameters supplied in the url are used to paginate the response.
    """
    # try loading cuisine recipes
    try:
        recipes = Recipe.objects.filter(meal=meal)
        recipes = recipes.order_by("-timestamp").all()
        recipes = paginate_recipes(request, recipes)

        # .serialize() creates a text string for json object
        return JsonResponse({"meal_recipes": [recipe.serialize() for recipe in recipes]})

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def favorites(request):
    """
    Allows authenticated users to retrieve the recipes they have
    favorited. The recipes are obtained from the "favorites" relationship of the current
    user. The favorites are then serialized into a JSON response and returned.
    """
    # try loading favorite recipes
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        # get recipes favorited by signed in user
        recipes = request.user.favorites.all()

        # .serialize() creates a text string for json object
        return JsonResponse({"list": [recipe.serialize() for recipe in recipes]})

    # return error code if any other exception occurs
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
def update_favorites(request, title):
    """
    Allows authenticated users to update the favorite status of a recipe.
    The recipe's title is specified in the URL as a parameter, and the view checks if the
    request method is a PUT request. If the recipe is already in the user's favorites, it
    will be removed from the favorites list. If it is not in the favorites, it will be added.
    The updated favorite status is returned as a JSON response.
    """
    # ensure method was a PUT request
    if request.method == "PUT":

        # try to get signed-in user, recipe to update, and flag from PUT request
        try:
            user = request.user
            recipe = Recipe.objects.get(title=title)

            # update user's favorites according to flag logic
            if recipe in user.favorites.all():
                user.favorites.remove(recipe)
                flag = "False"
            else:
                user.favorites.add(recipe)
                flag = "True"
            user.save()

            return JsonResponse({"flag": flag})

        # return error code if any other exception occurs
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    error_message = "Only PUT method is allowed for this URL."
    return HttpResponseNotAllowed(permitted_methods=["PUT"], content=error_message)


@login_required
def add_comment(request, title):
    """
    Allows authenticated users to add a new comment to a specific recipe.
    The recipe's title is specified in the URL as a parameter, and the view checks if the
    request method is a POST request. If so, the comment text is extracted from the request's
    JSON data, and a new `Comment` object is created and saved to the database. The JSON
    response contains the serialized representation of the newly created comment.
    """
    if request.method == "POST":
        # get recipe, user, and comment info
        user = request.user
        recipe = Recipe.objects.get(title=title)
        data = json.loads(request.body)
        text = data.get("body")

        # create new comment object
        comment = Comment(text=text, user=user, recipe=recipe)
        comment.save()

        return JsonResponse({"comment": comment.serialize()})

    return JsonResponse({"message": "Post Error."}, status=404)


@login_required
def remove_comment(request, id):
    """
    Allows authenticated users to remove their own comments from a specific
    recipe. The comment to be removed is specified by its unique identifier (ID) provided as
    a URL parameter. The view checks if the request method is a POST request and if the
    authenticated user is the author of the comment. If so, the comment is deleted from the
    database. The view returns a JSON response indicating the status of the comment removal.
    """
    if request.method == 'DELETE':
        # get comment by id and delete from database
        try:
            if Comment.objects.get(id=id):
                comment = Comment.objects.get(id=id)
                if comment.user != request.user:
                    return JsonResponse({"message": "You are not authorized to delete this comment."}, status=403)
                comment.delete()
            return JsonResponse({"message": "Comment Removed."}, status=204)

        # return error if comment does not exist
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Comment not found."}, status=404)

        # return error code if any other exception occurs
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    error_message = "Only PUT DELETE is allowed for this URL."
    return HttpResponseNotAllowed(permitted_methods=["DELETE"], content=error_message)

def paginate_recipes(request, recipes):
    """
    Take in a GET request and return a sliced version of the recipes list.
    """
    start = int(request.GET.get("start") or 0)
    end = start + 10
    total_recipes = len(recipes)

    start = min(start, abs(total_recipes - 1))
    end = min(end, total_recipes)

    # return appropriate recipes
    recipes = recipes[start:end]
    return recipes
