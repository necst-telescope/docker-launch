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
from pathlib import Path

import paramiko
from cleo import Command

from .. import ssh, utils
from ..connection import check_connection


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

        private_key_path = ssh.get_default_key_path(self.option("allow-locked"))
        if private_key_path is None:
            private_key_path = ssh.generate_default_key()
            self.info(f"Default key '{private_key_path}' generated.")
        else:
            self.info(f"Default key '{private_key_path}' found.")

        public_key_path = private_key_path.with_suffix(".pub")
        ret = ssh.ssh_copy_id(public_key_path, address)
        if ret != 0:
            self.line_error(
                f"Failed to copy public key to remote host '{address}'.\n", "error"
            )
            return 5

        self.info(f"Successfully copied public key to remote host '{address}'.")
        if check_connection(address):
            self.info("Connection OK!")
            return 0

        if ssh.get_ssh_error(address) is paramiko.BadHostKeyException:
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
        if ssh.is_locked(private_key_path):
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
