from typing import List

from op.models.base import OpBaseModel
from op.models.item import ItemRef


__all__ = ["Vault"]


class Vault(OpBaseModel):
    uuid: str
    name: str

    def list_items(self, **kwargs) -> List[ItemRef]:
        return op.list_items(vault=self.name, **kwargs)
