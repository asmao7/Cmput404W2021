from .models import Author, Post, TextPost, ImagePost


def AuthorToJSON(author):
    # Converts an Author object into JSON. Returns None if the author is bad
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


# TODO: Fill out categories, count, size, comments
def PostToJSON(post, is_image=False):
    # Converts a Post object into JSON. Return None if the Post is bad
    if not post:
        return None
    try:
        if is_image:
            content = post.content.url()
        else:
            content = post.content
        json = {
            "type":"post",
            "title":post.title,
            "id":post.url,
            "source":post.source,
            "origin":post.origin,
            "description":post.description,
            "contentType":post.content_type,
            "content":content,
            "author":AuthorToJSON(post.author),
            "categories":"",
            "count":0,
            "size":0,
            "comments":"",
            "published":post.published,
            "visibility":post.visibility,
            "unlisted":post.unlisted
        }
        return json
    except:
        return None