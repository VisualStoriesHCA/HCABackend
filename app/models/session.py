from .structures import User

active_sessions = {}


def create_user_session(user_id: str, user_name: str):
    active_sessions[user_id] = User(user_id=user_id, username=user_name)


def get_user_session(user_id: str) -> User:
    return active_sessions.get(user_id)
