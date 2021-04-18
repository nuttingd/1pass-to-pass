import json
import subprocess
from typing import Any, List, Optional

from op.models import item, vault
from common.run_command import run_command_json, run_command_bytes

__all__ = ["list_vaults", "list_items", "get_item", "get_document_bytes"]


def list_vaults() -> List[vault.Vault]:
    list_vaults_json = run_command_json(["list", "vaults"])
    return vault.Vault.create_list(items=list_vaults_json)


def list_items(
    *,
    vault: Optional[str],
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> List[item.ItemRef]:
    command = ["op", "list", "items"]
    if vault:
        command.extend(["--vault", vault])
    if categories:
        command.extend(["--categories", ",".join(categories)])
    if tags:
        command.extend(["--tags", ",".join(tags)])

    list_items_json = run_command_json(command)
    return item.ItemRef.create_list(items=list_items_json, vault=vault)


def get_item(*, uuid_or_name: str, vault: Optional[str]) -> item.Item:
    command = ["op", "get", "item", uuid_or_name]

    # this should only be used when the call is made on the op object directly,
    # outside any of the helper delegates
    if vault:
        command.extend(["--vault", vault])

    get_item_json = run_command_json(command)
    return item.Item.create(item=get_item_json, vault=vault)


def get_document_bytes(*, uuid_or_name: str, vault: Optional[str]) -> bytes:
    command = ["op", "get", "document", uuid_or_name]
    # this should only be used when the call is made on the op object directly,
    # outside any of the helper delegates
    if vault:
        command.extend(["--vault", vault])

    return run_command_bytes(command)
