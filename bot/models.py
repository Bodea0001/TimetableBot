from enum import Enum
from dataclasses import dataclass


class TokenType(str, Enum):
    access = 'access'
    refresh = 'refresh'


@dataclass
class Token:
    token: str
    expire: int


class AccessToken(Token):
    """Use to save the access token in your redis server"""
    pass


class RefreshToken(Token):
    """Use to save the refresh token in your redis server"""
    pass


class Education_level(str, Enum):
    undergraduate = "Бакалавриат"
    magistracy = "Магистратура"
    specialty = "Специалитет"


@dataclass
class Timetable:
    id: int
    name: str
    university: str
    specialization_name: str
    specialization_code: str
    education_level: Education_level
    course: int
    creation_date: str