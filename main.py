import base64
import json
import os
import subprocess
from typing import Dict

import op
import passwrapper

def main():
    op_vaults = op.list_vaults()

    for op_vault in op_vaults:
        op_vault.name = op_vault.name
        op_items = op.list_items(vault=op_vault.uuid)
        print(f"Loading {len(op_items)} items to vault: {op_vault.name}")

        for op_item in op_items:
            op_full_item = op_item.get_item()

            # TODO: this is messy, halp
            #  - use strategy based on op_item.type to deserialize into correct model
            #  - currently CreditCard, BankAccount, and a few others don't have much meaningful info
            document_fields = add_document_to_pass(op_full_item)
            add_item_to_pass(op_full_item, op_vault.name, document_fields)


def add_item_to_pass(
    op_full_item: op.Item, op_vault_name: str, document_fields: Dict[str, str]
):
    op_export_base64json = str(
        base64.b64encode(json.dumps(op_full_item.__dict__).encode("utf-8")), "utf-8"
    )
    pass_fields = {
        **op_full_item.get_fields(),
        **document_fields,
        # 1password meta data
        "op_vault_name": op_vault_name,
        "op_item_type": op_full_item.type.name,
        "op_export_base64json": op_export_base64json,
    }

    item_name = (
        pass_fields.get("username", None) or pass_fields.get("email", None) or "default"
    )
    folder_name = get_folder_name(op_full_item)
    pass_item_name = f"{op_full_item.type.item_root}/{folder_name}/{item_name}"
    password = passwrapper.Password(name=pass_item_name, **pass_fields)
    passwrapper.insert_item(password)


def add_document_to_pass(op_full_item: op.Item) -> Dict[str, str]:
    if op_full_item.is_document:
        folder_name = get_folder_name(op_full_item)
        pass_doc_name = (
            f"{op_full_item.type.item_root}/{folder_name}/{op_full_item.safe_name}"
        )
        pass_doc_bytes = op_full_item.get_document_bytes()
        password = passwrapper.Password(name=pass_doc_name, is_file=True, data=pass_doc_bytes)
        passwrapper.insert_item(password)
        return {"document": password.name}
    return dict()


def get_folder_name(op_full_item: op.Item):
    folder_name = (
        os.path.splitext(op_full_item.safe_name)[0]
        if op_full_item.is_document
        else op_full_item.safe_name
    )
    return folder_name


if __name__ == "__main__":
    main()
