from typing import Any, Tuple

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from fsm.base import FSM
from schemas.user import UserPrototype, UserPrototypeState, UserInDB
# from text.task import task_keyboard, task_messages
from text.user import user_keyboard, user_messages


class UserReplyData:
    """Simple class to store callback queries data"""
    creating_change_username: str = "creating_user_change_username"
    creating_change_login: str = "creating_user_change_login"
    creating_create_user: str = "creating_user_create_user"

    created_change_username: str = "created_user_change_username"
    created_change_login: str = "created_user_change_login"


class UserFSM(FSM):
    """FSM to manage user representations"""
    default_move_rules = {
        UserPrototypeState.not_exsists.name: [
            UserPrototypeState.creating.name
        ],
        UserPrototypeState.creating.name: [
            UserPrototypeState.created.name
        ],
        UserPrototypeState.created.name: [],
    }

    async def handle_general(
        self,
        state: str,
        user: UserPrototype | UserInDB,
        *args,
        **kwargs,
    ) -> None:
        """general api func to handle general representation"""
        return await self.handle_representation(
            "general",
            state,
            *args,
            user=user,
            **kwargs,
        )

    async def not_exsists_general(
        self,
        state: str,
        user: UserPrototype,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """handler for general representation in not_exists state"""
        return (
            user_messages.not_exsists__user_create,
            InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        user_keyboard.inline_username,
                        UserReplyData.creating_change_username,
                    )],
                    [InlineKeyboardButton(
                        user_keyboard.inline_login,
                        UserReplyData.creating_change_login,
                    )],
                ]
            )
        )

    async def creating_general(
        self,
        state: str,
        user: UserPrototype,
        *args,
        **kwargs,
    ) -> None:
        """handler for general representation in creating state"""
        keyboard = list()
        if not user.username:
            keyboard.append(
                [InlineKeyboardButton(
                    user_keyboard.inline_username,
                    UserReplyData.creating_change_username,
                )]
            )
        if not user.login:
            keyboard.append(
                [InlineKeyboardButton(
                    user_keyboard.inline_login,
                    UserReplyData.creating_change_login,
                )],
            )
        if user.username and user.login:
            keyboard.append(
                [InlineKeyboardButton(
                    user_keyboard.inline_create_user,
                    UserReplyData.creating_create_user,
                )],
            )
        return (
            user_messages.not_exsists__user_create.format(**user.model_dump()),
            InlineKeyboardMarkup(keyboard)
        )

    async def created_general(
        self,
        state: str,
        user: UserInDB,
        *args,
        **kwargs,
    ) -> None:
        """handler for general representation in created state"""
        return (
            user_messages.created__user_update.format(**user.model_dump()),
            InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        user_keyboard.inline_username,
                        UserReplyData.created_change_username,
                    )],
                    [InlineKeyboardButton(
                        user_keyboard.inline_login,
                        UserReplyData.created_change_login,
                    )],
                ]
            )
        )


user_fsmlike_wrapper = UserFSM()
