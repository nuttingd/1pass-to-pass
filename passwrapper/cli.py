import subprocess
from passwrapper import models


__all__ = ["insert_item"]


def insert_item(password: models.Password) -> None:
    pass_item_proc = subprocess.Popen(
        ["pass", "insert", "-m", password.name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=False,
    )
    output = pass_item_proc.communicate(input=password.get_body())
    rc = pass_item_proc.wait()
    if rc != 0:
        print(f"Error creating '{password.name}'\nRC: {rc}\nOutput:\n{output}")
    print(f"Added: {password.name}")
