# Cookbook Web App

Welcome to the Cookbook web app! This app allows you to store and manage your favorite recipes in a digital cookbook. You can search for recipes by ingredients or title, filter recipes by cuisine, add new recipes, modify and delete your own recipes, rate recipes, comment on recipes, and more. Below, you'll find an overview of the app's features, technical architecture, and deployment instructions.

## Features

1. **Search Recipes by Ingredients or Title:** You can search for recipes based on the ingredients you have at hand or by the title of the recipe, making it easier to find the perfect recipe for your available ingredients.

2. **Filter by Cuisine:** The app allows you to filter recipes based on cuisine, making it convenient to discover recipes from different parts of the world.

3. **User Authentication:** You must sign up and log in to use the full functionality of the app. This ensures that your posted recipes, favorites, and comments are associated with your account.

4. **Recipe Management:**
   - **Add New Recipes:** You can add your own recipes to the cookbook, complete with ingredients, instructions, and other details.
   - **Modify and Delete Recipes:** You have full control over the recipes you created. You can edit or delete them as needed.

5. **Favorite Recipes:** You can mark recipes as your favorites for quick access in the future.

6. **Star Rating System:** Users can rate recipes using a star rating system, providing valuable feedback to recipe creators and helping others find highly-rated recipes.

7. **Comments:** Users can leave comments on their own and other people's recipes, creating a lively community and fostering recipe discussions.

## Technical Architecture

The Cookbook web app is built using the following technologies:

### Front End:
- **JavaScript:** The front-end is dynamically displayed using JavaScript, which enhances user interactivity and provides a smooth experience.
- **React Framework:** The app is built on the React framework, enabling efficient component-based development.

### HTML/CSS:
- **Bootstrap/Flexbox:** Bootstrap and Flexbox are used for responsive design and to ensure the app looks great on various devices.

### Back End:
- **Python/Django Framework:** The back end is powered by Python using the Django web framework, providing a robust and scalable foundation for the app.
- **MySQL Database:** The app uses a MySQL database to store user accounts, recipes, comments, and other essential data.

### Django Model Objects:
- **User Model:** The User model builds on Django's base abstract user class and adds the ability to have favorite recipes.
  - **Fields:**
    - `username`: The unique username of the user.
    - `email`: The user's email address.
    - `password`: The hashed password for authentication.
    - `favorites`: A many-to-many relationship field storing the favorite recipes of the user.

- **Recipe Model:** The Recipe model represents a single recipe in the cookbook.
  - **Fields:**
    - `user`: The author of the recipe, linked to the User model.
    - `title`: The title of the recipe.
    - `ingredients`: A field to store the list of ingredients for the recipe.
    - `instructions`: The cooking instructions for the recipe.
    - `category`: The cuisine or category to which the recipe belongs.
    - `cooktime`: The time required to cook the recipe.
    - `image` (optional): An image representing the finished dish, if provided by the user.
    - `notes` (optional): Additional notes or tips for the recipe, if provided by the user.
    - `timestamp`: A timestamp associated with the creation of the recipe.
    - `user_rating`: A dictionary object that stores the user's ratings and their corresponding ratings for the recipe.

- **Comment Model:** The Comment model represents a comment left by a user on a recipe.
  - **Fields:**
    - `text`: The comment text.
    - `author`: The user who wrote the comment, linked to the User model.
    - `recipe`: The recipe to which the comment is associated.
    - `timestamp`: A timestamp associated with the creation of the comment.

### Testing & CI/CD:
- **Unit Testing:** Both back-end and front-end code undergo unit testing to ensure reliability and maintainability.
- **Back-End Testing:** Tests are conducted to validate models and methods.
- **Front-End Testing:** Selenium is used to perform front-end testing.
- **Continuous Integration and Continuous Deployment (CI/CD):** A CI/CD pipeline can be set up to automate the testing, building, and deployment processes.

### Caching:
- Back-end caching is implemented using the Django framework to optimize response times and reduce database queries.
- **Memcached:** Memcached is utilized on the local host to improve caching efficiency.
- **@cache_page Decorator:** The @cache_page decorator is used for per-view caching.
- **Low-level API Caching:** Expensive queries are cached using low-level API caching, making the app more responsive.
- **@receiver(post_save) and post_delete Decorators:** These decorators are used to handle updates to the database efficiently.

### Security:
- **CSRF Tokens:** CSRF tokens are sent from the front end during API calls to prevent cross-site request forgery attacks.
- **Error Handling:** Both front-end and back-end code implement try/except statements to handle improper request methods or JSON data gracefully.
- **Environmental Variables:** Sensitive information, such as API keys, is loaded through a secret .env file kept offline from the repository for enhanced security.

### Deployment:
- **Docker:** The app is deployed using Docker containers, ensuring consistent and scalable deployments. A custom Docker image is used to build the application container, while an off-the-shelf Docker image is used for the MySQL database.
- **Docker Compose:** Docker Compose is used to build and run containers and create a network for database and app communication.
- **Requirements.txt:** The requirements.txt file is used to supply dependencies for the database and app.
- **Local Volumes:** Volumes are persisted on the local machine for data persistence.
- **Startup Script:** A startup script is provided to install Docker and Docker Compose on the host machine and run the docker-compose.yaml file.
- **Platform Compatibility:** The app is designed to work specifically for macOS but can be adapted for other platforms if needed.

### Documentation/Formatting:
- **Docstrings/Comments:** Python back-end code includes docstrings and comments to improve code readability and maintainability.

## Getting Started

To run the Cookbook web app locally, follow these steps:

1. Clone the repository to your local machine.
2. Ensure you have Docker and Docker Compose installed.
3. Create a .env file with the necessary environmental variables.
4. Run the startup script to build and run the app containers.

Please refer to the detailed documentation provided within the codebase for more specific instructions on setting up and running the app.

Thank you for choosing the Cookbook web app! We hope you enjoy managing and sharing your favorite recipes with ease. If you encounter any issues or have suggestions for improvement, feel free to open an issue on this repository. Happy cooking! 🍳🧁🥗
