FROM python:latest

# Set the environment variables with default values
ENV ADMIN_USER=default_admin \
    ADMIN_PASSWORD=default_password

RUN mkdir -p /home/Recipes
COPY . /home/Recipes
WORKDIR /home/Recipes

# install dependencies from requirements file
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]