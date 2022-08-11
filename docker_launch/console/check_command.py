import logging
import subprocess
from pathlib import Path
from typing import Optional, Type

import paramiko
from cleo import Command

from ..ssh import check_connection, _get_ssh_client, _parse_address
from ..typing import PathLike


SSH_DIR = Path.home() / ".ssh"


class CheckCommand(Command):
    """
    Check and configure SSH connection with remote machines

    check
        {address : Machine to check, in user@host format}
        {--s|setup : Set-up the connection if it cannot be established}
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

        private_key_path = self._get_default_private_key_path()
        if private_key_path is None:
            # TODO: Check when only one of (id_rsa, id_rsa.pub) exists, raise error?
            private_key_path = self._generate_default_key()
            self.info(f"Default RSA key '{private_key_path}' generated.")
        else:
            self.info(f"Default key '{private_key_path}' found.")

        public_key_path = private_key_path.with_suffix(".pub")
        ret = self._ssh_copy_id(public_key_path, address)
        if ret == 0:
            self.info(f"Successfully copied public key to remote host '{address}'.")
            if check_connection(address):
                self.info("Connection OK!")
                return 0
            else:
                if self._get_ssh_error(address) is paramiko.BadHostKeyException:
                    ipaddr, _ = _parse_address(address)
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

        self.line_error(
            f"Failed to copy public key to remote host '{address}'.\n", "error"
        )
        return 5

    def _get_default_private_key_path(self) -> Optional[Path]:
        # Check if default keys exist or not. Paramiko searches for them by default.
        # https://docs.paramiko.org/en/stable/api/client.html#paramiko.client.SSHClient.connect
        default_keys = ["id_rsa", "id_dsa", "id_ecdsa"]
        for key in default_keys:
            if (SSH_DIR / key).exists() and (SSH_DIR / (key + ".pub")).exists():
                return SSH_DIR / key

    def _check_if_key_is_locked(self, key_path: PathLike) -> bool:
        try:
            paramiko.RSAKey.from_private_key_file(key_path)
            return False
        except paramiko.PasswordRequiredException:
            return True

    def _ssh_copy_id(
        self, pubkey_path: PathLike, address: str, *, username: str = None
    ) -> int:
        ipaddr, username = _parse_address(address, username)
        command = ["ssh-copy-id", "-i", str(pubkey_path), f"{username}@{ipaddr}"]
        with subprocess.Popen(command) as p:
            try:
                return_code = p.wait()
            except KeyboardInterrupt:
                return_code = p.wait()
        return return_code

    def _generate_default_key(self, comment: str = "id") -> Path:
        new_key = paramiko.RSAKey.generate(4096)
        public_key = f"{new_key.get_name()} {new_key.get_base64()} {comment}"

        private_key_path = SSH_DIR / "id_rsa"
        public_key_path = SSH_DIR / "id_rsa.pub"

        new_key.write_private_key_file(private_key_path)
        public_key_path.write_text(public_key)
        public_key_path.chmod(0o644)

        return private_key_path

    def _get_ssh_error(
        self, address: str, *, username: str = None, port: int = 22, timeout: float = 3
    ) -> Optional[Type[Exception]]:
        ipaddr, username = _parse_address(address, username)

        client = _get_ssh_client()
        try:
            client.connect(ipaddr, port=port, username=username, timeout=timeout)
            client.close()
            return
        except Exception as e:
            return e.__class__
