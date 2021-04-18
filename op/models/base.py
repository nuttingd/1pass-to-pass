from typing import Any, Dict, Iterable, List, TYPE_CHECKING, Type, TypeVar

T = TypeVar("T", bound="OpBaseModel")


# TODO: use pydantic :)
class OpBaseModel(object):
    _context: Dict[str, Any]

    def __init__(self, *, context: Dict[str, Any], **attrs) -> None:
        self._context = context
        for k, v in attrs.items():
            setattr(self, k, v)

    @classmethod
    def create(cls: Type[T], *, item: Any, **context) -> T:
        return cls(context=context, **item)

    @classmethod
    def create_list(cls: Type[T], *, items: Iterable[Any], **context) -> List[T]:
        return [cls.create(item=item, **context) for item in items]
