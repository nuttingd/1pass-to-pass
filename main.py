import base64
import json
import subprocess
from typing import Dict

import op


def create_pass_item_body(**fields):
    password = fields.pop("password", "")
    the_rest = "\n".join([f"{k}: {v}" for k, v in fields.items()])
    return f"{password}\n{the_rest}\n"


def main():
    op_vaults = op.list_vaults()

    for op_vault in op_vaults:
        vault_uuid = op_vault.uuid
        vault_name = op_vault.name
        op_items = op.list_items(vault=vault_uuid)
        print(f"Loading {len(op_items)} items to vault: {vault_name}")

        for op_item in op_items:
            op_full_item = (
                op_item.get_document() if op_item.is_document else op_item.get_item()
            )

            # this is messy, halp
            document_fields = add_document_to_pass(op_full_item, vault_name)
            add_item_to_pass(op_full_item, vault_name, document_fields)


def add_item_to_pass(op_full_item, vault_name, document_fields: Dict[str, str]):
    op_export_base64json = str(
        base64.b64encode(json.dumps(op_full_item.__dict__).encode("utf-8")), "utf-8"
    )
    pass_fields = {
        **op_full_item.get_fields(),
        "vault_name": vault_name,
        "item_type": op_full_item.type,
        **document_fields,
        "op_export_base64json": op_export_base64json,
    }
    item_name = (
        pass_fields.get("username", None) or pass_fields.get("email", None) or "item"
    )
    pass_item_name = (
        f"{vault_name}/{op_full_item.type}/{op_full_item.safe_name}/{item_name}"
    )
    pass_item_body = create_pass_item_body(**pass_fields)
    pass_item_proc = subprocess.Popen(
        ["pass", "insert", "-m", pass_item_name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    output = pass_item_proc.communicate(input=pass_item_body)
    rc = pass_item_proc.wait()
    if rc != 0:
        print(f"Error creating '{pass_item_name}'\nRC: {rc}\nOutput:\n{output}")
    print(f"Added: {pass_item_name}")


def add_document_to_pass(op_full_item, vault_name) -> Dict[str, str]:
    if op_full_item.is_document:
        pass_doc_name = f"{vault_name}/{op_full_item.type}/{op_full_item.safe_name}/{op_full_item.safe_name}"
        pass_doc_bytes = op_full_item.get_document_bytes()
        pass_doc_proc = subprocess.Popen(
            ["pass", "insert", "-m", pass_doc_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=False,
        )
        output = pass_doc_proc.communicate(input=pass_doc_bytes)
        rc = pass_doc_proc.wait()
        if rc != 0:
            print(f"Error creating '{pass_doc_name}'\nRC: {rc}\nOutput:\n{output}")
        print(f"Added document: {pass_doc_name}")
        return {"document": pass_doc_name}
    return dict()


if __name__ == "__main__":
    main()
