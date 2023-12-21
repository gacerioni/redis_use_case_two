# in services/user_service.py
import logging
import uuid
from models.user import User


class UserService:
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    def save_user(self, user: User):
        if not user.user_id:
            user.user_id = str(uuid.uuid4())

        user_key = f"user:{user.user_id}"
        user_data = {
            'username': user.username,
            'email': user.email,
            'country': user.country
        }

        self.redis_conn.hset(user_key, mapping=user_data)

    def load_user(self, user_id):
        user_key = f"user:{user_id}"
        user_data = self.redis_conn.hgetall(user_key)
        if user_data:
            return User(user_id, user_data[b'username'].decode(), user_data[b'email'].decode())
        return None

    def get_all_users(self):
        user_keys = self.redis_conn.keys('user:*')
        users = []
        for key in user_keys:
            user_data = self.redis_conn.hgetall(key)
            user_id = key.decode().split(':')[1]
            users.append(User(
                user_id,
                user_data[b'username'].decode(),
                user_data[b'email'].decode(),
                user_data.get(b'country', b'').decode()
            ))
        return users