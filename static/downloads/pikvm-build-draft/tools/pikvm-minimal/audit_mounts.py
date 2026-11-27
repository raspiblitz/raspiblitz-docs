"""Run the native release content checks with only the mounted image and trusted tools visible."""

from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


def _bind(source, destination):
    path = Path(source).resolve(strict=True)
    # All controller mountpoints and the deployed script use simple path components.
    # Reject unit-property separators and specifiers before composing a bind definition.
    if not re.fullmatch(r'[/a-zA-Z0-9_.-]+', str(path)):
        raise ValueError(f'Unsupported audit source path: {path}')
    return f'{path}:{destination}:norbind'


def audit_mounts(check_script, root, boot, commit, version):
    """Inspect the controller's two cold mounts. A failed check raises CalledProcessError."""
    bindings = [
        _bind('/usr/bin', '/usr/bin'), _bind('/usr/lib', '/usr/lib'),
        _bind('/dev/null', '/dev/null'), _bind(check_script, '/audit.sh'),
        _bind(root, '/image-root'), _bind(boot, '/image-boot'),
    ]
    with tempfile.TemporaryDirectory(prefix='raspiblitz-audit-', dir='/run') as directory:
        jail = Path(directory)
        jail.chmod(0o755)
        for path in ('usr/bin', 'usr/lib', 'dev', 'image-root', 'image-boot',
                     'proc', 'sys', 'run', 'etc', 'root', 'var'):
            (jail / path).mkdir(parents=True)
        # The controller uses umask 077. The service user must traverse this
        # intermediate directory before exec gains its read-only capability.
        (jail / 'usr').chmod(0o755)
        (jail / 'dev/null').touch()
        (jail / 'audit.sh').touch()
        # PiKVM is Arch ARM64 with the dynamic loader under /usr/lib.
        (jail / 'lib').symlink_to('usr/lib')
        (jail / 'bin').symlink_to('usr/bin')
        properties = [
            f'RootDirectory={jail}', 'BindReadOnlyPaths=' + ' '.join(bindings),
            'ReadOnlyPaths=+/', 'NoExecPaths=+/image-root +/image-boot',
            'MountAPIVFS=no', 'BindLogSockets=no',
            'InaccessiblePaths=+/sys', 'TemporaryFileSystem=/proc:ro /run:ro',
            'User=65534', 'Group=65534', 'NoNewPrivileges=yes',
            'CapabilityBoundingSet=CAP_DAC_READ_SEARCH', 'AmbientCapabilities=CAP_DAC_READ_SEARCH',
            'PrivateNetwork=yes', 'PrivateIPC=yes', 'RestrictNamespaces=yes',
            'SystemCallFilter=~@mount @network-io @privileged @raw-io @debug @keyring '
            'open_by_handle_at name_to_handle_at io_uring_setup io_uring_enter io_uring_register',
            'SystemCallErrorNumber=EPERM', 'LimitCORE=0',
            'MemoryMax=256M', 'TasksMax=32', 'RuntimeMaxSec=10min',
        ]
        with subprocess.Popen([
            'systemd-run', '--wait', '--pipe', '--collect', '--quiet', '--service-type=exec',
            *(f'--property={prop}' for prop in properties),
            '--setenv=PATH=/usr/bin', '--setenv=HOME=/nonexistent',
            '--setenv=GIT_CONFIG_NOSYSTEM=1', '--setenv=GIT_CONFIG_GLOBAL=/dev/null',
            '--setenv=GIT_ALLOW_PROTOCOL=', '--setenv=GIT_TERMINAL_PROMPT=0',
            '/usr/bin/bash', '/audit.sh', '--isolated-content', commit, version,
        ], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as audit:
            # An explicit pipe keeps findings in the controller's journal when
            # both the controller and its isolated check are transient services.
            shutil.copyfileobj(audit.stdout, sys.stdout.buffer)
            sys.stdout.buffer.flush()
            code = audit.wait()
            if code:
                raise subprocess.CalledProcessError(code, audit.args)
