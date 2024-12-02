from typing import Any, Tuple, List


from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from fsm.base import FSM
from schemas.tasks import TaskState, TaskInDB, TaskPrototype
from text.task import task_keyboard, task_messages


class TaskFSM(FSM):
    """FSM for tasks"""
    default_move_rules = {
        TaskState.not_exsists.name: [
            TaskState.creating.name,
        ],
        TaskState.creating.name: [
            TaskState.scheduled.name,
        ],
        TaskState.scheduled.name: [
            TaskState.suspended.name,
            TaskState.accepted.name,
            TaskState.canceled.name,
        ],
        TaskState.suspended.name: [
            TaskState.scheduled.name,
            TaskState.accepted.name,
            TaskState.in_work.name,
            TaskState.awaits_user_review.name,
            TaskState.finished.name,
            TaskState.canceled.name,
        ],
        TaskState.accepted.name: [
            TaskState.suspended.name,
            TaskState.in_work.name,
            TaskState.canceled.name,
        ],
        TaskState.in_work.name: [
            TaskState.suspended.name,
            TaskState.awaits_user_review.name,
            TaskState.finished.name,
            TaskState.canceled.name,
        ],
        TaskState.awaits_user_review.name: [
            TaskState.suspended.name,
            TaskState.finished.name,
            TaskState.canceled.name,
        ],
        TaskState.finished.name: [
        ],
        TaskState.canceled.name: [
        ],
    }

    async def handle_move_state(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """general api func to handle move_state representation"""
        return await self.handle_representation("move_state", state, *args, task=task, **kwargs)

    async def default_move_state(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """default (all states) handler for move_state representation"""
        if self.move_rules[state]:
            return (
                task_messages.get(
                    f"{state}__move_state",
                ),
                InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(
                            task_keyboard.get(f"inline__{state_to}"),
                            f"task_set_state_callback:{task.id}:{state_to}"
                        )]
                        for state_to in self.move_rules[state]
                    ]
                )
            )
        else:
            return (
                task_messages.get(
                    f"{state}__move_state",
                ),
                None
            )

    async def handle_edit(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """general api func to handle edit representation"""
        return await self.handle_representation("edit", state, *args, task=task, **kwargs)

    async def not_exsists_edit(
        self,
        state: str,
        task: TaskPrototype,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """handler for edit representation in not_exists state"""
        return (
            task_messages.get(f"{state}__edit").format(**task.model_dump()),
            InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        task_keyboard.inline__title,
                        "new_task_callback_title"
                    )],
                    [InlineKeyboardButton(
                        task_keyboard.inline__description,
                        "new_task_callback_description"
                    )],
                ]
            )
        )

    async def creating_edit(
        self,
        state: str,
        task: TaskPrototype,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """handler for edit representation in creating state"""
        keyboard = [
            [InlineKeyboardButton(
                task_keyboard.inline__title,
                "new_task_callback_title"
            )],
            [InlineKeyboardButton(
                task_keyboard.inline__description,
                "new_task_callback_description"
            )],
            [InlineKeyboardButton(
                task_keyboard.inline__discard,
                "new_task_callback_discard"
            )],
        ]
        if task.title and task.description:
            keyboard.insert(
                2,
                [InlineKeyboardButton(
                    task_keyboard.inline__create,
                    "new_task_callback_create"
                )],
            )
        return (
            task_messages.get(f"{state}__edit").format(**task.model_dump()),
            InlineKeyboardMarkup(keyboard)
        )

    async def default_edit(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """default (all states) handler for edit representation"""
        fields = ['description', 'title']
        return (
            task_messages.get(
                f"{state}__edit",
            ),
            InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        task_keyboard.get(f'inline__{field}'),
                        f"task_edit_callback:{task.id}:{field}"
                    )]
                    for field in fields
                ]
            )
        )

    async def handle_general(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """general api func to handle general representation"""
        return await self.handle_representation(
            "general",
            state,
            *args,
            task=task,
            **kwargs
        )

    async def default_general(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """default (all states) handler for general representation"""
        return (
            task_messages.get(f"{state}__general").format(
                title=task.title,
                description=task.description,
                state=task.state.name,
            ),
            InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        task_keyboard.inline__edit,
                        f"task_menu_edit_callback:{task.id}",
                    )],
                    [InlineKeyboardButton(
                        task_keyboard.inline__move_state,
                        f"task_menu_move_state_callback:{task.id}",
                    )],
                ]
            )
        )

    async def handle_list(
        self,
        tasks: List[TaskInDB],
        offset: int,
        limit: int,
        max: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """general api func to handle list representation"""
        task_buttons = [
            [InlineKeyboardButton(
                task.title,
                f"task_callback:{task.id}"
            )]
            for task in tasks
        ]
        nav_buttons = list()
        if offset > 0:
            new_offset = offset-limit if offset-limit > 0 else 0
            nav_buttons.append(
                InlineKeyboardButton(
                    task_keyboard.inline__left,
                    f"task_list_callback:{new_offset}:{limit}"
                ),
            )
        if max > offset+limit:
            nav_buttons.append(
                InlineKeyboardButton(
                    task_keyboard.inline__right,
                    f"task_list_callback:{offset+limit}:{limit}"
                ),
            )
        return (
            task_messages.task_list,
            InlineKeyboardMarkup(
                [
                    *task_buttons,
                    nav_buttons,
                ]
            )
        )


task_fsmlike_wrapper = TaskFSM()
