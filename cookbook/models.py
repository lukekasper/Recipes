from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm
from django.core.validators import MaxValueValidator, MinValueValidator

import re


class User(AbstractUser):
    """
    Represents a user of the recipes book.
    Adds a "favorites" relationship between a user and a recipe to the built-in Django user model.
    """
    favorites = models.ManyToManyField('Recipe', symmetrical=False, blank=True, related_name="favoriters")

    def serialize(self):
        return {
            "favorites": [recipe.title for recipe in self.favorites.all()],
        }


class Recipe(models.Model):
    """
    Represents a recipe entry into the cookbook"
    """
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, related_name="recipes")
    title = models.CharField(max_length=50, null=True)
    ingredients = models.CharField(max_length=5000, null=True, blank=True)
    instructions = models.CharField(max_length=50000, null=True, blank=True)
    category = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='images/', blank=True)
    cooktime = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=500, blank=True)
    user_rating = models.CharField(max_length=50000, null=True, blank=True)

    def user_rating_dict(self):
        """
        Make a dict object from user rating charfield.
        """
        rating_dict = dict()
        if self.user_rating is not None:

            # get rid of {} and split by dict entry
            rating_str = self.user_rating[1:-1]
            ratings_list = rating_str.split(",")

            # loop through each entry and split into separate key: value pairs
            for entry in ratings_list:
                current_entry = entry.split(":")

                # trim off extra characters from converting between string and dictionary types
                username = current_entry[0].strip()
                rating = current_entry[1].strip()
                start_ind, end_ind = 0, len(username) - 1
                if re.search(r"[a-zA-Z0-9_]", username) is not None:
                    res1 = re.search(r"[a-zA-Z0-9_]", username)
                    res2 = re.search(r"[a-zA-Z0-9_]", username[::-1])
                    start_ind, end_ind = res1.start(), res2.start()
                rating_dict[username[start_ind:len(username) - end_ind]] = int(rating)

        return rating_dict

    def num_ratings(self):
        """
        Get the number of ratings for a given recipes.
        """
        if self.user_rating_dict():
            return len(self.user_rating_dict().values())
        else:
            return 0

    def avg_rating(self):
        """
        Get the average value of the user ratings for display.
        """
        if self.user_rating_dict():
            return round(sum(self.user_rating_dict().values())/self.num_ratings(), 1)
        else:
            return 0

    def stringify_comments(self):
        """
        Get all the comments for a specified recipe.
        """
        if self.recipe_comments.all():
            return [comment.serialize() for comment in self.recipe_comments.order_by("timestamp").all()]
        else:
            return None

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "poster": self.user.username,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "category": self.category,
            "image": self.image.url,
            "cooktime": self.cooktime,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "note": self.note,
            "rating": self.avg_rating(),
            "num_ratings": self.num_ratings(),
            "comments": self.stringify_comments()
        }


class Comment(models.Model):
    """
    Represents a user comment on a recipe.
    """
    text = models.CharField(max_length=250, null=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, related_name="user_comments")
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE, null=True, related_name="recipe_comments")
    timestamp = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "comment": self.text,
            "poster": self.user.username,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p")
        }
