from pydantic import BaseModel, Field
from typing import List, Optional

class PostRequest(BaseModel):
    content: str

class User(BaseModel):
    name: str = None
    user_name: Optional[str] = None
    birth_date: Optional[str] = None
    verified_profile: Optional[int] = None
    site: Optional[str] = None
    is_banned: Optional[bool] = None
    biography: Optional[str] = None
    email_verified_at: Optional[str] = None
    total_posts: Optional[int] = None
    total_followers: Optional[int] = None
    total_following: Optional[int] = None
    total_comments: Optional[int] = None

class ChatRequest(BaseModel):
    content: str
    user: User

class Message(BaseModel):
    role: str
    content: str

class ChatRequestV2(BaseModel):
    user: User
    messages: Optional[List[Message]] = []
    
class ChatRequestImage(BaseModel):
    image_path: Optional[str] = None
    image_base64: Optional[str] = None