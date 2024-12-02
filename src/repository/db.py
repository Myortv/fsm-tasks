import logging

from typing import Union, List
from abc import ABC


from asyncpg import (
    create_pool,
    Pool,
    Connection,
    Record,
)


class ConnectionInterface(ABC):
    """Interface to implement for database connections"""
    async def fetch(
        self,
        query: str,
        *args,
        **kwargs,
    ) -> List[dict]:
        """Fetch listed result of query"""
        pass

    async def fetchrow(
        self,
        query: str,
        *args,
        **kwargs,
    ) -> dict:
        """Fetch single result of query"""
        pass


class PostgresConnection(ConnectionInterface):
    """Asyncpg Postgres Connection"""

    def __init__(self, connection: Connection):
        self._wrapped_connection = connection

    async def fetch(
        self,
        query: str,
        *args,
        **kwargs,
    ) -> list:
        return await self._wrapped_connection.fetch(
            query,
            *args,
            **kwargs
        )

    async def fetchrow(
        self,
        query: str,
        *args,
        **kwargs,
    ) -> Union[dict, None]:
        result: Record = await self._wrapped_connection.fetchrow(
            query,
            *args,
            **kwargs
        )
        return dict(result) if result else None


class ManagerInterface(ABC):
    """Interface to implemet for managers.
    DatabaseManagers is an entity that manages connections
    and provide same api
    """
    async def get_connection(self) -> ConnectionInterface:
        pass

    async def close_connection(self, connection: ConnectionInterface) -> None:
        pass


class PostgresManager(ManagerInterface):
    """DatabaseManger for Postgres"""

    def __init__(self):
        self.pool: Pool = None

    async def get_connection(self) -> PostgresConnection:
        return PostgresConnection(
            await self.pool.acquire()
        )

    async def close_connection(self, connection: PostgresConnection) -> None:
        await self.pool.release(connection._wrapped_connection)


class DatabaseConnection:
    """Context manager to handle database managers
    and open/close connections"""

    def __init__(self, engine):
        self._engine = engine
        self._connection = None

    async def __aenter__(self):
        self._connection = await self._engine.get_connection()
        return self._connection

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self._engine.close_connection(
            self._connection
        )


postgres_manager = PostgresManager()


async def init_asyncpg(
    db_name: str,
    db_host: str,
    db_user: str,
    db_password: str,
):
    """Init function to start postgres manager
    (connect to database and create pool)
    """
    postgres_manager.pool = await create_pool(
        database=db_name,
        host=db_host,
        user=db_user,
        password=db_password,
    )
    logging.info(
        f'PostgresManager create postgres pool on:{postgres_manager.pool}',
    )
    return postgres_manager


async def stop_asyncpg():
    """Stop function to stop postgres manager
    (close pool and disconect from database)
    """
    if postgres_manager.pool:
        await postgres_manager.pool.close()
        logging.info(
            f'PostgresManager closed postgres pool on:{postgres_manager.pool}',
        )
    else:
        logging.info(
            'PostgresManager was never started',
        )
    return postgres_manager
