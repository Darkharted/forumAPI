# Generated by Django 3.2.7 on 2021-12-29 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='available',
            field=models.BooleanField(default=False),
        ),
    ]