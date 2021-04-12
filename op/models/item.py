import enum
import re
from functools import reduce
from pathlib import Path
from typing import Dict

import op
from op.models.base import OpBaseModel

__all__ = ["ItemRef", "Item"]


class TemplateType(str, enum.Enum):
    LOGIN = "001"
    CREDIT_CARD = ("002",)
    SECURE_NOTE = ("003",)
    IDENTITY = ("004",)
    PASSWORD = ("005",)
    DOCUMENT = ("006",)
    SOFTWARE_LICENSE = ("100",)
    BANK_ACCOUNT = ("101",)
    DRIVER_LICENSE = ("103",)
    REWARDS_PROGRAM = ("107",)
    SOCIAL_SECURITY_NUMBER = ("108",)


def _fields_dict_reduce_fn(fields_dict, field_item):
    # prefer "designation" over "name"
    field_name = (
        field_item.get("designation") or field_item.get("name") or "unknown"
    )  # TODO (collision inevitable for unknown)
    field_value = field_item.get("value")
    fields_dict[field_name] = field_value
    return fields_dict


class ItemRef(OpBaseModel):
    uuid: str
    templateUuid: TemplateType

    def get_item(self) -> "Item":
        return op.get_item(uuid_or_name=self.uuid, **self._context)

    def get_document(self) -> "Document":
        return op.get_document(uuid_or_name=self.uuid, **self._context)

    @property
    def is_document(self) -> bool:
        return self.templateUuid == TemplateType.DOCUMENT

    @property
    def name(self) -> str:
        overview = getattr(self, "overview", dict())
        return str(overview.get("title") or self.uuid)

    @property
    def safe_name(self) -> str:
        return re.sub("[^\w\-_\. ]+", "_", self.name)

    @property
    def type(self) -> str:
        return TemplateType(self.templateUuid).name


class Item(ItemRef):
    name: str

    def get_fields(self) -> Dict:
        details = getattr(self, "details", None)
        if details:
            fields = [
                f for f in (details.get("fields") or list()) if f.get("value")
            ]  # ignore fields without any value
            if fields:
                return reduce(_fields_dict_reduce_fn, fields, dict())
        return dict()


class Document(Item):
    def get_document_bytes(self) -> bytes:
        return op.get_document_bytes(uuid_or_name=self.uuid, **self._context)

    def export_to_file(self, path: Path) -> None:
        with open(path, "wb") as export_file:
            export_file.write(self.get_document_bytes())
