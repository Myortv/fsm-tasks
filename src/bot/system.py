from pyrogram import (
    Client,
    filters,
)
from pyrogram.types import Message


from text.system import system_messages, system_keyboard

from core.configs import settings

from bot import user_login

from bot.pages import (
    system as system_pages,
)

from utils.user_states import user_states


def main_keyboard_filter():
    """return keyboard filter to
    filter out main keyboard values"""
    return (
        ~ filters.regex(system_keyboard.user_info) &
        ~ filters.regex(system_keyboard.all_tasks) &
        ~ filters.regex(system_keyboard.new_task) &
        ~ filters.regex(system_keyboard.rules)
    )


def init(app: Client) -> None:

    @app.on_message(filters.command(['start']) & filters.private)
    async def start_command_handler(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: slash command
        INVOKE (optional): page with inline keyboard to set user
        info if user is setted, login page if not setted
        """
        if await user_login.show_login_if_needed(client, message):
            return
        await system_pages.page_welcome(client, message.from_user.id)

    async def unhandled_input(client: Client, message: Message) -> None:
        """Handle notfiltered random input without user state"""
        await message.reply(
            system_messages.unhandled_input,
        )

    @app.on_message(filters.text & filters.private & main_keyboard_filter())
    async def handle_general_input(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: any user input
        INVOKE: subscribed function
        Handle user input and try to invoke related subscribed func"""
        login_flag = await user_login.show_login_if_needed(
            client,
            message,
            user_states.get_state(message.from_user.id)
        )
        if user_states.any_state_setted(message.from_user.id):
            try:
                await user_states.handle_action(
                    message.from_user.id,
                    client,
                    message,
                )
            finally:
                user_states.clean_state(message.from_user.id)
        else:
            if login_flag:
                return
            await unhandled_input(
                client,
                message,
            )

    @app.on_message(filters.regex(system_keyboard.rules) & filters.private)
    async def main_keyboard_rules(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: main keyboard (bottom keypad/persistent keyboard)
        INVOKE: nothing
        send rules page
        """
        if await user_login.show_login_if_needed(client, message):
            return
        await message.reply(
            system_messages.rules.format(
                bot_name=settings.BOT_NAME,
                rules=system_keyboard.rules,
                user_info=system_keyboard.user_info,
                new_task=system_keyboard.new_task,
                all_tasks=system_keyboard.all_tasks,
            ),
        )
