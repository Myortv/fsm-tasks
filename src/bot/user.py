from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    Message,
)


from repository import (
    user as user_repository
)

from bot import user_login

from fsm.user import user_fsmlike_wrapper, UserReplyData
from schemas.user import UserUpdate, UserPrototypeState

from utils.user_states import user_response_wrapper, user_states

from text.user import (
    # user_keyboard,
    user_messages,
)
from text.system import system_keyboard


def init(app: Client) -> None:
    @app.on_message(filters.regex(system_keyboard.user_info) & filters.private)
    async def main_keyboard_user(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: main keyboard (bottom keypad/persistent keyboard)
        INVOKE: callback_change_username/callback_change_login
        send page with user info and inline buttons for update
        """
        if await user_login.show_login_if_needed(client, message):
            return
        user = await user_repository.get_user(message.from_user.id)
        text, reply_markup = await user_fsmlike_wrapper.handle_general(
            UserPrototypeState.created.name,
            user,
        )
        await message.reply(text, reply_markup=reply_markup)

    @app.on_callback_query(filters.regex(UserReplyData.created_change_username))
    async def callback_change_username(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: main_keyboard_user
        INVOKE: await_for_username_input
        callback on inline button of user page.
        """
        user_states.set_state(callback_query.from_user.id, 'created_await_for_username')
        await client.send_message(
            callback_query.from_user.id,
            user_messages.input_prompt_username
        )
        await callback_query.answer()

    @user_response_wrapper.subscribe("created_await_for_username")
    async def await_for_username_input(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: callback_change_username
        INVOKE: create/update user page if needed
        Catch user input of username and update it
        """
        user = await user_repository.get_user(message.from_user.id)
        assert user is not None, "User should be created already"
        user.username = message.text
        user = await user_repository.update(
            user.telegram_id,
            UserUpdate(**user.model_dump())
        )
        await message.reply(
            user_messages.username_updated.format(**user.model_dump())
        )

    @app.on_callback_query(filters.regex(UserReplyData.created_change_login))
    async def callback_change_login(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: main_keyboard_user
        INVOKE: await_for_username_input
        callback on inline button of user page.
        """
        user_states.set_state(callback_query.from_user.id, 'created_await_for_login')
        await client.send_message(
            callback_query.from_user.id,
            user_messages.input_prompt_login
        )
        await callback_query.answer()

    @user_response_wrapper.subscribe("created_await_for_login")
    async def await_for_login_input(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: callback_change_login
        INVOKE: create/update user page if needed
        Catch user input of login and update it
        """
        user = await user_repository.get_user(message.from_user.id)
        assert user is not None, "User should be created already"
        user.login = message.text
        user = await user_repository.update(
            user.telegram_id,
            UserUpdate(**user.model_dump())
        )
        await message.reply(
            user_messages.login_updated.format(**user.model_dump())
        )
