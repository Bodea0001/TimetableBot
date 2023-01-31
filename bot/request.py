import httpx
from httpx import Response, Headers

from config import PROTOCOL, DOMAIN
from exceptions import EmptyResponse, NotOkResponse


def _validate_response(response: Response, message: str) -> Response:
    if not response.text or str(response) == str(Response(404)):
        raise EmptyResponse(message)
    if str(response) not in (str(Response(200)), str(Response(201))):
        raise NotOkResponse(response)
    return response


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
        response = await client.post(
            url=f"{PROTOCOL}://{DOMAIN}/telegram/bot/consider_application", 
            params={"code": code, "tg_user_id": user_id},
            headers=headers
        )
        empty_response_message = "Failed to get tokens"
        return _validate_response(response, empty_response_message)    


async def send_request_to_get_timetables(access_token: str) -> Response:
    async with httpx.AsyncClient() as client:
        headers = Headers({
            'accept': 'application/json',
            'authorization': f'Bearer {access_token}'
        })
        response = await client.get(
            url=f"{PROTOCOL}://{DOMAIN}/timetable/get_user_timetables/lite", 
            headers=headers
        )
        empty_response_message = "No timetables"
        return _validate_response(response, empty_response_message)


async def send_request_to_get_tasks(
    timetable_id: int, 
    access_token: str
) -> Response:
    async with httpx.AsyncClient() as client:
        headers = Headers({
            'accept': 'application/json',
            'authorization': f'Bearer {access_token}'
        })
        response = await client.get(
            url=f"{PROTOCOL}://{DOMAIN}/task/get_in_timetable/for_user",
            headers=headers,
            params={'timetable_id': timetable_id}
        )
        empty_response_message = "No tasks"
        return _validate_response(response, empty_response_message)