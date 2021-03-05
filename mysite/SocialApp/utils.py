from .models import Author, Followers

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


def FollowerFinalJSON(follower_list):
    """
    Converts Followe object into a JSON-compatible dictionary.
    Returns None on failure.
    """
    if not follower_list:
        return None
    try:
        json = {
            "type":"followers",
            "items": follower_list
        }
        return json
    except:
        return None
