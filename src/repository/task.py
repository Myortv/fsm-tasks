from typing import Tuple, List


from repository.db import DatabaseConnection, postgres_manager


from schemas.tasks import TaskInDB, TaskCreate, TaskUpdate

from fsm.tasks import task_fsmlike_wrapper


async def create(user_id: int, task: TaskCreate) -> TaskInDB | None:
    async with DatabaseConnection(postgres_manager) as conn:
        result = await conn.fetchrow(
            """
            insert into task (
                user_id,
                title,
                description,
                state
            )
            values (
                $1, $2, $3, $4
            )
            returning *
            """,
            user_id,
            task.title,
            task.description,
            task.state.value,
        )
    if result:
        return TaskInDB(**result)


async def update(task_id: int, task: TaskUpdate) -> TaskInDB | None:
    async with DatabaseConnection(postgres_manager) as conn:
        result = await conn.fetchrow(
            """
            update task set
                title = $1,
                description = $2,
                state = $3
            where id = $4
            returning *
            """,
            task.title,
            task.description,
            task.state.value,
            task_id,
        )
    if result:
        return TaskInDB(**result)


async def move_state(task_id: int, state: str) -> TaskInDB | None:
    """Use this to ensure status changes is valid"""
    async with DatabaseConnection(postgres_manager) as conn:
        async with conn._wrapped_connection.transaction():
            result = await conn.fetchrow(
                "select * from task where id = $1 for update",
                task_id,
            )
            if not result:
                return
            task = TaskInDB(**result)
            if not task_fsmlike_wrapper.can_move(
                task.state.name,
                state,
            ):
                return
            await conn.fetchrow(
                'update task set state = $1 where id = $2',
                state,
                task_id,
            )
    if result:
        return TaskInDB(**result)


async def get(
    task_id: int
) -> TaskInDB | None:
    async with DatabaseConnection(postgres_manager) as conn:
        result = await conn.fetchrow(
            """
            select * from task
            where id = $1
            """,
            task_id,
        )
    if result:
        return TaskInDB(**result)


async def get_page(
    user_id: int,
    offset: int,
    limit: int,
) -> Tuple[int, List[TaskInDB]]:
    async with DatabaseConnection(postgres_manager) as conn:
        result = await conn.fetch(
            """
            select
                *,
                count (*) over() as total_tasks
            from task
            where user_id = $1
            order by created_at desc
            limit $2 offset $3
            """,
            user_id,
            limit,
            offset
        )
    if result:
        return (
            result[0]['total_tasks'],
            [TaskInDB(**task) for task in result]
        )
