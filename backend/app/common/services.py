# app/db/base_repository.py
from beanie import Document
from pydantic import BaseModel
from typing import Type, TypeVar, Generic, Optional

T = TypeVar("T", bound=Document)


class BaseRepository(Generic[T]):
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
