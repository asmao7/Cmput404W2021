# Generated by Django 3.1.7 on 2021-03-03 20:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SocialApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='followers',
            old_name='followers',
            new_name='follower',
        ),
    ]
