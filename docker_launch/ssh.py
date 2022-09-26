import subprocess
from pathlib import Path
from typing import List, Optional, Type

import paramiko

from . import utils
from .connection import _get_ssh_client
from .typing import PathLike

SSH_DIR = Path.home() / ".ssh"


def _get_existent_default_private_key_path(
    include_incomplete: bool = False,
) -> List[Path]:
    def _exists(private_key_path: Path, pair_only: bool) -> bool:
        public_key_path = private_key_path.parent / (private_key_path.name + ".pub")
        return (
            (private_key_path.exists() and public_key_path.exists())
            if pair_only
            else (private_key_path.exists() or public_key_path.exists())
        )

    # Check if default keys exist or not. Paramiko searches for them by default.
    # https://docs.paramiko.org/en/stable/api/client.html#paramiko.client.SSHClient.connect
    default_keys = ["id_rsa", "id_dsa", "id_ecdsa"]
    return [
        SSH_DIR / key
        for key in default_keys
        if _exists(SSH_DIR / key, not include_incomplete)
    ]


def get_default_key_path(allow_locked: bool = False) -> Optional[Path]:
    default_keys = _get_existent_default_private_key_path()
    for key in default_keys:
        if allow_locked or (not is_locked(key)):
            return key


def is_locked(key_path: Path) -> bool:
    for key_handler in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey]:
        try:
            key_handler.from_private_key_file(key_path)
            return False
        except paramiko.PasswordRequiredException:
            return True
        except Exception:
            pass
    raise ValueError(f"Key type for '{key_path}' unknown.")


def ssh_copy_id(pubkey_path: PathLike, address: str, *, username: str = None) -> int:
    ipaddr, username = utils.parse_address(address, username)
    command = ["ssh-copy-id", "-i", str(pubkey_path), f"{username}@{ipaddr}"]
    with subprocess.Popen(command) as p:
        try:
            return_code = p.wait()
        except KeyboardInterrupt:
            return_code = p.wait()
    return return_code


def generate_default_key(comment: str = "generated-by-docker-launch") -> Path:
    key_generation_config = {
        "id_rsa": (paramiko.RSAKey, (4096,)),
        "id_dsa": (paramiko.DSSKey, (3072,)),
        "id_ecdsa": (paramiko.ECDSAKey, ()),
    }

    existent = _get_existent_default_private_key_path(include_incomplete=True)
    existent_types = [path.name for path in existent]
    new_key_type = set(key_generation_config.keys()) - set(existent_types)
    if len(new_key_type) < 1:
        raise FileExistsError(
            f"Default keys {list(key_generation_config.keys())} already exist. "
            "Consider using/unlocking them or remove unused one."
        )
    new_key_name = new_key_type.pop()

    key_generator, args = key_generation_config[new_key_name]
    new_key = key_generator.generate(*args)
    public_key = f"{new_key.get_name()} {new_key.get_base64()} {comment}"

    private_key_path = SSH_DIR / new_key_name
    public_key_path = SSH_DIR / f"{new_key_name}.pub"

    new_key.write_private_key_file(private_key_path)
    public_key_path.write_text(public_key)
    public_key_path.chmod(0o644)

    return private_key_path


def get_ssh_error(
    address: str, *, username: str = None, port: int = 22, timeout: float = 3.0
) -> Optional[Type[Exception]]:
    ipaddr, username = utils.parse_address(address, username)
    client = _get_ssh_client()
    try:
        client.connect(ipaddr, port=port, username=username, timeout=timeout)
        client.close()
        return
    except Exception as e:
        return e.__class__
