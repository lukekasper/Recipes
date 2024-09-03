import json
import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Recipe, Comment


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "cookbook/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "cookbook/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "cookbook/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "cookbook/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "cookbook/register.html")


def index(request):
    return render(request, "cookbook/index.html")


@csrf_exempt
@login_required
def new_recipe(request):
    return render(request, "cookbook/new_recipe.html")


@csrf_exempt
@login_required
def add_recipe(request):

    # create recipe from POST info
    if request.method == "POST":

        # get recipe info from fetch
        title = request.POST.get("title")
        user = request.user
        category = request.POST.get("category")
        cooktime = request.POST.get("cooktime")

        # get image if one was uploaded, otherwise use stock image
        if request.FILES.get("image", False):
            image = request.FILES["image"]
        else:
            image = "images/no_image.jpeg"

        # create recipe
        recipe = Recipe(user=user, title=title, category=category, image=image, cooktime=cooktime)

        # add directions and notes to recipe model (if notes were uploaded, otherwise leave blank)
        directions = request.POST.get("instructions")
        if request.POST.get("notes", False):
            notes = request.POST.get("notes")
        else:
            notes = ''

        # see if any of the ingredients are a sub-recipe, if so add it as one and remove from ingredients
        ingredients = list(request.POST.get("ingredients").split(","))
        ingredients_str = ''
        for ingredient in ingredients:
            if Recipe.objects.filter(title=ingredient):
                sub_rec = Recipe.objects.get(title=ingredient)
                ingredients.remove(ingredient)
                recipe.sub_recipe.add(sub_rec)
            else:
                ingredients_str += ingredient + ","
        ingredients_str = ingredients_str[:-1]

        # update recipe details
        recipe.ingredients = ingredients_str
        recipe.instructions = directions
        recipe.note = notes
        recipe.save()

        HttpResponseRedirect("index")

    return JsonResponse({"message": "Post Error."}, status=404)


def all_recipes(request):

    recipes = Recipe.objects.all()
    recipes = recipes.order_by("-timestamp").all()

    # .serialize() creates a text string for json object
    return JsonResponse({"recipes": [recipe.serialize() for recipe in recipes]})


def get_recipe(request, name):

    # get requested recipe and set favorite flag
    recipe = Recipe.objects.get(title=name)
    favorite_flag = "None"

    # if the recipe is in the user's list of favorites, set favorite flag to True
    if request.user.is_authenticated:
        if recipe in request.user.favorites.all():
            favorite_flag = "True"
        else:
            favorite_flag = "False"

    return JsonResponse({"recipe": recipe.serialize(), "favorite_flag": favorite_flag})


@csrf_exempt
@login_required
def update_rating(request, name):

    # get recipe info and convert user ratings into a dictionary
    recipe = Recipe.objects.get(title=name)
    rating_dict = recipe.user_rating_dict()
    signed_user = request.user.username
    data = json.loads(request.body)

    # either add new entry or update existing entry and save
    rating_dict[signed_user] = data.get("rating")
    recipe.user_rating = str(rating_dict)
    recipe.save()

    return JsonResponse({"avg_rating": recipe.avg_rating(), "num_ratings": recipe.num_ratings()})


@csrf_exempt
@login_required
def search_recipes(request):

    # get ingredients list and split into individual ingredients
    if request.method == "POST":
        data = json.loads(request.body)
        search = data.get("search")

        recipes = Recipe.objects.all()
        matched_recipes = set()

        search_list = search.split(", ")

        # loop over all recipes
        for recipe in recipes:

            # clean the ingredients data
            recipe_ingredients_list = recipe.ingredients
            recipe_ingredients_list = recipe_ingredients_list[1:-1]
            recipe_ingredients_list = recipe_ingredients_list.replace('"', '')
            recipe_ingredients_list = recipe_ingredients_list.split(",")

            # if the recipe has the ingredients being searched, add it to the list of recipes to return
            if set(search_list).issubset(set(recipe_ingredients_list)):
                matched_recipes.add(recipe.title)

            # check if search matches a recipe title, if so add it to the matched recipes list
            if len(search_list) == 1:
                if search_list[0] in recipe.title:
                    matched_recipes.add(recipe.title)

        return JsonResponse({"matched_recipes": list(matched_recipes)})

    return JsonResponse({"message": "Post Error."}, status=404)


@csrf_exempt
@login_required
def my_recipes(request):

    # get signed-in user recipes posted by that user and order by post time
    user = request.user
    user_recipes = Recipe.objects.filter(user=user)
    user_recipes = user_recipes.order_by("-timestamp").all()

    # .serialize() creates a text string for json object
    return JsonResponse({"user_recipes": [recipe.serialize() for recipe in user_recipes]})


def cuisines(request):

    recipes = Recipe.objects.all()
    cuisines_list = set()

    for recipe in recipes:
        cuisines_list.add(recipe.category)

    return JsonResponse({"list": list(cuisines_list)})


def cuisine_recipes(request, cuisine):

    recipes = Recipe.objects.filter(category=cuisine)
    recipes = recipes.order_by("-timestamp").all()

    # .serialize() creates a text string for json object
    return JsonResponse({"cuisine_recipes": [recipe.serialize() for recipe in recipes]})


@login_required
def favorites(request):

    # get recipes favorited by signed in user
    recipes = request.user.favorites.all()

    # .serialize() creates a text string for json object
    return JsonResponse({"list": [recipe.serialize() for recipe in recipes]})


@login_required
@csrf_exempt
def update_favorites(request, title):

    # get signed-in user, recipe to update, and flag from PUT request
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


@login_required
@csrf_exempt
def add_comment(request, title):

    if request.method == "POST":

        # get recipe, user, and comment info
        user = request.user
        recipe = Recipe.objects.get(title=title)
        data = json.loads(request.body)
        text = data.get("comment")

        # create new comment object
        comment = Comment(text=text, user=user, recipe=recipe)
        comment.save()

        return JsonResponse({"comment": comment.serialize()})

    return JsonResponse({"message": "Post Error."}, status=404)


@login_required
def remove_comment(request, id):

    # get comment by id and delete from database
    if Comment.objects.get(id=id):
        comment = Comment.objects.get(id=id)
        comment.delete()

    return JsonResponse({"message": "Comment Removed."}, status=200)
