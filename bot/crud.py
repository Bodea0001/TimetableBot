import redis

from models import AccessToken, RefreshToken, TokenType


def get_access_token(r: redis.Redis, user_id: int) -> str | None:
    access_token = r.get(f"{user_id}:access_token")
    if access_token:
        return access_token.decode('utf-8')


def get_refresh_token(r: redis.Redis, user_id: int) -> str | None:
    refresh_token = r.get(f"{user_id}:refresh_token")
    if refresh_token:
        return refresh_token.decode('utf-8')


def save_tokens(
    r: redis.Redis,
    user_id: int,
    access_token: AccessToken,
    refresh_token: RefreshToken
):
    with r.pipeline() as pipe:
        pipe.multi()
        pipe.set(
            f'{user_id}:{TokenType.access.value}_token', 
            access_token.token, 
            access_token.expire
        )
        pipe.set(
            f'{user_id}:{TokenType.refresh.value}_token', 
            refresh_token.token, 
            refresh_token.expire
        )
        pipe.execute()
