AUTH_URL = "https://rksok\-protocol\.ru/login/telegram/bot/{tg_user_id}"  # type: ignore


NO_AUTH_MESSAGE = """Чтобы пользоваться ботом, сначала необходимо войти \
[тут]({auth_url}) в свой аккаунт\!""".format(  # type: ignore
    auth_url=AUTH_URL
)

FAILED_TO_UPDATE_TOKENS_MESSAGE = """Произошла ошибка\. Можете, пожалуйста, \
еще раз войти в свой аккаунт\. Вот [ссылка]({auth_url})""".format(  # type: ignore
    auth_url=AUTH_URL
)

LOGIN_MESSAGE = """Чтобы войти в свой аккаунт, перейдите \
[сюда]({auth_url})""".format(auth_url=AUTH_URL)

CONNECTION_FAILED_MESSAGE = """В данный момент сайт не доступен\. Повторите \
попытку позже\."""  # type: ignore

EMPTY_MESSAGE = """Пока у вас ничего нет\."""  #type: ignore

SERVER_ERROR_MESSAGE = """Сервер пока не отвечает\. Попробуйте позже"""  # type: ignore

CHOOSE_TIMETABLE_MESSAGE = """Ниже представлены ваши расписания.
Выберите расписание, о котором хотите получать информацию."""

MESSAGE_AFTER_SELECTING_TIMETABLE = """Вы выбрали расписание {name}.

Ниже представлены команды, которыми теперь можно пользоваться:

"Тут должны быть команды, но их пока нет"
"""