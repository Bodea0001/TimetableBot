import redis
from telegram import User
from httpx import Response

from parsing import parse_response_text
from request import send_token_refresh_request
from exceptions import FailedTokenRefresh, UnknownUser
from crud import get_access_token, get_refresh_token, save_tokens


async def get_tokens(
    r: redis.Redis,
    user: User,
) -> tuple[str, str]:
    access_token = get_access_token(r, user.id)
    refresh_token = get_refresh_token(r, user.id)
    if not refresh_token:
        raise UnknownUser
    if access_token:
        return (access_token, refresh_token)
    await _update_tokens(r, refresh_token, user)
    access_token = get_access_token(r, user.id)
    refresh_token = get_refresh_token(r, user.id)
    if access_token is None or refresh_token is None:   
        raise FailedTokenRefresh("Failed to save tokens")   
    return (access_token, refresh_token)


async def _update_tokens(
    r: redis.Redis,
    refresh_token: str,
    user: User,
):
    response = await send_token_refresh_request(refresh_token)
    if not response or (str(response) not in (str(Response(200)), str(Response(201)))):
        raise FailedTokenRefresh("Failed to refresh tokens")
    new_access_token, new_refresh_token = parse_response_text(response.text)
    save_tokens(r, user.id, new_access_token, new_refresh_token)
