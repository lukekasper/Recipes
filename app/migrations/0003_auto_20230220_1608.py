# Generated by Django 3.2.15 on 2023-02-20 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_recipe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='rating',
        ),
        migrations.AddField(
            model_name='recipe',
            name='user_rating',
            field=models.CharField(blank=True, max_length=50000, null=True),
        ),
    ]
