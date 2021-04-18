from typing import Any, Dict, Iterable, List, TYPE_CHECKING, Type, TypeVar

T = TypeVar("T", bound="PassBaseModel")


# TODO: use pydantic :)
class PassBaseModel(object):
    def __init__(self, *, **attrs) -> None:
        for k, v in attrs.items():
            setattr(self, k, v)

    @classmethod
    def create(cls: Type[T], *, item: Any) -> T:
        return cls(**item)

    @classmethod
    def create_list(cls: Type[T], *, items: Iterable[Any]) -> List[T]:
        return [cls.create(item=item) for item in items]
