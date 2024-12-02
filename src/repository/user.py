from repository.db import DatabaseConnection, postgres_manager

from schemas.user import UserInDB, UserUpdate, UserPrototype


async def get_user(
    telegram_id: int
) -> UserInDB | None:
    async with DatabaseConnection(postgres_manager) as conn:
        result = await conn.fetchrow(
            """
            select * from user_profile where telegram_id = $1
            """,
            telegram_id,
        )
    if result:
        return UserInDB(**result)


async def insert_if_not_exsists(
    telegram_id: int,
    user: UserPrototype,
) -> UserInDB | None:
    async with DatabaseConnection(postgres_manager) as conn:
        result = await conn.fetchrow(
            """
            insert into user_profile (telegram_id, username, login)
            values ($1, $2, $3)
            on conflict do nothing returning *
            """,
            telegram_id,
            user.username,
            user.login,
        )
    if result:
        return UserInDB(**result)


async def update(
    telegram_id: int,
    user: UserUpdate,
) -> UserInDB | None:
    async with DatabaseConnection(postgres_manager) as conn:
        result = await conn.fetchrow(
            """
            update user_profile set username = $1, login = $2
            where telegram_id = $3
            returning *
            """,
            user.username,
            user.login,
            telegram_id,
        )
    if result:
        return UserInDB(**result)
