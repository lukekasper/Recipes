import subprocess
import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from django.utils import timezone
import re
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .custom_storage import OverwriteStorage
from django.core.files import File
from io import BytesIO


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
    Represents a recipe entry into the app"
    """
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, related_name="recipes")
    title = models.CharField(max_length=50, null=True)
    ingredients = models.CharField(max_length=5000, null=True, blank=True)
    instructions = models.CharField(max_length=50000, null=True, blank=True)
    category = models.CharField(max_length=50, null=True)
    meal = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='images/', storage=OverwriteStorage(), blank=True)
    cooktime = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=500, blank=True)
    user_rating = models.CharField(max_length=50000, null=True, blank=True)


    # def save(self, *args, **kwargs):
    #     """
    #     Override image save method to crop photo to square for display.
    #     """
    #     if self.image:
    #         print(f"Image name: {self.image.name}")
    #         print(f"Image URL: {self.image.url}")
    #         print(f"Image path: {self.image.path}")

    #         AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    #         AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    #         if "images/images" in self.image.name:
    #             self.image.name = os.path.basename(self.image.name)
    #             print(f"Corrected name: {self.image.name}")
    #             self.image.path = f'/media/images/{self.image.name}'
    #             print(f"Corrected URL: {self.image.url}")
    #             self.image.url = f'https://{AWS_S3_CUSTOM_DOMAIN}/images/{self.image.name}'
    #             print(f"Corrected path: {self.image.path}")

    #         self.image.file.seek(0)  # Reset file pointer
    #         img = Image.open(self.image.file)

    #         print("Image opened")
    #         img = img.convert('RGB')
    #         print("Image rgb")
    #         width, height = img.size
    #         min_side = min(width, height)
    #         left = (width - min_side) / 2
    #         top = (height - min_side) / 2
    #         right = (width + min_side) / 2
    #         bottom = (height + min_side) / 2
    #         img = img.crop((left, top, right, bottom))
    #         print("Image cropped")
    #         img_io = BytesIO()
    #         img.save(img_io, format='JPEG')
    #         print("Image io saved")

    #         self.image.save(self.image.name, img_io, save=False)

    #     print("Super Save")
    #     super().save(*args, **kwargs)  # Call the "real" save() method to save the image field


    def save(self, *args, **kwargs):

        img_flag = kwargs.pop('flag', True)
        
        # Construct the AWS CLI command
        if img_flag:
            bucket_name = os.getenv('BUCKETEER_BUCKET_NAME')
            object_name = f'media/images/{self.image.name}'
            save_path = os.path.join(settings.MEDIA_ROOT, 'images')
            fs = FileSystemStorage(location=save_path)

            if self.image.file.readable():
                fs.save(self.image.name, self.image.file)

            else:
                # Fallback logic: Use static image in the source code
                static_file_path = os.path.join(
                    settings.BASE_DIR, 'static', 'images', 'no_image.jpeg'
                )

                try:
                    # Open the static file and wrap it in a Django File object
                    with open(static_file_path, 'rb') as f:
                        file_content = BytesIO(f.read())  # Read content and wrap in BytesIO
                        fallback_image = File(file_content, name='no_image.jpeg')

                        # Assign the fallback image to the ImageField
                        self.image.save(fallback_image.name, fallback_image, save=False)
                except FileNotFoundError:
                    print("Not saved!")
                    raise ValueError("Fallback image not found in static/images!")
                
            file_url = save_path + "/" + self.image.name

            command = [
                'aws', 's3', 'cp', file_url,
                f's3://{bucket_name}/{object_name}'
            ]

            try:
                # Run the command using subprocess
                result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print("Upload successful:", result.stdout.decode('utf-8'))
            except subprocess.CalledProcessError as e:
                print("Upload failed:", e.stderr.decode('utf-8'))
        else:
            print("No new image uploaded, using original image.")

        super().save(*args, **kwargs)

    
    def delete(self, *args, **kwargs):

        if self.image.name != "images/no_image.jpeg":
            bucket_name = os.getenv('BUCKETEER_BUCKET_NAME')
            object_name = f'media/{self.image.name}'

            command = [
                'aws', 's3', 'rm',
                f's3://{bucket_name}/{object_name}'
            ]

            try:
                # Run the command using subprocess
                result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print("Delete successful:", result.stdout.decode('utf-8'))
            except subprocess.CalledProcessError as e:
                print("Delete failed:", e.stderr.decode('utf-8'))

        super().delete(*args, **kwargs)


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
            return [comment.serialize() for comment in self.recipe_comments.order_by("-timestamp").all()]
        else:
            return None

    def serialize(self):
        local_timestamp = timezone.localtime(self.timestamp)
        return {
            "id": self.id,
            "title": self.title,
            "poster": self.user.username,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "category": self.category,
            "meal": self.meal,
            "image": self.image.url,
            "cooktime": self.cooktime,
            "timestamp": local_timestamp.strftime("%b %d %Y, %I:%M %p"),
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
