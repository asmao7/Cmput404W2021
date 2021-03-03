from .models import Author, Post


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
def PostToJSON(post):
    # Converts a Post object into JSON. Return None if the Post is bad
    if not post:
        return None
    try:
        # Maybe don't do this? Not sure yet.
        if post.image_content:
            content = post.image_content.url
        else:
            content = post.text_content
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


def CommentToJSON(comment):
    # Converts a Comment object into JSON. Return None if the Comment is bad
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