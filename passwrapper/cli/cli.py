import json
import subprocess
from typing import Any, List, Optional


from common.run_command import run_command

__all__ = ["insert_item"]


def insert_item(password: password.Password) -> None:
    pass_item_proc = subprocess.Popen(
        [["pass", "insert", "-m", password.name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=password.use_text,
    )
    output = pass_item_proc.communicate(input=password.body)
    rc = pass_item_proc.wait()
    if rc != 0:
        print(f"Error creating '{pass_item_name}'\nRC: {rc}\nOutput:\n{output}")
    print(f"Added: {password.name}")
