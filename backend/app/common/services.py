# app/db/base_repository.py
from beanie import Document
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sa_update
from typing import Type, TypeVar, Generic, Optional, List

T = TypeVar("T", bound=Document)


class BaseRepositorySQLMongo(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def save(self, document: T):
        await document.save()
        return document

    async def find_one(self, query):
        return await self.model.find_one(query)

    async def find_all(
        self, fields: Optional[type[BaseModel]] = None, query=None
    ) -> list[T]:
        if query:
            return await self.model.find_many(query).to_list()
        if fields:
            return await self.model.find_all().project(fields).to_list()
        return await self.model.find_all().to_list()

    async def update(self, document: T, update_data: dict):
        for key, value in update_data.items():
            setattr(document, key, value)

        await document.save()
        return document



class BaseRepositorySQL(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def save(self, session: AsyncSession, instance: T) -> T:
        """Insert or update a model instance."""
        session.add(instance)
        await session.flush()
        await session.commit()
        return instance

    async def find_one(self, session: AsyncSession, query) -> Optional[T]:
        """Find a single record using a SQLAlchemy expression."""
        stmt = select(self.model).where(query)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(
        self,
        session: AsyncSession,
        query=None,
    ) -> List[T]:
        """Find all records matching a query."""
        if query is not None:
            stmt = select(self.model).where(query)
        else:
            stmt = select(self.model)

        result = await session.execute(stmt)
        return result.scalars().all()

    async def update(
        self,
        session: AsyncSession,
        instance: T,
        update_data: dict,
    ) -> T:
        """Update fields on an instance."""
        for key, value in update_data.items():
            setattr(instance, key, value)

        session.add(instance)
        await session.flush()
        await session.commit()
        return instance

    async def update_where(
        self,
        session: AsyncSession,
        query,
        update_data: dict,
    ) -> None:
        """
        Optional:
        Perform a bulk update without loading objects into memory.
        """
        stmt = (
            sa_update(self.model)
            .where(query)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(stmt)
