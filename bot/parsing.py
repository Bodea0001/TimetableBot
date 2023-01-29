import json
from datetime import datetime

from models import Timetable
from exceptions import UnknownTokenType
from models import Token, TokenType, AccessToken, RefreshToken


def parse_response_text(text: str) -> tuple[AccessToken, RefreshToken]:
    data: dict = json.loads(text)
    access_token = _parse_access_token(data)
    refresh_token = _parse_refresh_token(data)
    return (access_token, refresh_token)


def _parse_token(data: dict, type: TokenType) -> Token:
    if type not in TokenType._value2member_map_.keys():
        raise UnknownTokenType
    passed_token: str = data[f"{str(type.value)}_token"]
    passed_token_expire: int = data[f"{str(type.value)}_token_expires"]
    token_expire = int(
        passed_token_expire - datetime.utcnow().timestamp() - 60
    )
    return Token(passed_token, token_expire)


def _parse_access_token(data: dict) -> AccessToken:
    token = _parse_token(data, TokenType.access)
    return AccessToken(token.token, token.expire)


def _parse_refresh_token(data: dict) -> RefreshToken:
    token = _parse_token(data, TokenType.refresh)
    return RefreshToken(token.token, token.expire)


def parse_timetables(timetables: str) -> list[Timetable]:
    timetables_list: list[dict] = json.loads(timetables)
    return [_parse_timetable(timetable) for timetable in timetables_list]
    

def _parse_timetable(timetable: dict) -> Timetable:
    return Timetable(
        id=timetable['id'],
        name=timetable['name'],
        university=timetable['university'],
        specialization_name=timetable['specialization_name'],
        specialization_code=timetable['specialization_code'],
        education_level=timetable['education_level'],
        course=timetable['course'],
        creation_date=timetable['creation_date']
    )


