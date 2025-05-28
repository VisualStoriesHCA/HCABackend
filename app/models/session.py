from .structures import User

active_sessions = {}


def generate_user_id(user_name: str) -> str:
    return "id_" + user_name


def create_user_session(name: str, user_name: str, user_id: str) -> User:
    active_sessions[user_id] = User(name=name, user_name=user_name, user_id=user_id)
    return active_sessions[user_id]


def get_user_session(user_id: str) -> User:
    return active_sessions.get(user_id)


def delete_user_session(user_id: str) -> bool:
    if user_id in active_sessions:
        del active_sessions[user_id]
        return True
    return False
