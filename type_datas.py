from pydantic import BaseModel, Field

class PostRequest(BaseModel):
    content: str

class User(BaseModel):
    name: str = None
    user_name: str = None
    birth_date: str = None
    verified_profile: int = None
    site: str = None
    is_banned: bool = None
    biography: str = None
    email_verified_at: str = None
    total_posts: int = None
    total_followers: int = None
    total_following: int = None
    total_comments: int = None

class ChatRequest(BaseModel):
    content: str
    user: User
    
class ChatRequestImage(BaseModel):
    image_path: str