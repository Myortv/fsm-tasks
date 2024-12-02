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
    # TaskInDB,
    # TaskUpdate,
    TaskCreate,
    TaskPrototype,
    TaskState,
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


def init(app: Client) -> None:
    @app.on_message(filters.regex(system_keyboard.new_task) & filters.private)
    async def main_keyboard_new_task(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: main keyboard (bottom keypad/persistent keyboard)
        INVOKE: callback_change_title/callback_change_description
        send page with fields to input
        """
        if await user_login.show_login_if_needed(client, message):
            return
        new_task = task_prototypes.get(message.from_user.id)
        if not new_task:
            new_task = TaskPrototype(state=TaskState.not_exsists)
        text, reply_keyboard = await task_fsmlike_wrapper.handle_edit(
            new_task.state.name,
            new_task,
        )
        await message.reply(text, reply_markup=reply_keyboard)

    @app.on_callback_query(filters.regex("new_task_callback_title"))
    async def callback_change_title(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: main_keyboard_new_task
        INVOKE: await_for_title_input (new_task_await_for_title)
        callback on "title" input field
        """
        user_states.set_state(callback_query.from_user.id, 'new_task_await_for_title')
        await client.send_message(
            callback_query.from_user.id,
            task_messages.input_prompt_title,
        )
        await callback_query.answer()

    @user_response_wrapper.subscribe("new_task_await_for_title")
    async def await_for_title_input(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: callback_change_title
        INVOKE: nothing (create page)
        Catch user input of title and update it
        """
        task = task_prototypes.get(message.from_user.id)
        if not task:
            task = TaskPrototype(
                state=TaskState.creating
            )
        task.title = message.text
        task_prototypes[message.from_user.id] = task
        text, reply_markup = await task_fsmlike_wrapper.handle_edit(
            task.state.name,
            task,
        )
        await message.reply(text, reply_markup=reply_markup)

    @app.on_callback_query(filters.regex("new_task_callback_description"))
    async def callback_change_description(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: main_keyboard_new_task
        INVOKE: await_for_description_input (new_task_await_for_description)
        callback on "description" input field
        """
        user_states.set_state(callback_query.from_user.id, 'new_task_await_for_description')
        await client.send_message(
            callback_query.from_user.id,
            task_messages.input_prompt_description,
        )
        await callback_query.answer()

    @user_response_wrapper.subscribe("new_task_await_for_description")
    async def await_for_description_input(
        client: Client,
        message: Message,
    ) -> None:
        """
        FROM: callback_change_description
        INVOKE: create page
        Catch user input of description and update it
        """
        task = task_prototypes.get(message.from_user.id)
        if not task:
            task = TaskPrototype(
                state=TaskState.creating
            )
        task.description = message.text
        task_prototypes[message.from_user.id] = task
        text, reply_markup = await task_fsmlike_wrapper.handle_edit(
            task.state.name,
            task,
        )
        await message.reply(text, reply_markup=reply_markup)

    @app.on_callback_query(filters.regex("new_task_callback_create"))
    async def callback_create(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: creation page (await_for_title_input/await_for_description_input)
        INVOKE: nothing
        "create task" button callback, creates new task from prototype
        """
        task = task_prototypes.get(callback_query.from_user.id)
        assert task is not None, "Shoud not be accessable if task not exsits"

        assert task_fsmlike_wrapper.can_move(task.state.name, TaskState.scheduled.name)
        task = TaskCreate(**task.model_dump())
        task.state = TaskState.scheduled
        task = await task_repository.create(
            callback_query.from_user.id,
            task
        )
        await client.send_message(
            callback_query.from_user.id,
            task_messages.task_created.format(
                **task.model_dump(),
                all_tasks=system_keyboard.all_tasks
            ),
        )
        del task_prototypes[callback_query.from_user.id]
        await callback_query.answer()

    @app.on_callback_query(filters.regex("new_task_callback_discard"))
    async def callback_discard(
        client: Client,
        callback_query: CallbackQuery,
    ) -> None:
        """
        FROM: creation page (await_for_title_input/await_for_description_input)
        INVOKE: nothing
        "discoard input" button callback, deletes task prototype data
        """
        task = task_prototypes.get(callback_query.from_user.id)
        assert task is not None, "Shoud not be accessable if task not exsits"
        del task_prototypes[callback_query.from_user.id]

        await client.send_message(
            callback_query.from_user.id,
            task_messages.task_discard.format(
                **task.model_dump(),
            ),
        )
        await callback_query.answer()
