from django.test import Client, TestCase

from .models import User, Recipe, Comment


# Test Cases for Backend
class RecipeTestCase(TestCase):

    def setUp(self):
        # create users
        u1 = User.objects.create(username="lukek", password="pass123")
        u2 = User.objects.create(username="megm", password="pass321")

        # create recipes
        ing_str1 = "peanut butter, jelly, bread"
        directions1 = "spread peanut butter on one bread slice, spread jam on other slice, put slices together"
        user_rating = "{lukek: 4, megm: 3}"
        r1 = Recipe.objects.create(user=u1, title="pb&j", ingredients=ing_str1, instructions=directions1,
                                   category="lunch", image="images/no_image.jpeg", cooktime="5 min",
                                   user_rating=user_rating)

        # create comments
        c1 = Comment.objects.create(text="this is good", user=u1, recipe=r1)

    def test_user_rating_dict(self):
        """Test ability to make a dict object from user rating charfield"""
        r1 = Recipe.objects.get(title="pb&j")
        self.assertIsInstance(r1.user_rating_dict(), dict)

    def test_num_ratings(self):
        """Test ability to count the number of user ratings"""
        r1 = Recipe.objects.get(title="pb&j")
        self.assertEqual(r1.num_ratings(), 2)

    def test_avg_rating(self):
        """Test ability to calculate the average rating to the nearest tenth of a decimal point"""
        r1 = Recipe.objects.get(title="pb&j")
        self.assertEqual(r1.avg_rating(), 3.5)

    def test_home_page(self):
        """Test response of Home page"""
        c = Client()
        response = c.get("all_recipes")
        self.assertEqual(response.status_code, 200)

    def test_recipe_page(self):
        """Test response of individual recipe page"""
        r1 = Recipe.objects.get(title="pb&j")

        c = Client()
        response = c.get(f"/{r1.title}")
        self.assertEqual(response.status_code, 200)

    def test_invalid_recipe_page(self):
        """Test response of invalid recipe page"""
        c = Client()
        response = c.get("/turkey&cheese")
        self.assertEqual(response.status_code, 404)

    def test_new_recipe_page(self):
        """Test response of new recipe page"""
        c = Client()
        response = c.get("new_recipe")
        self.assertEqual(response.status_code, 200)

    def test_my_recipes_page(self):
        """Test response of my recipes page"""
        c = Client()
        response = c.get("my_recipes")
        self.assertEqual(response.status_code, 200)

    def test_cuisines_page(self):
        """Test response of cuisines page"""
        c = Client()
        response = c.get("cuisines")
        self.assertEqual(response.status_code, 200)

    def test_cuisine_recipes_page(self):
        """Test response of cuisine recipes page"""
        r1 = Recipe.objects.get(title="pb&j")
        c = Client()
        response = c.get(f"cuisines/{r1.category}")
        self.assertEqual(response.status_code, 200)

    def test_favorites_page(self):
        """Test adding a recipe to a user's favorites and favorites page"""
        r1 = Recipe.objects.get(title="pb&j")
        u1 = User.objects.get(username="lukek")
        u1.favorites.add(r1)

        self.assertEqual(len(u1.favorites), 1)

        c = Client()
        response = c.get("favorites")
        self.assertEqual(response.status_code, 200)
