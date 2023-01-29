import httpx
from httpx import Response, Headers

from config import PROTOCOL, DOMAIN


async def send_token_refresh_request(refresh_token: str) -> Response:
    async with httpx.AsyncClient() as client:
        headers = Headers({
            'accept': 'application/json',
            'authorization': f'Bearer {refresh_token}'
        })
        return await client.post(
            url=f"{PROTOCOL}://{DOMAIN}/refresh", 
            headers=headers
        )


async def send_code_to_get_tokens(code: str, user_id: int) -> Response:
    async with httpx.AsyncClient() as client:
        headers = Headers({
            'accept': 'application/json',
            'Content-Type': 'application/json',
        })
        return await client.post(
            url=f"{PROTOCOL}://{DOMAIN}/telegram/bot/consider_application", 
            params={"code": code, "tg_user_id": user_id},
            headers=headers
        )    


async def send_request_to_get_timetables(access_token: str) -> Response:
    async with httpx.AsyncClient() as client:
        headers = Headers({
            'accept': 'application/json',
            'authorization': f'Bearer {access_token}'
        })
        return await client.get(
            url=f"{PROTOCOL}://{DOMAIN}/timetable/get_user_timetables/lite", 
            headers=headers
        )
