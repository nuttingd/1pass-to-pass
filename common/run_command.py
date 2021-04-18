import json
import subprocess
from typing import Any, List, Optional


def run_command(command: List[str], text=False) -> subprocess.CompletedProcess:
    result = subprocess.run(
        command,
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
