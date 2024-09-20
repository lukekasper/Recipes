# Generated by Django 3.2.15 on 2023-03-14 20:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_user_favorites'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=250, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipe_comments', to='app.recipe')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]