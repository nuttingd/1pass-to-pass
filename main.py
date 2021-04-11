import base64
import json
import re
import subprocess
from functools import reduce

# noinspection PyPackageRequirements
import onepassword

templateTypeMap = {
    "001": "Logins",
    "002": "Credit Cards",
    "003": "Notes",
    "004": "Identities",
    "005": "Passwords",
    "006": "Documents",
    "100": "Software Licenses",
    "101": "Bank Accounts",
    "103": "Driver Licenses",
    "107": "Rewards Programs",
    "108": "Social Security Numbers",
}


def get_item_type(item):
    template_uuid = item.get("templateUuid")
    return templateTypeMap.get(template_uuid) or "Unknown"


def fields_dict_reduce_fn(fields_dict, field_item):
    # prefer "designation" over "name"
    field_name = (
        field_item.get("designation") or field_item.get("name") or "unknown"
    )  # TODO (collision inevitable for unknown)
    field_value = field_item.get("value")
    fields_dict[field_name] = field_value
    return fields_dict


def create_fields_dict(full_item):
    details = full_item.get("details")
    if details:
        fields = [
            f for f in (details.get("fields") or list()) if f.get("value")
        ]  # ignore fields without any value
        if fields:
            return reduce(fields_dict_reduce_fn, fields, dict())
    return dict()


def create_pass_item_body(**fields):
    password = fields.pop("password", "")
    the_rest = "\n".join([f"{k}: {v}" for k, v in fields.items()])
    return f"{password}\n{the_rest}\n"


def main():
    op = onepassword.OnePassword()
    op_vaults = json.loads(op.list_vaults())

    for op_vault in op_vaults:
        vault_uuid = op_vault["uuid"]
        vault_name = op_vault["name"]
        op_items = op.list_items(vault=vault_uuid)

        for op_item in op_items:
            op_item_uuid = op_item["uuid"]
            op_item_name = str(op_item["overview"].get("title") or op_item_uuid)
            op_item_type = get_item_type(op_item)
            op_full_item = op.get_item(op_item_uuid)
            if op_item_type == "Documents":
                # TODO: this doesn't work! This 1password lib assumes a document is a JSON/YAML
                # I'm not crazy about this; where's my uuid based lookup?
                # op_document = op.get_document(docname=op_item_name, vault=vault_uuid)
                pass

            op_export_base64json = str(
                base64.b64encode(json.dumps(op_full_item).encode("utf-8")), "utf-8"
            )
            op_fields = create_fields_dict(op_full_item)

            pass_fields = {
                **op_fields,
                "vault_name": vault_name,
                "item_type": op_item_type,
                "op_export_base64json": op_export_base64json,
            }
            safe_item_name = re.sub("[^\w\-_\. ]+", "_", op_item_name)
            pass_item_name = f"{vault_name}/{op_item_type}/{safe_item_name}"
            pass_item_body = create_pass_item_body(**pass_fields)

            p = subprocess.Popen(
                ["pass", "insert", "-m", pass_item_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output = p.communicate(input=pass_item_body)
            rc = p.wait()
            if rc != 0:
                print(f"Error creating '{pass_item_name}'\nRC: {rc}\nOutput:\n{output}")


if __name__ == "__main__":
    main()
