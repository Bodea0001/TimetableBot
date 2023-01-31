from enum import Enum
from datetime import datetime
from dataclasses import dataclass

from config import DATE_FORMAT


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

    def __post_init__(self):
        value = getattr(self, "creation_date").split(".")
        if value is None:
            return
        value = datetime.strptime(value[0], "%Y-%m-%dT%H:%M:%S").strftime(DATE_FORMAT)
        setattr(self, "creation_date", value)


class TaskTags(str, Enum):
    one = "один"
    all = "все"


class TaskStatuses(str, Enum):
    in_progress = "В процессе"
    complited = "Завершено"


@dataclass
class Task:
    id: int
    id_timetable: int
    tag: TaskTags
    deadline: str
    subject: str
    description: str
    status: TaskStatuses
    creation_date: str
    
    def __post_init__(self):
        """Set up deadline and creation_date to needed string format"""
        for field in ("deadline", "creation_date"):
            value = getattr(self, field).split(".")
            if value is None:
                continue
            value = datetime.strptime(value[0], "%Y-%m-%dT%H:%M:%S").strftime(DATE_FORMAT)
            setattr(self, field, value)