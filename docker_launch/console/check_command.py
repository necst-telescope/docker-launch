"""Check and configure the SSH connection with remote machine.

Docker containers can be spawned on remote hosts when SSH connection with no password
(i.e. public key authentication) is enabled.
This restriction isn't that complicated as long as you run Docker-related scripts
locally.

The story gets troublesome when
- you run Docker on remote machine through SSH
- your authentication key is locked with passphrase
- you're connecting to known address, but different machine than the last time

The cause of the first two is that key authenticator `ssh-agent` cannot be caught from
remote, even if you're logged in with SSH. This disables public key authentication and
passphrase auto-locking.
(If you're using VNC, this won't be the case, you'll enjoy the benefits of `ssh-agent`)
As a measure for this difficulty, this script uses the default SSH keys only. They're
automatically searched by `paramiko`, defacto standard package for SSH handling in
Python.

The last situation arose from security reason. If the identity of remote host is
different from what's been last time, it may indicate someone impersonating the host.
Due to such reason, this script won't automatically ignore the connection issue, rather
provides some hints to resolve it.

"""

import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Type

import paramiko
from cleo import Command

from .. import utils
from ..ssh import check_connection, _get_ssh_client
from ..typing import PathLike


SSH_DIR = Path.home() / ".ssh"


class CheckCommand(Command):
    # DO NOT EDIT DOCSTRING IF YOU DON'T KNOW "CLEO"
    """
    Check and configure SSH connection with remote machines

    check
        {address : Machine to check, in user@host format}
        {--s|setup : Set-up the connection if it cannot be established}
        {--allow-locked : Use default locked SSH key, if exists}
    """

    def handle(self) -> int:
        logging.root.setLevel(logging.ERROR + 1)

        address = self.argument("address")

        if check_connection(address):
            self.info("OK")
            return 0

        if not self.option("setup"):
            self.line_error(
                "<error>Cannot connect.</> Use <comment>--setup</> flag to set-up."
            )
            return 1

        private_key_path = self._get_default_private_key_path(
            self.option("allow-locked")
        )
        if private_key_path is None:
            private_key_path = self._generate_default_key()
            self.info(f"Default RSA key '{private_key_path}' generated.")
        else:
            self.info(f"Default key '{private_key_path}' found.")

        public_key_path = private_key_path.with_suffix(".pub")
        ret = self._ssh_copy_id(public_key_path, address)
        if ret != 0:
            self.line_error(
                f"Failed to copy public key to remote host '{address}'.\n", "error"
            )
            return 5

        self.info(f"Successfully copied public key to remote host '{address}'.")
        if check_connection(address):
            self.info("Connection OK!")
            return 0

        if self._get_ssh_error(address) is paramiko.BadHostKeyException:
            ipaddr, _ = utils.parse_address(address)
            self.line_error(
                f"{address} looks different from what this machine knows it is."
            )
            self.line(
                f"If you know why this happens (e.g. machine at {address} is "
                f"replaced), run <comment>ssh keygen -R {ipaddr}</> and retry."
            )
            return 2
        self.line_error("Connection failed.", "error")
        if self._check_if_key_is_locked(private_key_path):
            self.info("This error may originates from locked key.\n")
            self.line(
                "If ssh-agent is running and well configured, the key will be "
                "unlocked automatically. Otherwise the connection will fail "
                "because Docker doesn't handle passphrase.\n"
                "In shells with no 'SSH_AUTH_SOCK' and 'SSH_AGENT_PID' "
                "variables set (e.g. shell over SSH), the agent cannot be "
                "accessed, so need configuration of the agent every time you "
                "log-in to the shell, which this command doesn't support."
            )
            return 3
        self.line("Unknown error.")
        return 4

    def _get_default_private_key_path(
        self, allow_locked: bool = False
    ) -> Optional[Path]:
        default_keys = self._get_existent_default_private_key_path()
        for key in default_keys:
            if allow_locked or (not self._check_if_key_is_locked(key)):
                return key

    def _get_existent_default_private_key_path(
        self, include_incomplete: bool = False
    ) -> List[Path]:
        def _exists(private_key_path: Path, pair_only: bool) -> bool:
            private = private_key_path
            public = private_key_path.parent / (private_key_path.name + ".pub")
            return (
                (private.exists() and public.exists())
                if pair_only
                else (private.exists() or public.exists())
            )

        # Check if default keys exist or not. Paramiko searches for them by default.
        # https://docs.paramiko.org/en/stable/api/client.html#paramiko.client.SSHClient.connect
        default_keys = ["id_rsa", "id_dsa", "id_ecdsa"]
        return [
            SSH_DIR / key
            for key in default_keys
            if _exists(SSH_DIR / key, not include_incomplete)
        ]

    def _check_if_key_is_locked(self, key_path: PathLike) -> bool:
        for key_handler in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey]:
            try:
                paramiko.RSAKey.from_private_key_file(key_path)
                return False
            except paramiko.PasswordRequiredException:
                return True
            except Exception:
                pass
        raise ValueError("Unknown key type.")

    def _ssh_copy_id(
        self, pubkey_path: PathLike, address: str, *, username: str = None
    ) -> int:
        ipaddr, username = utils.parse_address(address, username)
        command = ["ssh-copy-id", "-i", str(pubkey_path), f"{username}@{ipaddr}"]
        with subprocess.Popen(command) as p:
            try:
                return_code = p.wait()
            except KeyboardInterrupt:
                return_code = p.wait()
        return return_code

    def _generate_default_key(
        self, comment: str = "generated-by-docker-launch"
    ) -> Path:
        key_generation_config = {
            "id_rsa": (paramiko.RSAKey, (4096,)),
            "id_dsa": (paramiko.DSSKey, (4096,)),
            "id_ecdsa": (paramiko.ECDSAKey, ()),
        }

        existent = self._get_existent_default_private_key_path(include_incomplete=True)
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

    def _get_ssh_error(
        self, address: str, *, username: str = None, port: int = 22, timeout: float = 3
    ) -> Optional[Type[Exception]]:
        ipaddr, username = utils.parse_address(address, username)

        client = _get_ssh_client()
        try:
            client.connect(ipaddr, port=port, username=username, timeout=timeout)
            client.close()
            return
        except Exception as e:
            return e.__class__
