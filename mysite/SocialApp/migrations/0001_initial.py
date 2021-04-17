# Generated by Django 3.1.6 on 2021-04-15 06:59

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author_url', models.CharField(blank=True, default='', max_length=200)),
                ('author_json', models.TextField(default='')),
                ('comment', models.TextField()),
                ('content_type', models.CharField(choices=[('text/plain', 'Plain Text'), ('text/markdown', 'Markdown')], default='text/plain', max_length=20)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('url', models.CharField(editable=False, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Followers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Followers',
                'verbose_name_plural': 'Followers',
            },
        ),
        migrations.CreateModel(
            name='ForeignServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('host_name', models.CharField(blank=True, max_length=100)),
                ('authors_url', models.CharField(blank=True, max_length=200)),
                ('authors_json_key', models.CharField(blank=True, max_length=25)),
                ('posts_url', models.CharField(blank=True, max_length=200)),
                ('posts_json_key', models.CharField(blank=True, max_length=25)),
                ('username', models.CharField(blank=True, max_length=100)),
                ('password', models.CharField(blank=True, max_length=25)),
            ],
            options={
                'verbose_name': 'Foreign Server',
                'verbose_name_plural': 'Foreign Servers',
            },
        ),
        migrations.CreateModel(
            name='InboxItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField(default='')),
                ('json_str', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='ObjectLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_url', models.CharField(max_length=200)),
                ('author_json', models.TextField(default='')),
                ('object_url', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Liked Object',
                'verbose_name_plural': 'Liked Objects',
            },
        ),
        migrations.CreateModel(
            name='PostCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Post Category',
                'verbose_name_plural': 'Post Categories',
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('host', models.CharField(default='localhost:8000', editable=False, max_length=100)),
                ('url', models.CharField(editable=False, max_length=200)),
                ('github', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('is_server', models.BooleanField(default=False)),
                ('followers', models.ManyToManyField(related_name='followed_by', through='SocialApp.Followers', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='RemoteFriends',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remote_friends', models.CharField(editable=False, max_length=200)),
                ('local_author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RemoteFollowers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remote_author_from', models.CharField(editable=False, max_length=200)),
                ('local_author_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='remote_followers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RemoteFollow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remote_author_to', models.CharField(editable=False, max_length=200)),
                ('local_author_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='remote_following', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('url', models.CharField(editable=False, max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('content_type', models.CharField(choices=[('text/plain', 'Plain Text'), ('text/markdown', 'Markdown'), ('application/base64', 'Base64 Encoding'), ('image/png;base64', 'PNG'), ('image/jpeg;base64', 'JPEG')], default='text/plain', max_length=20)),
                ('content', models.TextField(blank=True, default='')),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('visibility', models.CharField(choices=[('PUBLIC', 'Public'), ('FRIENDS', 'Friends')], default='PUBLIC', max_length=10)),
                ('unlisted', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('categories', models.ManyToManyField(blank=True, to='SocialApp.PostCategory')),
            ],
        ),
        migrations.AddConstraint(
            model_name='objectlike',
            constraint=models.UniqueConstraint(fields=('author_url', 'object_url'), name='unique_like'),
        ),
        migrations.AddField(
            model_name='inboxitem',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='followers',
            name='author_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='followers',
            name='author_to',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='followee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SocialApp.post'),
        ),
        migrations.AddConstraint(
            model_name='remotefollowers',
            constraint=models.UniqueConstraint(fields=('remote_author_from', 'local_author_to'), name='remote_followers'),
        ),
        migrations.AddConstraint(
            model_name='remotefollow',
            constraint=models.UniqueConstraint(fields=('local_author_from', 'remote_author_to'), name='remote_follow'),
        ),
        migrations.AddConstraint(
            model_name='followers',
            constraint=models.UniqueConstraint(fields=('author_from', 'author_to'), name='unique_follow'),
        ),
    ]
