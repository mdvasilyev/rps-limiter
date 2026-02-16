from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedDTO(GenericModel, Generic[T]):
    limit: int
    offset: int
    total: int
    items: list[T]
