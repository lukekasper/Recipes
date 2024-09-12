from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path('accounts/', include('django.contrib.auth.urls')),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_recipe", views.new_recipe, name="new_recipe"),

    # API routes
    path("add_recipe", views.add_recipe, name="add_recipe"),
    path("all_recipes", views.all_recipes, name="all_recipes"),
    path("recipe_page/<str:title>", views.get_recipe, name="recipe_page"),
    path("update_rating/<str:name>", views.update_rating, name="update_rating"),
    path("search_recipes", views.search_recipes, name="search_recipes"),
    path("my_recipes", views.my_recipes, name="my_recipes"),
    path("cuisines", views.cuisines, name="cuisines"),
    path("cuisine_recipes/<str:cuisine>", views.cuisine_recipes, name="cuisine_recipes"),
    path("favorites", views.favorites, name="favorites"),
    path("update_favorites/<str:title>", views.update_favorites, name="update_favorites"),
    path("add_comment/<str:title>", views.add_comment, name="add_comment"),
    path("remove_comment/<int:id>", views.remove_comment, name="remove_comment"),
    path("delete_recipe/<str:title>", views.delete_recipe, name="delete_recipe"),
    path("update_recipe/<str:title>", views.update_recipe, name="update_recipe")
]
