# Generated by Django 3.2.15 on 2023-03-10 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cookbook', '0003_auto_20230220_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='favorites',
            field=models.ManyToManyField(blank=True, related_name='favoriters', to='cookbook.Recipe'),
        ),
    ]
