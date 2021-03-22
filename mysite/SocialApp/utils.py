"""
Contains useful helper functions
"""
from .models import Author, Post, Comment, PostCategory

def AuthorToJSON(author):
    """
    Converts an Author object into a JSON-compatible dictionary.
    Returns None on failure.
    """
    if not author:
        return None
    try:
        json = {
            "type":"author",
            "id":author.url,
            "host":author.host,
            "displayName":author.display_name,
            "url":author.url,
            "github":author.github
        }
        return json
    except:
        return None


# TODO: Fill out size
def PostToJSON(post):
    """
    Converts a Post object into a JSON-compatible dictionary.
    Return None on failure.
    """
    if not post:
        return None

    try:
        json = {
            "type":"post",
            "title":post.title,
            "id":post.url,
            "source":post.source,
            "origin":post.origin,
            "description":post.description,
            "contentType":post.content_type,
            "content":post.content,
            "author":AuthorToJSON(post.author),
            "categories":PostCategoryListToStringList(post.categories),
            "count":Comment.objects.filter(post=post).count(),
            "size":0,
            "comments":CommentListToJSON(Comment.objects.filter(post=post)),
            "published":str(post.published),
            "visibility":post.visibility,
            "unlisted":post.unlisted
        }
        return json
    except:
        return None


def PostListToJSON(posts):
    """
    Converts a list of Post objects into a JSON-compatible list
    of Posts. Returns an empty list on Failure.
    """
    if not posts:
        return []
    try:
        post_list = []
        for post in posts:
            test_json = PostToJSON(post)
            if test_json:
                post_list.append(test_json)
        return post_list
    except:
        return []


def CommentToJSON(comment):
    """
    Converts a Comment object into a JSON-compatible dictionary.
    Return None on failure.
    """
    if not comment:
        return None
    try:
        json = {
            "type":"comment",
            "author":AuthorToJSON(comment.author),
            "comment":comment.comment,
            "contentType":comment.content_type,
            "published":comment.published,
            "id":comment.url
        }
        return json
    except:
        return None


def CommentListToJSON(comments):
    """
    Converts a list of Comment objects into a JSON-compatible list
    of Comments. Returns an empty list on failure.
    """
    if not comments:
        return []
    try:
        comment_list = []
        for comment in comments:
            test_json = CommentToJSON(comment)
            if test_json:
                comment_list.append(test_json)
        return comment_list
    except:
        return []


def PostCategoryListToStringList(categories):
    """
    Converts a collection of Category objects into a JSON-compatible
    list of strings. Return empty list on failure.
    """
    if not categories:
        return []
    try:
        category_list = []
        for category in categories:
            category_list.append(category.name)
        return category_list
    except:
        return []


def StringListToPostCategoryList(category_list):
    """
    Converts a list of strings into ORM categories. Will add
    new categories to the database if they do not exist.
    Return empty list on failure.
    """
    if not category_list:
        return [];
    try:
        categories = []
        for category in category_list:
            try:
                test_cat = PostCategory.objects.get(name=category)
                categories.append(test_cat)
            except:
                test_cat = PostCategory.objects.create(name=category)
                categories.append(test_cat)
        return categories
    except:
        return []