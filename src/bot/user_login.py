from typing import Optional, Dict

from pyrogram.types import (
    Message,
    CallbackQuery
)
from pyrogram import (
    Client,
    filters,
)


from schemas.user import (
    # UserInDB,
    # UserCreate,
    UserPrototype,
    UserPrototypeState,
)

from repository import (
    user as user_repository,
)

from bot.pages import (
    system as system_pages,
)

from text.user import (
    user_messages,
    # user_keyboard,
)

from utils.user_states import user_states, user_response_wrapper
from fsm.user import user_fsmlike_wrapper, UserReplyData


user_prototypes: Dict[int, UserPrototype] = dict()


def init(app: Client) -> None:
    @app.on_callback_query(filters.regex(UserReplyData.creating_change_username))
    async def callback_change_username(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: login_page/ field update callbacks
        INVOKE: await for user input ()
        callback on inline button of user page.
        """
        user_states.set_state(callback_query.from_user.id, 'creating_await_for_username')
        await client.send_message(
            callback_query.from_user.id,
            user_messages.input_prompt_username
        )
        await callback_query.answer()

    @user_response_wrapper.subscribe("creating_await_for_username")
    async def await_for_username_input(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: callback_change_username
        INVOKE: create/update user page if needed
        Catch user input of username and update it
        """
        user = user_prototypes.get(message.from_user.id)
        if not user:
            user = UserPrototype(
                state=UserPrototypeState.creating
            )
        user.username = message.text
        user_prototypes[message.from_user.id] = user
        text, reply_markup = await user_fsmlike_wrapper.handle_general(
            user.state.name,
            user,
        )
        await message.reply(text, reply_markup=reply_markup)

    @app.on_callback_query(filters.regex(UserReplyData.creating_change_login))
    async def callback_change_login(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: login_page/ field update callbacks
        INVOKE: await for user input ()
        callback on inline button of user page.
        """
        user_states.set_state(callback_query.from_user.id, 'creating_await_for_login')
        await client.send_message(
            callback_query.from_user.id,
            user_messages.input_prompt_login
        )
        await callback_query.answer()

    @user_response_wrapper.subscribe("creating_await_for_login")
    async def await_for_login_input(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: callback_change_login
        INVOKE: create/update user page if needed
        Catch user input of login and update it
        """
        user = user_prototypes.get(message.from_user.id)
        if not user:
            user = UserPrototype(
                state=UserPrototypeState.creating
            )
        user.login = message.text
        user_prototypes[message.from_user.id] = user
        text, reply_markup = await user_fsmlike_wrapper.handle_general(
            user.state.name,
            user,
        )
        await message.reply(text, reply_markup=reply_markup)

    @app.on_callback_query(filters.regex(UserReplyData.creating_create_user))
    async def callback_create_user(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: login_page/ field update callbacks
        INVOKE: await for user input ()
        callback on inline button of user page.
        """
        user = user_prototypes.get(callback_query.from_user.id)
        assert user is not None, "This option should be accessable only if\
            user exsists in wallet"
        user = await user_repository.insert_if_not_exsists(
            callback_query.from_user.id,
            user,
        )
        await callback_query.answer()
        await system_pages.page_welcome(client, callback_query.from_user.id)


async def login_page(
    client: Client,
    message: Message,
) -> None:
    """Show login page"""
    user = user_prototypes.get(message.from_user.id)
    if not user:
        user = UserPrototype(state=UserPrototypeState.not_exsists)
    text, reply_markup = await user_fsmlike_wrapper.handle_general(
        user.state.name,
        user,
    )
    await message.reply(
        text,
        reply_markup=reply_markup
    )


async def show_login_if_needed(
    client: Client,
    message: Message,
    state: Optional[str] = None,
) -> bool:
    """Check is user info is full, if not sending user info page"""
    if state and state.startswith('creating_'):
        return True
    # try to get data from database
    user = await user_repository.get_user(message.from_user.id)
    if user:
        return False
    await login_page(client, message)
    return True
