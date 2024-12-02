from typing import Dict

from pyrogram.types import (
    Message,
    CallbackQuery
)
from pyrogram import (
    Client,
    filters,
)


from schemas.tasks import (
    TaskUpdate,
    TaskPrototype,
    # TaskState,
    # TaskInDB,
)

from repository import (
    task as task_repository,
)

from bot import user_login

from text.system import system_keyboard
from text.task import (
    # task_keyboard,
    task_messages,
)

from utils.user_states import user_states, user_response_wrapper
from fsm.tasks import task_fsmlike_wrapper


task_prototypes: Dict[int, TaskPrototype] = dict()


LIMIT = 10


def init(app: Client) -> None:
    @app.on_message(filters.regex(system_keyboard.all_tasks) & filters.private)
    async def main_keyboard_all_tasks(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: main keyboard (bottom keypad/persistent keyboard)
        INVOKE: callback to select task
        send list of inline buttons to select task
        """
        if await user_login.show_login_if_needed(client, message):
            return
        max, all_tasks = await task_repository.get_page(
            message.from_user.id,
            0,
            LIMIT,
        )
        text, reply_keyboard = await task_fsmlike_wrapper.handle_list(
            all_tasks,
            0,
            LIMIT,
            max
        )
        await message.reply(text, reply_markup=reply_keyboard)

    @app.on_callback_query(filters.regex("task_list_callback:.*?"))
    async def callback_new_pagination_page(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: main_keyboard_all_tasks (navigation inline buttons)
        INVOKE: task general/itself
        callback on pagination (nav) buttons to send new page of tasks
        """
        _, offset, limit = callback_query.data.split(':')
        offset = int(offset)
        limit = int(limit)
        max, all_tasks = await task_repository.get_page(
            callback_query.from_user.id,
            offset,
            limit,
        )
        text, reply_keyboard = await task_fsmlike_wrapper.handle_list(
            all_tasks,
            offset,
            limit,
            max
        )
        await client.send_message(
            callback_query.from_user.id,
            text, reply_markup=reply_keyboard
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex("task_callback:.*?"))
    async def callback_select_task(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: main_keyboard_new_task/callback_new_pagintaion_page
        INVOKE: menu callbacks callback_menu_task_edit/callback_meun_task_move_state
        callback on inline button of tasks to show page of specific one
        """
        _, task_id = callback_query.data.split(':')
        task_id = int(task_id)
        task = await task_repository.get(task_id)
        text, reply_markup = await task_fsmlike_wrapper.handle_general(
            task.state.name,
            task,
        )
        await client.send_message(
            callback_query.from_user.id,
            text, reply_markup=reply_markup
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex("task_menu_edit_callback:.*?"))
    async def callback_menu_task_edit(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: callback_select_task
        INVOKE: callback_task_edit_field
        callback to show edit menu for task
        """
        _, task_id = callback_query.data.split(':')
        task_id = int(task_id)
        task = await task_repository.get(task_id)
        text, reply_markup = await task_fsmlike_wrapper.handle_edit(
            task.state.name,
            task,
        )
        await client.send_message(
            callback_query.from_user.id,
            text, reply_markup=reply_markup
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex("task_menu_move_state_callback:.*?"))
    async def callback_menu_task_move_state(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: callback_select_task
        INVOKE: callback_task_set_state
        callback to show move options of task
        """
        _, task_id = callback_query.data.split(':')
        task_id = int(task_id)
        task = await task_repository.get(task_id)
        text, reply_markup = await task_fsmlike_wrapper.handle_move_state(
            task.state.name,
            task,
        )
        await client.send_message(
            callback_query.from_user.id,
            text, reply_markup=reply_markup
        )
        await callback_query.answer()

    @app.on_callback_query(filters.regex("task_edit_callback:.*?"))
    async def callback_menu_task_edit_field(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: callback_menu_task_edit
        INVOKE: await_for_edit_input
        callback to select field to edit from edit menu
        """
        _, task_id, field = callback_query.data.split(':')
        user_states.set_state(
            callback_query.from_user.id,
            f"task_await_for_edit:{task_id}:{field}"
        )
        await client.send_message(
            callback_query.from_user.id,
            task_messages.get(f'prompt_input__{field}')
        )
        await callback_query.answer()

    @user_response_wrapper.subscribe("task_await_for_edit")
    async def await_for_edit_input(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: callback_menu_task_edit_field
        INVOKE: nothing
        awaits for user input to update task field
        """
        _, task_id, field = user_states.get_state(message.from_user.id).split(':')
        task_id = int(task_id)
        task = await task_repository.get(task_id)
        setattr(task, field, message.text)
        task = await task_repository.update(
            task.id,
            TaskUpdate(**task.model_dump())
        )
        text, reply_markup = await task_fsmlike_wrapper.handle_general(
            task.state.name,
            task,
        )
        await client.send_message(
            message.from_user.id,
            text, reply_markup=reply_markup
        )

    @app.on_callback_query(filters.regex("task_set_state_callback:.*?"))
    async def callback_task_set_state(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: callback_select_task
        INVOKE: nothing
        callback to select new status from move menu
        """
        _, task_id, state = callback_query.data.split(':')
        task_id = int(task_id)
        task = await task_repository.move_state(
            task_id, state
        )
        if not task:
            await client.send_message(
                callback_query.from_user.id,
                task_messages.cant_move_to_this_state
            )
            await callback_query.answer()
            return
        text, reply_markup = await task_fsmlike_wrapper.handle_general(
            task.state.name,
            task,
        )
        await client.send_message(
            callback_query.from_user.id,
            text, reply_markup=reply_markup
        )
        await callback_query.answer()
