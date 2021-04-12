import json
import subprocess
from typing import List, Any, Optional

from op.models.item import ItemRef, Item, Document
from op.models.vault import Vault

"""
TODO: Need to think about how the vault plays into the context of the model.
  Should the vault be a requirement, keeping all calls scoped to a single vault?
  Otherwise, there are places in the API (get_item) where allowing a vault to be
  specified could break things
"""


def run_command(command, text=False):
    result = subprocess.run(
        ["op", *command],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=text,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Error running: {result.args}\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}\n"
        )
    return result


def run_command_json(command: List[str]) -> Any:
    result = run_command(command, text=True)
    json_obj = json.loads(result.stdout)
    return json_obj


def run_command_bytes(command: List[str]) -> Any:
    result = run_command(command, text=False)
    return result.stdout


def list_vaults() -> List[Vault]:
    list_vaults_json = run_command_json(["list", "vaults"])
    return Vault.create_list(items=list_vaults_json)


def list_items(
    *,
    vault: Optional[str],
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> List[ItemRef]:
    command = ["list", "items"]
    if vault:
        command.extend(["--vault", vault])
    if categories:
        command.extend(["--categories", ",".join(categories)])
    if tags:
        command.extend(["--tags", ",".join(tags)])

    list_items_json = run_command_json(command)
    return ItemRef.create_list(items=list_items_json, vault=vault)


def get_item(*, uuid_or_name: str, vault: Optional[str]) -> Item:
    command = ["get", "item", uuid_or_name]

    # this should only be used when the call is made on the op object directly,
    # outside any of the helper delegates
    if vault:
        command.extend(["--vault", vault])

    get_item_json = run_command_json(command)
    return Item.create(item=get_item_json, vault=vault)


def get_document(*, uuid_or_name: str, vault: Optional[str]) -> Document:
    command = ["get", "item", uuid_or_name]

    # this should only be used when the call is made on the op object directly,
    # outside any of the helper delegates
    if vault:
        command.extend(["--vault", vault])

    get_item_json = run_command_json(command)
    document = Document.create(item=get_item_json, vault=vault)
    if not document.is_document:
        raise ValueError(f"Item {document.uuid} is not a document")
    return document


def get_document_bytes(*, uuid_or_name: str, vault: Optional[str]) -> bytes:
    command = ["get", "document", uuid_or_name]
    # this should only be used when the call is made on the op object directly,
    # outside any of the helper delegates
    if vault:
        command.extend(["--vault", vault])

    return run_command_bytes(command)
