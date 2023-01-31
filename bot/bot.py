import json
import redis
import logging
from telegram import (
    User,
    Chat,
    Update, 
    constants, 
    InlineKeyboardMarkup,
    InlineKeyboardButton, 
)
from telegram.ext import (
    ContextTypes, 
    CommandHandler, 
    ApplicationBuilder, 
    CallbackQueryHandler
)
from httpx import ConnectError

from exceptions import (
    UnknownUser, 
    NotOkResponse,
    EmptyResponse, 
    FailedTokenRefresh, 
)
from models import Timetable
from tokens import get_tokens
from request import (
    send_code_to_get_tokens,
    send_request_to_get_tasks,
    send_request_to_get_timetables, 
)
from messages import (
    EMPTY_MESSAGE,
    NO_AUTH_MESSAGE,
    SERVER_ERROR_MESSAGE,
    CHOOSE_TIMETABLE_MESSAGE,
    CONNECTION_FAILED_MESSAGE,
    NO_SAVED_TIMETABLE_MESSAGE,
    FAILED_TO_UPDATE_TOKENS_MESSAGE,
    MESSAGE_AFTER_SELECTING_TIMETABLE,
)
from config import TELEGRAM_BOT_TOKEN
from crud import save_tokens, get_timetable_name, get_timetable_id
from parsing import parse_response_text, parse_timetables, parse_tasks


r = redis.Redis()


logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(funcName)s: %(lineno)d - %(message)s',
    level=logging.INFO
)
    
logger = logging.getLogger()


def handler_decorator(func):
    async def new_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
        effective_chat = update.effective_chat
        if not effective_chat:
            logger.warning("effective_chat is None in /start")
            return

        user = update.effective_user
        if not user:
            logger.warning("effective_chat is None in /start")
            return  

        try:
            return await func(update, context)
        except ConnectError as e:
            logger.error(e)
            await context.bot.send_message(
                chat_id=effective_chat.id,
                text=CONNECTION_FAILED_MESSAGE,
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
        except UnknownUser:
            logger.info(f'User {user.id}: no authenticated')
            await context.bot.send_message(
                chat_id=effective_chat.id,
                text=NO_AUTH_MESSAGE.format(tg_user_id=user.id),
                parse_mode=constants.ParseMode.MARKDOWN_V2,
            )  
        except FailedTokenRefresh as e:
            logger.warning(f'User {user.id}: {e}')
            await context.bot.send_message(
                chat_id=effective_chat.id,
                text=FAILED_TO_UPDATE_TOKENS_MESSAGE.format(tg_user_id=user.id),
                parse_mode=constants.ParseMode.MARKDOWN_V2,
            )
        except EmptyResponse as e:
            logger.info(f'User {user.id}: {e}')
            await context.bot.send_message(
                chat_id=effective_chat.id,
                text=EMPTY_MESSAGE,
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )
        except NotOkResponse as e:
            logger.warning(f'User {user.id}: {e}')
            await context.bot.send_message(
                chat_id=effective_chat.id,
                text=SERVER_ERROR_MESSAGE,
                parse_mode=constants.ParseMode.MARKDOWN_V2
            )

    return new_func


@handler_decorator
async def choose_timetable(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user: User = update.effective_user  # type: ignore

    access_token, _ = await get_tokens(r, user)
    response = await send_request_to_get_timetables(access_token)

    timetables = parse_timetables(response.text)
    logger.info(f'User {user.id}: timetables transferred')
    await update.message.reply_text(
        text=CHOOSE_TIMETABLE_MESSAGE,
        reply_markup=_get_timetables_keyboard(timetables),
        parse_mode=constants.ParseMode.HTML
    )


async def timetable_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        logger.warning("effective_chat is None in /start")
        return 

    query = update.callback_query
    await query.answer()
    if not query.data:
        return

    timetable = json.loads(query.data)
    with r.pipeline() as pipe:
        pipe.multi()
        pipe.set(f'{user.id}:timetable:name', timetable['name'])
        pipe.set(f'{user.id}:timetable:id', timetable['id'])
        pipe.execute()
    logger.info(f'User {user.id}: choose timetable with id {timetable["id"]}')
    await query.edit_message_text(
        text=MESSAGE_AFTER_SELECTING_TIMETABLE.format(name=timetable['name']),
        parse_mode=constants.ParseMode.HTML
    )


def _get_timetables_keyboard(timetables: list[Timetable]) -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(
            timetable.name, 
            callback_data=json.dumps({
                'name': timetable.name, 
                "id": timetable.id,
            })
        )
    ] for timetable in timetables]
    return InlineKeyboardMarkup(keyboard)


@handler_decorator
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: User = update.effective_user   # type: ignore

    message_parts = update.message.text.split()
    if len(message_parts) == 2:
        code = message_parts[1]
        response = await send_code_to_get_tokens(code, user.id)
        access_token, refresh_token = parse_response_text(response.text)
        save_tokens(r, user.id, access_token, refresh_token)
    await choose_timetable(update, context)  


@handler_decorator
async def get_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat: Chat = update.effective_chat  # type: ignore
    user: User = update.effective_user  # type: ignore

    timetable_id = get_timetable_id(r, user.id)
    if not timetable_id:
        logger.info(f"User {user.id}: No timetable")
        await context.bot.send_message(
            chat_id=effective_chat.id,
            text=NO_SAVED_TIMETABLE_MESSAGE,
            parse_mode=constants.ParseMode.HTML
        )
        return
        
    access_token, _ = await get_tokens(r, user)
    response = await send_request_to_get_tasks(timetable_id, access_token)
    
    tasks = parse_tasks(response.text)
    text = ""
    for task in tasks:
        text += f"◦ {task.subject}: {task.description}.\n Нужно сделать до <i>{task.deadline}</i>.\n"
    logger.info(f'User {user.id}: tasks transferred')
    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=text,
        parse_mode=constants.ParseMode.HTML
    )


async def pass_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat: Chat = update.effective_chat  # type: ignore
    user: User = update.effective_user  # type: ignore

    timetable_name = get_timetable_name(r, user.id)
    if not timetable_name:
        logger.info(f"User {user.id}: No timetable")
        await context.bot.send_message(
            chat_id=effective_chat.id,
            text=NO_SAVED_TIMETABLE_MESSAGE,
            parse_mode=constants.ParseMode.HTML
        )
        return

    await context.bot.send_message(
        chat_id=effective_chat.id,
        text=f"Вы выбрали расписание {timetable_name}",
        parse_mode=constants.ParseMode.HTML
    )



if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    app.add_handler(start_handler)

    timetable_button_handler = CallbackQueryHandler(timetable_button)
    app.add_handler(timetable_button_handler)

    choose_timetable_handler = CommandHandler("choose", choose_timetable)
    app.add_handler(choose_timetable_handler)

    tasks_handler = CommandHandler("tasks", get_tasks)
    app.add_handler(tasks_handler)

    timetable_handler = CommandHandler("timetable", pass_timetable)
    app.add_handler(timetable_handler)

    app.run_polling()
