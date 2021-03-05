#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import uuid


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def seed_db():
    # Set up two test authors
    author_id_1 = uuid.uuid4()
    author_host_1 = settings.HOST_NAME
    author_display_name_1 = "Test Author 1"
    author_username_1 = "TestAuthor1"
    author_github_1 = "github.com/testauthor1"
    author_1 = Author(id=author_id_1, host=author_host_1,
                        display_name=author_display_name_1,
                        github=author_github_1, username=author_username_1)
    author_1.save()

    author_id_2 = uuid.uuid4()
    author_host_2 = settings.HOST_NAME
    author_display_name_2 = "Test Author 2"
    author_username_2 = "TestAuthor2"
    author_github_2 = "github.com/testauthor2"
    author_2 = Author(id=author_id_2, host=author_host_2,
                        display_name=author_display_name_2,
                        github=author_github_2, username=author_username_2)
    author_2.save()

    # Set up some test post categories
    category_name_1 = "Test Category One"
    category_name_2 = "Test Category Two"
    category_name_3 = "Test Category Three"
    PostCategory(name=category_name_1).save()
    PostCategory(name=category_name_2).save()
    PostCategory(name=category_name_3).save()

    # Set up a test post
    post_id = uuid.uuid4()
    post_title = "Test Post"
    post_source = "SomeTestWebsite.com/posts/"
    post_origin = "SomeOtherTestWebsite.com/posts/"
    post_description = "A small test post."
    post_content_type = "text/plain"
    post_text_content = "This is a test post. It doesn't have much to it."
    post = Post(id=post_id, title=post_title, source=post_source,
                origin=post_origin, description=post_description,
                content_type=post_content_type, text_content=post_text_content,
                author=Author.objects.get(pk=author_id_1))
    post.categories.add(PostCategory.objects.get(pk=1),
                        PostCategory.objects.get(pk=2),
                        PostCategory.objects.get(pk=3))
    post.save()


if __name__ == '__main__':
    main()
