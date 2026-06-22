# Data models representing users and posts in the system

class User:
    """
    Represents a registered User in our system.
    Handles data structure mapping for user rows.
    """
    def __init__(self, user_id: int, username: str, password_hash: str):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash

    def to_dict(self) -> dict:
        """
        Converts the User object data into a clean dictionary representation.
        Useful for JSON serialization in web routes.
        """
        return {
            "id": self.user_id,
            "username": self.username
        }


class Post:
    """
    Represents a blog post created by a registered user.
    """
    def __init__(self, post_id: int, user_id: int, title: str, content: str):
        self.post_id = post_id
        self.user_id = user_id
        self.title = title
        self.content = content

    def to_dict(self) -> dict:
        """
        Converts the Post object data into a clean dictionary representation.
        """
        return {
            "id": self.post_id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content
        }
