from pyrogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton, )
from pyrogram import Client


from text.system import system_keyboard, system_messages
from core.configs import settings


async def page_welcome(
    client: Client,
    chat_id: int
):
    """Send default welcome page with main (bottom) keypad"""
    await client.send_message(
        chat_id,
        system_messages.start_command_message.format(
            bot_name=settings.BOT_NAME,
            rules=system_keyboard.rules,
            user_info=system_keyboard.user_info,
            new_task=system_keyboard.new_task,
            all_tasks=system_keyboard.all_tasks,
        ),
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton(system_keyboard.new_task)],
                [KeyboardButton(system_keyboard.all_tasks)],
                [KeyboardButton(system_keyboard.user_info)],
                [KeyboardButton(system_keyboard.rules)],
            ]
        )
    )
