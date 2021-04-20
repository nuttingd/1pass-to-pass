from typing import Dict, Optional

class Password:
    name: str
    is_file: bool
    fields: Optional[Dict]
    data: Optional[bytes]

    def __init__(self, name, *, is_file=False, **fields):
        self.name = name
        self.is_file = is_file
        if self.is_file:
            data = fields.get("data")
            if data is None:
                raise "Must specify 'data' when 'is_file=True'"
            self.data = data
        else:
            self.fields = fields

    def get_body(self) -> bytes:
        if self.is_file:
            return self.data
        else:
            password = self.fields.get("password", "")
            the_rest = "\n".join([f"{k}: {v}" for k, v in self.fields.items() if k != "password"])
            return f"{password}\n{the_rest}\n".encode("utf-8")