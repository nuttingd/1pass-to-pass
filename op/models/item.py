import enum
import re
import string
from functools import reduce
from pathlib import Path
from typing import Dict

import op
from op.models.base import OpBaseModel

__all__ = ["ItemRef", "Item"]


class ItemType(str, enum.Enum):
    Login = "001"
    CreditCard = "002"
    SecureNote = "003"
    Identity = "004"
    Password = "005"
    Document = "006"
    SoftwareLicense = "100"
    BankAccount = "101"
    DriverLicense = "103"
    RewardsProgram = "107"
    SocialSecurityNumber = "108"

    @property
    def item_root(self):
        return ItemRoot.root_from_type(self)


class ItemRoot(str, enum.Enum):
    Logins = "logins",
    Documents = "docs",
    Identity = "identity",
    Software = "software",
    Financial = "financial"

    @staticmethod
    def root_from_type(item_type: ItemType):
        if item_type in [ItemType.Login, ItemType.Password]:
            return ItemRoot.Logins
        if item_type in [ItemType.CreditCard, ItemType.BankAccount, ItemType.RewardsProgram]:
            return ItemRoot.Financial
        if item_type in [ItemType.SecureNote, ItemType.Document]:
            return ItemRoot.Documents
        if item_type in [ItemType.SoftwareLicense]:
            return ItemRoot.Software
        if item_type in [ItemType.Identity, ItemType.DriverLicense, ItemType.SocialSecurityNumber]:
            return ItemRoot.Identity


def _fields_dict_reduce_fn(fields_dict, field_item):
    # prefer "designation" over "name"
    field_name = (
        field_item.get("designation") or field_item.get("name") or "unknown"
    )  # TODO (collision inevitable for unknown)
    field_value = field_item.get("value")
    fields_dict[field_name] = field_value
    return fields_dict


def get_safe_name(name):
    escape_re = '!"#$%\'()[]*,/:;<=>?\\^_`{|}~'
    escaped_name = re.sub(f"[{escape_re}]", "_", name)
    safe_name = re.sub(r"\s+", "-", escaped_name)
    return safe_name


class ItemRef(OpBaseModel):
    uuid: str
    templateUuid: str

    def get_item(self) -> "Item":
        return op.get_item(uuid_or_name=self.uuid, **self._context)

    def get_document(self) -> "Document":
        return op.get_document(uuid_or_name=self.uuid, **self._context)

    @property
    def is_document(self) -> bool:
        return self.type == ItemType.Document

    @property
    def name(self) -> str:
        overview = getattr(self, "overview", dict())
        return str(overview.get("title") or self.uuid)

    @property
    def safe_name(self) -> str:
        safe_name = get_safe_name(self.name)
        return safe_name

    @property
    def type(self) -> ItemType:
        return ItemType(self.templateUuid)


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
